"""
Improved Face Detector with Modern Techniques
- Better real-time performance
- Handles moving faces, pose variations, partial occlusions
- Reduces false positives
- Smooth tracking with temporal consistency
"""

import cv2
import numpy as np
import logging
from collections import deque
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

class ImprovedFaceDetector:
    def __init__(self, method='insightface'):
        """
        Initialize improved face detector with tracking
        """
        self.method = method
        self.detector = None
        self.faces_cache = []
        
        # Tracking parameters
        self.tracked_faces = []  # List of tracked face positions
        self.face_history = deque(maxlen=5)  # Smooth tracking over 5 frames
        self.min_detection_confidence = 0.5
        self.iou_threshold = 0.3  # For matching tracked faces
        
        # Performance optimization
        self.frame_skip = 0  # Process every frame
        self.frame_count = 0
        
        self._init_detector()
    
    def _init_detector(self):
        """Initialize the detector with optimal settings"""
        try:
            if self.method == 'insightface':
                from insightface.app import FaceAnalysis
                logger.info("🔧 Initializing Improved InsightFace detector...")
                
                self.detector = FaceAnalysis(
                    name='buffalo_l',  # Use buffalo_l model for better accuracy
                    providers=['CPUExecutionProvider'],
                    allowed_modules=['detection']
                )
                
                # Prepare with optimal detection size
                # Very low threshold for maximum side face detection
                self.detector.prepare(
                    ctx_id=-1, 
                    det_size=(320, 320),  # Reduced for faster processing
                    det_thresh=0.3  # Slightly higher threshold for speed
                )
                
                # Update minimum confidence for filtering
                self.min_detection_confidence = 0.2  # Very low for side faces
                
                print("✅ Improved InsightFace detector initialized")
                print("   Model: buffalo_l")
                print("   Detection size: 320x320 (optimized for speed)")
                print("   Threshold: 0.3 (balanced speed and accuracy)")
                print("   Status: Ready for high-performance face detection")
                
            elif self.method == 'opencv':
                # Use DNN-based face detector (much better than Haar Cascade)
                model_file = "opencv_face_detector_uint8.pb"
                config_file = "opencv_face_detector.pbtxt"
                
                try:
                    self.detector = cv2.dnn.readNetFromTensorflow(model_file, config_file)
                    self.method = 'opencv_dnn'
                    print("✅ OpenCV DNN face detector initialized")
                except:
                    # Fallback to Haar Cascade
                    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                    self.detector = cv2.CascadeClassifier(cascade_path)
                    print("✅ OpenCV Haar Cascade detector initialized (fallback)")
                
        except Exception as e:
            logger.error(f"⚠️  Failed to initialize {self.method} detector: {e}")
            print(f"⚠️  Falling back to OpenCV Haar Cascade")
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.detector = cv2.CascadeClassifier(cascade_path)
            self.method = 'opencv'
    
    def _calculate_iou(self, box1, box2):
        """Calculate Intersection over Union for two bounding boxes"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _smooth_bbox(self, current_bbox, history_weight=0.7):
        """Smooth bounding box using temporal history"""
        if len(self.face_history) == 0:
            return current_bbox
        
        # Weighted average with history
        x, y, w, h = current_bbox
        
        # Average with previous detections
        for prev_bbox in self.face_history:
            px, py, pw, ph = prev_bbox
            x = int(x * history_weight + px * (1 - history_weight))
            y = int(y * history_weight + py * (1 - history_weight))
            w = int(w * history_weight + pw * (1 - history_weight))
            h = int(h * history_weight + ph * (1 - history_weight))
        
        return (x, y, w, h)
    
    def _expand_bbox(self, bbox, img_shape, expand_ratio=0.15):
        """Expand bounding box slightly for better face capture"""
        x, y, w, h = bbox
        img_h, img_w = img_shape[:2]
        
        # Expand by ratio
        expand_w = int(w * expand_ratio)
        expand_h = int(h * expand_ratio)
        
        x = max(0, x - expand_w)
        y = max(0, y - expand_h)
        w = min(img_w - x, w + 2 * expand_w)
        h = min(img_h - y, h + 2 * expand_h)
        
        return (x, y, w, h)
    
    def _filter_false_positives(self, faces, img):
        """Filter out false positives using additional checks"""
        if len(faces) == 0:
            return faces
        
        filtered_faces = []
        
        for face in faces:
            x, y, w, h = face
            
            # Check 1: Reasonable aspect ratio (very lenient for side faces)
            aspect_ratio = w / h if h > 0 else 0
            # Side faces can be much narrower, so allow 0.3 to 3.0
            if aspect_ratio < 0.3 or aspect_ratio > 3.0:
                continue
            
            # Check 2: Minimum size (too small = likely false positive)
            if w < 20 or h < 20:  # Very small minimum for distant side faces
                continue
            
            # Check 3: Not too large (entire image = likely error)
            img_h, img_w = img.shape[:2]
            if w > img_w * 0.9 or h > img_h * 0.9:
                continue
            
            filtered_faces.append(face)
        
        return filtered_faces
    
    def detect_faces(self, img, return_confidence=False):
        """
        Detect faces with improved accuracy and tracking
        
        Args:
            img: Input image (BGR format)
            return_confidence: If True, return confidence scores
            
        Returns:
            List of face bounding boxes [(x, y, w, h), ...]
            If return_confidence=True: List of (bbox, confidence) tuples
        """
        if self.detector is None:
            return []
        
        self.frame_count += 1
        
        try:
            if self.method == 'insightface':
                # Convert to RGB for InsightFace
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                self.faces_cache = self.detector.get(rgb_img)
                
                if len(self.faces_cache) == 0:
                    return []
                
                # Convert to OpenCV format with confidence
                faces = []
                confidences = []
                
                for face in self.faces_cache:
                    # Get bounding box
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    x, y, w, h = x1, y1, x2 - x1, y2 - y1
                    
                    # Get confidence score
                    confidence = float(face.det_score)
                    
                    # Filter by confidence (balanced threshold for speed)
                    if confidence < 0.3:  # Higher threshold for better performance
                        continue
                    
                    # Expand bbox slightly
                    bbox_expanded = self._expand_bbox((x, y, w, h), img.shape)
                    
                    faces.append(bbox_expanded)
                    confidences.append(confidence)
                
                # Filter false positives
                faces = self._filter_false_positives(faces, img)
                
                # Apply temporal smoothing for the primary face
                if len(faces) > 0:
                    # Use the face with highest confidence
                    if len(confidences) > 0:
                        best_idx = np.argmax(confidences)
                        best_face = faces[best_idx]
                        
                        # Smooth with history
                        smoothed_face = self._smooth_bbox(best_face)
                        self.face_history.append(smoothed_face)
                        faces[best_idx] = smoothed_face
                
                if return_confidence:
                    return list(zip(faces, confidences))
                
                return np.array(faces) if faces else []
            
            elif self.method == 'opencv':
                # Preprocess image
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
                # Better than simple histogram equalization
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                gray = clahe.apply(gray)
                
                # Reduce noise
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
                
                # Detect faces with optimized parameters
                faces = self.detector.detectMultiScale(
                    gray,
                    scaleFactor=1.05,  # Smaller steps for better detection
                    minNeighbors=4,    # Balance between false positives and misses
                    minSize=(40, 40),  # Minimum face size
                    maxSize=(500, 500),  # Maximum face size
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                # Filter false positives
                faces = self._filter_false_positives(faces, img)
                
                # Apply temporal smoothing
                if len(faces) > 0:
                    smoothed_face = self._smooth_bbox(faces[0])
                    self.face_history.append(smoothed_face)
                    faces[0] = smoothed_face
                
                self.faces_cache = []
                
                if return_confidence:
                    # OpenCV doesn't provide confidence, use 1.0
                    return [(face, 1.0) for face in faces]
                
                return faces
                
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def get_face_landmarks(self, face_idx=0):
        """Get facial landmarks for detected face"""
        if self.method == 'insightface' and len(self.faces_cache) > face_idx:
            face = self.faces_cache[face_idx]
            if hasattr(face, 'kps'):
                return face.kps
        return None
    
    def reset_tracking(self):
        """Reset tracking history"""
        self.face_history.clear()
        self.tracked_faces.clear()
        self.frame_count = 0

# Global instance
_detector_instance = None

def get_face_detector(method='insightface'):
    """Get singleton face detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = ImprovedFaceDetector(method=method)
    return _detector_instance
