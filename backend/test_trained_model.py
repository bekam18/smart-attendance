"""
Test Trained Model Script
Verifies the trained model works correctly and shows predictions
"""

import pickle
import numpy as np
from pathlib import Path
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelTester:
    """Test trained face recognition model"""
    
    def __init__(self, model_path='models/Classifier'):
        self.model_path = Path(model_path)
        
        # Initialize device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Load model artifacts
        self.load_model()
        
        # Initialize MTCNN and FaceNet
        self.mtcnn = MTCNN(
            image_size=160,
            margin=20,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            device=self.device,
            keep_all=False
        )
        
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        logger.info("Loaded FaceNet model")
        
    def load_model(self):
        """Load trained model artifacts"""
        logger.info(f"Loading model from: {self.model_path}")
        
        # Load classifier
        classifier_path = self.model_path / 'face_classifier.pkl'
        with open(classifier_path, 'rb') as f:
            self.classifier = pickle.load(f)
        logger.info(f"✓ Loaded classifier: {type(self.classifier).__name__}")
        
        # Load label encoder
        encoder_path = self.model_path / 'label_encoder.pkl'
        with open(encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)
        logger.info(f"✓ Loaded label encoder: {len(self.label_encoder.classes_)} classes")
        
        # Load metadata
        metadata_path = self.model_path / 'model_metadata.pkl'
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        logger.info(f"✓ Loaded metadata")
        
        # Display model info
        logger.info("\n" + "="*60)
        logger.info("MODEL INFORMATION")
        logger.info("="*60)
        logger.info(f"Embedding dimension: {self.metadata['embedding_dim']}")
        logger.info(f"Number of classes: {self.metadata['num_classes']}")
        logger.info(f"Confidence threshold: {self.metadata['threshold']:.4f}")
        logger.info(f"Model type: {self.metadata['model_type']}")
        logger.info(f"Students: {', '.join(self.metadata['classes'])}")
        logger.info("="*60 + "\n")
        
    def predict_image(self, image_path):
        """Predict student ID from image"""
        logger.info(f"Processing: {image_path}")
        
        # Load image
        img = Image.open(image_path).convert('RGB')
        
        # Detect face
        face_tensor = self.mtcnn(img)
        if face_tensor is None:
            logger.warning("✗ No face detected")
            return None, 0.0
        
        # Extract embedding
        with torch.no_grad():
            face_tensor = face_tensor.unsqueeze(0).to(self.device)
            embedding = self.facenet(face_tensor).cpu().numpy().flatten()
        
        # Verify dimension
        if embedding.shape[0] != self.metadata['embedding_dim']:
            logger.error(f"✗ Invalid embedding dimension: {embedding.shape[0]}")
            return None, 0.0
        
        # Predict
        embedding = embedding.reshape(1, -1)
        prediction = self.classifier.predict(embedding)[0]
        probabilities = self.classifier.predict_proba(embedding)[0]
        confidence = probabilities.max()
        
        # Decode label
        student_id = self.label_encoder.inverse_transform([prediction])[0]
        
        # Check threshold
        threshold = self.metadata['threshold']
        if confidence < threshold:
            logger.info(f"✓ Prediction: Unknown (confidence {confidence:.4f} < threshold {threshold:.4f})")
            return "Unknown", confidence
        else:
            logger.info(f"✓ Prediction: {student_id} (confidence: {confidence:.4f})")
            return student_id, confidence
    
    def test_dataset(self, dataset_path='dataset'):
        """Test model on entire dataset"""
        dataset_path = Path(dataset_path)
        
        if not dataset_path.exists():
            logger.error(f"Dataset not found: {dataset_path}")
            return
        
        logger.info(f"\nTesting model on dataset: {dataset_path}\n")
        
        student_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]
        
        total_correct = 0
        total_images = 0
        results = []
        
        for student_dir in sorted(student_dirs):
            true_id = student_dir.name
            image_files = list(student_dir.glob('*.jpg')) + \
                         list(student_dir.glob('*.jpeg')) + \
                         list(student_dir.glob('*.png'))
            
            logger.info(f"\nTesting {true_id}: {len(image_files)} images")
            logger.info("-" * 60)
            
            correct = 0
            for img_path in image_files:
                try:
                    pred_id, confidence = self.predict_image(img_path)
                    
                    if pred_id == true_id:
                        correct += 1
                        total_correct += 1
                    
                    total_images += 1
                    results.append({
                        'true_id': true_id,
                        'pred_id': pred_id,
                        'confidence': confidence,
                        'correct': pred_id == true_id
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing {img_path}: {e}")
            
            accuracy = correct / len(image_files) if image_files else 0
            logger.info(f"\n{true_id} Accuracy: {correct}/{len(image_files)} ({accuracy:.2%})")
        
        # Overall statistics
        overall_accuracy = total_correct / total_images if total_images > 0 else 0
        
        logger.info("\n" + "="*60)
        logger.info("OVERALL RESULTS")
        logger.info("="*60)
        logger.info(f"Total images tested: {total_images}")
        logger.info(f"Correct predictions: {total_correct}")
        logger.info(f"Overall accuracy: {overall_accuracy:.2%}")
        logger.info("="*60)
        
        # Show confusion cases
        errors = [r for r in results if not r['correct']]
        if errors:
            logger.info("\nMisclassifications:")
            for err in errors:
                logger.info(f"  True: {err['true_id']}, Predicted: {err['pred_id']}, Confidence: {err['confidence']:.4f}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test trained face recognition model')
    parser.add_argument('--model', type=str, default='models/Classifier',
                       help='Path to model directory')
    parser.add_argument('--image', type=str,
                       help='Test single image')
    parser.add_argument('--dataset', type=str, default='dataset',
                       help='Test entire dataset')
    parser.add_argument('--test-all', action='store_true',
                       help='Test model on entire dataset')
    
    args = parser.parse_args()
    
    # Create tester
    tester = ModelTester(model_path=args.model)
    
    if args.image:
        # Test single image
        student_id, confidence = tester.predict_image(args.image)
        if student_id:
            print(f"\nResult: {student_id} (confidence: {confidence:.4f})")
    
    elif args.test_all:
        # Test entire dataset
        tester.test_dataset(dataset_path=args.dataset)
    
    else:
        logger.info("\nModel loaded successfully!")
        logger.info("\nUsage:")
        logger.info("  Test single image: python test_trained_model.py --image path/to/image.jpg")
        logger.info("  Test dataset: python test_trained_model.py --test-all")


if __name__ == '__main__':
    main()
