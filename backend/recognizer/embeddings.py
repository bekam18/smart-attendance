import cv2
import numpy as np

class EmbeddingGenerator:
    def __init__(self, method='facenet'):
        """
        Initialize embedding generator
        method: 'facenet', 'arcface', or 'simple'
        """
        self.method = method
        self.model = None
        self._init_model()
    
    def _init_model(self):
        """Initialize the embedding model"""
        try:
            if self.method == 'arcface':
                # Try to load ArcFace ONNX model
                import insightface
                from insightface.model_zoo import get_model
                self.model = get_model('arcface_r100_v1')
                self.model.prepare(ctx_id=-1)  # CPU
                print("✅ ArcFace embedding model initialized")
                
            elif self.method == 'facenet':
                # Try to load FaceNet with TensorFlow
                try:
                    from tensorflow.keras.models import load_model
                    # Note: You would need to provide the FaceNet model file
                    # For now, we'll use a simple feature extraction
                    print("⚠️  FaceNet model not found, using simple features")
                    self.method = 'simple'
                except:
                    print("⚠️  TensorFlow not available, using simple features")
                    self.method = 'simple'
                    
        except Exception as e:
            print(f"⚠️  Failed to initialize {self.method} model: {e}")
            print("Using simple feature extraction")
            self.method = 'simple'
    
    def generate_embedding(self, face_img):
        """
        Generate embedding vector from face image
        Returns: numpy array of embedding
        """
        try:
            if self.method == 'arcface' and self.model:
                # ArcFace expects BGR image
                embedding = self.model.get_embedding(face_img)
                return embedding
                
            elif self.method == 'facenet' and self.model:
                # FaceNet preprocessing
                face_pixels = face_img.astype('float32')
                mean, std = face_pixels.mean(), face_pixels.std()
                face_pixels = (face_pixels - mean) / std
                face_pixels = np.expand_dims(face_pixels, axis=0)
                embedding = self.model.predict(face_pixels)[0]
                return embedding
                
            else:
                # Simple feature extraction (fallback)
                return self._simple_features(face_img)
                
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return self._simple_features(face_img)
    
    def _simple_features(self, face_img):
        """
        Simple feature extraction using histogram and pixel statistics
        This is a fallback method when advanced models are not available
        """
        # Resize to standard size
        face = cv2.resize(face_img, (160, 160))
        
        # Convert to grayscale
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        
        # Compute histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten()
        hist = hist / (hist.sum() + 1e-7)  # Normalize
        
        # Compute LBP-like features (simplified)
        features = []
        
        # Divide face into regions and compute statistics
        h, w = gray.shape
        regions = [
            gray[0:h//2, 0:w//2],      # Top-left
            gray[0:h//2, w//2:w],      # Top-right
            gray[h//2:h, 0:w//2],      # Bottom-left
            gray[h//2:h, w//2:w],      # Bottom-right
        ]
        
        for region in regions:
            features.extend([
                region.mean(),
                region.std(),
                np.median(region),
            ])
        
        # Combine histogram and regional features
        embedding = np.concatenate([hist[::8], features])  # Downsample histogram
        
        return embedding

# Global embedding generator
embedding_generator = EmbeddingGenerator(method='simple')
