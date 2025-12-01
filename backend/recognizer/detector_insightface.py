"""
InsightFace-based Face Detector with Alignment
Replaces OpenCV Haar Cascade for better detection accuracy
"""

import cv2
import numpy as np
from insightface.app import FaceAnalysis
import logging

logger = logging.getLogger(__name__)


class InsightFaceDetector:
    """
    Face detector using InsightFace RetinaFace
    Provides better detection + 5-point landmark alignment
    """
    
    def __init__(self, det_size=(640, 640)):
        """
        Initialize InsightFace detector
        
        Args:
            det_size: Detection size (width, height)
        """
        self.det_size = det_size
        self.detector = None
        self._init_detector()
    
    def _init_detector(self):
        """Initialize InsightFace FaceAnalysis"""
        try:
            logger.info("Initializing InsightFace detector...")
            
            # Initialize FaceAnalysis with CPU provider
            self.detector = FaceAnalysis(
                providers=['CPUExecutionProvider'],
                allowed_modules=['detection']  # Only use detection, not recognition
            )
            
            # Prepare detector with specified size
            self.detector.prepare(
                ctx_id=-1,  # CPU
                det_size=self.det_size
            )
            
            logger.info(f"✅ InsightFace detector initialized (det_size={self.det_size})")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize InsightFace detector: {e}")
            raise
    
    def detect_faces(self, img):
        """
        Detect faces in image using InsightFace
        
        Args:
            img: BGR image (numpy array)
        
        Returns:
            list of tuples: [(x, y, w, h), ...] in OpenCV format
        """
        if self.detector is None:
            logger.warning("Detector not initialized")
            return []
        
        try:
            # InsightFace expects RGB
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = self.detector.get(rgb_img)
            
            if len(faces) == 0:
                return []
            
            # Convert bboxes to OpenCV format (x, y, w, h)
            bboxes = []
            for face in faces:
                bbox = face.bbox.astype(int)
                x1, y1, x2, y2 = bbox
                x, y, w, h = x1, y1, x2 - x1, y2 - y1
                bboxes.append((x, y, w, h))
            
            return bboxes
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def get_faces_with_landmarks(self, img):
        """
        Detect faces and return full face data including landmarks
        
        Args:
            img: BGR image (numpy array)
        
        Returns:
            list of face objects with bbox, landmarks, etc.
        """
        if self.detector is None:
            logger.warning("Detector not initialized")
            return []
        
        try:
            # InsightFace expects RGB
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces with full data
            faces = self.detector.get(rgb_img)
            
            return faces
            
        except Exception as e:
            logger.error(f"Error detecting faces with landmarks: {e}")
            return []
    
    def align_face(self, img, landmarks, output_size=(160, 160)):
        """
        Align face using 5-point landmarks
        
        Args:
            img: BGR image
            landmarks: 5-point landmarks from InsightFace (shape: 5x2)
            output_size: Output image size (width, height)
        
        Returns:
            Aligned face image (160x160 by default)
        """
        try:
            # Standard reference points for alignment (based on FaceNet)
            # These are normalized coordinates for a 112x112 image
            reference_points = np.array([
                [38.2946, 51.6963],  # Left eye
                [73.5318, 51.5014],  # Right eye
                [56.0252, 71.7366],  # Nose
                [41.5493, 92.3655],  # Left mouth
                [70.7299, 92.2041]   # Right mouth
            ], dtype=np.float32)
            
            # Scale reference points to output size
            scale_x = output_size[0] / 112.0
            scale_y = output_size[1] / 112.0
            reference_points[:, 0] *= scale_x
            reference_points[:, 1] *= scale_y
            
            # Estimate similarity transform
            tform = self._estimate_transform(landmarks, reference_points)
            
            # Apply transformation
            aligned_face = cv2.warpAffine(
                img,
                tform,
                output_size,
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=0
            )
            
            return aligned_face
            
        except Exception as e:
            logger.error(f"Error aligning face: {e}")
            # Fallback: just resize
            return cv2.resize(img, output_size, interpolation=cv2.INTER_LINEAR)
    
    def _estimate_transform(self, src_points, dst_points):
        """
        Estimate similarity transformation matrix
        
        Args:
            src_points: Source landmarks (Nx2)
            dst_points: Destination landmarks (Nx2)
        
        Returns:
            2x3 transformation matrix
        """
        # Use only first 3 points (eyes + nose) for more stable alignment
        src = src_points[:3].astype(np.float32)
        dst = dst_points[:3].astype(np.float32)
        
        # Estimate affine transform
        tform = cv2.estimateAffinePartial2D(src, dst)[0]
        
        return tform
    
    def extract_face(self, img, bbox, landmarks=None, output_size=(160, 160)):
        """
        Extract and align face from image
        
        Args:
            img: BGR image
            bbox: Bounding box (x, y, w, h)
            landmarks: Optional 5-point landmarks for alignment
            output_size: Output size (width, height)
        
        Returns:
            Aligned and cropped face image
        """
        try:
            # If landmarks provided, use alignment
            if landmarks is not None and len(landmarks) == 5:
                return self.align_face(img, landmarks, output_size)
            
            # Otherwise, use bbox with padding
            x, y, w, h = bbox
            
            # Convert to int and ensure non-negative
            x = int(max(0, x))
            y = int(max(0, y))
            w = int(max(1, w))
            h = int(max(1, h))
            
            # Add padding (30% of face size)
            pad = int(max(w, h) * 0.3)
            
            # Compute square crop centered on bbox
            cx = x + w // 2
            cy = y + h // 2
            half = max(w, h) // 2 + pad
            
            x1 = max(0, cx - half)
            y1 = max(0, cy - half)
            x2 = min(img.shape[1], cx + half)
            y2 = min(img.shape[0], cy + half)
            
            # Safety check
            if x2 <= x1 or y2 <= y1:
                logger.warning("Invalid crop coordinates, using bbox directly")
                x1, y1 = x, y
                x2, y2 = x + w, y + h
            
            # Crop face
            face = img[y1:y2, x1:x2]
            
            # Check if crop is valid
            if face is None or face.size == 0:
                logger.warning("Empty face crop, returning black image")
                return np.zeros((output_size[1], output_size[0], 3), dtype=np.uint8)
            
            # Resize to output size
            face = cv2.resize(face, output_size, interpolation=cv2.INTER_LINEAR)
            
            return face
            
        except Exception as e:
            logger.error(f"Error extracting face: {e}")
            return np.zeros((output_size[1], output_size[0], 3), dtype=np.uint8)


# Global detector instance
face_detector = InsightFaceDetector(det_size=(640, 640))
