import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FaceDetector:
    def __init__(self, method='insightface'):
        """
        Initialize face detector
        method: 'opencv', 'mtcnn', or 'insightface' (default)
        """
        self.method = method
        self.detector = None
        self.faces_cache = []  # Cache for faces with landmarks
        self._init_detector()
    
    def _init_detector(self):
        """Initialize the selected detector"""
        try:
            if self.method == 'insightface':
                from insightface.app import FaceAnalysis
                logger.info("Initializing InsightFace detector...")
                self.detector = FaceAnalysis(
                    providers=['CPUExecutionProvider'],
                    allowed_modules=['detection']  # Only detection, not recognition
                )
                self.detector.prepare(ctx_id=-1, det_size=(640, 640))
                print("✅ InsightFace detector initialized (det_size=640x640)")
                
            elif self.method == 'opencv':
                # Use OpenCV Haar Cascade (fallback)
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.detector = cv2.CascadeClassifier(cascade_path)
                print("✅ OpenCV face detector initialized")
                
            elif self.method == 'mtcnn':
                from mtcnn import MTCNN
                self.detector = MTCNN()
                print("✅ MTCNN face detector initialized")
                
        except Exception as e:
            logger.error(f"⚠️  Failed to initialize {self.method} detector: {e}")
            print(f"⚠️  Failed to initialize {self.method} detector: {e}")
            print("Falling back to OpenCV detector")
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.detector = cv2.CascadeClassifier(cascade_path)
            self.method = 'opencv'
    
    def detect_faces(self, img):
        """
        Detect faces in image
        Returns: list of face bounding boxes [(x, y, w, h), ...]
        """
        if self.detector is None:
            return []
        
        try:
            if self.method == 'insightface':
                # InsightFace expects RGB
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Detect faces and cache full data
                self.faces_cache = self.detector.get(rgb_img)
                
                if len(self.faces_cache) == 0:
                    return []
                
                # Convert bboxes to OpenCV format (x, y, w, h)
                faces = []
                for face in self.faces_cache:
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    x, y, w, h = x1, y1, x2 - x1, y2 - y1
                    faces.append((x, y, w, h))
                
                return np.array(faces) if faces else []
            
            elif self.method == 'opencv':
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # Apply histogram equalization for better detection in varying lighting
                gray = cv2.equalizeHist(gray)
                # More lenient parameters for better detection
                faces = self.detector.detectMultiScale(
                    gray, 
                    scaleFactor=1.05,  # More sensitive (was 1.1)
                    minNeighbors=3,    # Less strict (was 5)
                    minSize=(20, 20),  # Smaller minimum (was 30x30)
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                self.faces_cache = []  # No landmarks for OpenCV
                return faces
                
            elif self.method == 'mtcnn':
                rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                detections = self.detector.detect_faces(rgb)
                faces = []
                for det in detections:
                    x, y, w, h = det['box']
                    faces.append((x, y, w, h))
                self.faces_cache = []  # No landmarks cached for MTCNN
                return np.array(faces)
                
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            print(f"Error detecting faces: {e}")
            return []
    
    def extract_face(self, img, bbox, face_index=0, margin=20):
        """
        Extract and align face from image
        bbox: (x, y, w, h)
        face_index: Index of face in faces_cache (for InsightFace alignment)
        Returns: face image (aligned and cropped to 160x160)
        """
        try:
            # If using InsightFace and we have cached face data with landmarks
            if self.method == 'insightface' and len(self.faces_cache) > face_index:
                face_data = self.faces_cache[face_index]
                
                # Check if landmarks are available
                if hasattr(face_data, 'kps') and face_data.kps is not None:
                    landmarks = face_data.kps.astype(np.float32)
                    
                    # Align face using landmarks
                    aligned_face = self._align_face_with_landmarks(img, landmarks)
                    
                    if aligned_face is not None and aligned_face.size > 0:
                        return aligned_face
            
            # Fallback: Use bbox-based extraction (works for all methods)
            return self._extract_face_bbox(img, bbox, margin)
            
        except Exception as e:
            logger.error(f"Error extracting face: {e}")
            return self._extract_face_bbox(img, bbox, margin)
    
    def _align_face_with_landmarks(self, img, landmarks, output_size=(160, 160)):
        """
        Align face using 5-point landmarks from InsightFace
        
        Args:
            img: BGR image
            landmarks: 5-point landmarks (shape: 5x2)
            output_size: Output size (width, height)
        
        Returns:
            Aligned face image
        """
        try:
            # Standard reference points for FaceNet (160x160)
            reference_points = np.array([
                [54.706573, 73.85186],   # Left eye
                [105.045425, 73.573425], # Right eye
                [80.036255, 102.48086],  # Nose
                [59.356144, 131.95071],  # Left mouth
                [101.04271, 131.72014]   # Right mouth
            ], dtype=np.float32)
            
            # Estimate similarity transform
            tform = cv2.estimateAffinePartial2D(landmarks, reference_points)[0]
            
            if tform is None:
                return None
            
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
            logger.error(f"Error in landmark alignment: {e}")
            return None
    
    def _extract_face_bbox(self, img, bbox, margin=20):
        """
        Extract face using bounding box (fallback method)
        
        Args:
            img: BGR image
            bbox: (x, y, w, h)
            margin: Padding around face
        
        Returns:
            Cropped and resized face image (160x160)
        """
        x, y, w, h = bbox

        # Convert bbox to int and ensure non-negative
        x = int(max(0, x))
        y = int(max(0, y))
        w = int(max(1, w))
        h = int(max(1, h))

        # Use a padding factor relative to face size (30% for better framing)
        pad = int(max(w, h) * 0.3)

        # Compute square crop centered on detected bbox
        cx = x + w // 2
        cy = y + h // 2
        half = max(w, h) // 2 + pad

        x1 = max(0, cx - half)
        y1 = max(0, cy - half)
        x2 = min(img.shape[1], cx + half)
        y2 = min(img.shape[0], cy + half)

        # Debug safety: ensure coordinates make sense
        if x2 <= x1 or y2 <= y1:
            # Fallback to conservative bbox with margin
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(img.shape[1], x + w + margin)
            y2 = min(img.shape[0], y + h + margin)

        face = img[y1:y2, x1:x2]

        # If face extraction failed, return empty array
        if face is None or face.size == 0:
            return np.zeros((160, 160, 3), dtype=np.uint8)

        # Resize to standard size (160x160 for FaceNet)
        face = cv2.resize(face, (160, 160), interpolation=cv2.INTER_LINEAR)

        return face

# Global detector instance
# Use 'insightface' for better accuracy (requires C++ build tools on Windows)
# Use 'opencv' for simpler installation (works out of the box)
face_detector = FaceDetector(method='opencv')  # Change to 'insightface' when installed
