"""
FaceNet Embedding Generator with MTCNN
Uses facenet-pytorch for production-quality embeddings
"""

import torch
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class FaceNetEmbeddingGenerator:
    """Generate 512-dimensional embeddings using FaceNet"""
    
    def __init__(self):
        self.device = None
        self.facenet = None
        self.transform = None
        self._initialized = False
        self._init_error = None
        
    def _lazy_init(self):
        """Lazy initialization - only load models when first needed"""
        if self._initialized:
            return True
        
        if self._init_error:
            logger.error(f"Previous initialization failed: {self._init_error}")
            return False
        
        try:
            logger.info("Initializing FaceNet embedding generator...")
            
            # Import here to avoid loading on module import
            from facenet_pytorch import InceptionResnetV1
            from torchvision import transforms
            
            # Setup device
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"Using device: {self.device}")
            
            # Load FaceNet model
            self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
            logger.info("✅ FaceNet model loaded (vggface2)")
            
            # Setup transform
            self.transform = transforms.Compose([
                transforms.Resize((160, 160)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
            ])
            
            self._initialized = True
            logger.info("✅ FaceNet embedding generator initialized")
            return True
            
        except ImportError as e:
            self._init_error = f"Missing dependencies: {e}"
            logger.error(f"❌ {self._init_error}")
            logger.error("Install with: pip install torch torchvision facenet-pytorch")
            return False
            
        except Exception as e:
            self._init_error = f"Initialization failed: {e}"
            logger.error(f"❌ {self._init_error}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_embedding(self, face_img):
        """
        Generate 512-dimensional embedding from face image
        
        Args:
            face_img: numpy array (BGR) or PIL Image
            
        Returns:
            numpy array of shape (512,) or None if failed
        """
        # Lazy initialization
        if not self._lazy_init():
            logger.error("FaceNet not initialized, cannot generate embedding")
            raise RuntimeError(f"FaceNet initialization failed: {self._init_error}")
        
        try:
            # Convert numpy array to PIL Image if needed
            if isinstance(face_img, np.ndarray):
                # OpenCV uses BGR, PIL uses RGB
                if len(face_img.shape) == 3 and face_img.shape[2] == 3:
                    import cv2
                    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
                face_img = Image.fromarray(face_img)
            
            # Transform image (already resized by detector)
            face_tensor = self.transform(face_img).unsqueeze(0).to(self.device)

            # Generate embedding
            with torch.no_grad():
                embedding = self.facenet(face_tensor).cpu().numpy().flatten()

            # L2-normalize the embedding to unit length. This is standard for
            # FaceNet embeddings and improves cosine-similarity based comparisons
            # and makes downstream classifiers more stable if trained with
            # normalized vectors.
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            # Verify dimension
            if embedding.shape[0] != 512:
                logger.error(f"Invalid embedding dimension: {embedding.shape[0]}, expected 512")
                raise ValueError(f"Invalid embedding dimension: {embedding.shape[0]}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def is_available(self):
        """Check if FaceNet is available"""
        return self._lazy_init()


# Global instance
try:
    embedding_generator = FaceNetEmbeddingGenerator()
    logger.info("FaceNet embedding generator created")
except Exception as e:
    logger.error(f"Failed to create FaceNet embedding generator: {e}")
    embedding_generator = None
