"""
Test Production Model
Verifies trained model works correctly and tests unknown detection
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


class ProductionModelTester:
    """Test production face recognition model"""
    
    def __init__(self, model_path='models/Classifier'):
        self.model_path = Path(model_path)
        
        # Device setup
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Load model
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
        
        # Load main classifier file
        classifier_path = self.model_path / 'face_classifier_v1.pkl'
        with open(classifier_path, 'rb') as f:
            data = pickle.load(f)
        
        self.classifier = data['classifier']
        self.scaler = data['scaler']
        self.label_encoder = data['label_encoder']
        self.metadata = data['metadata']
        
        logger.info(f"✓ Loaded classifier: {self.metadata['classifier_type']}")
        logger.info(f"✓ Number of classes: {self.metadata['num_classes']}")
        logger.info(f"✓ Confidence threshold: {self.metadata['threshold']:.4f}")
        
        # Display model info
        logger.info("\n" + "="*60)
        logger.info("MODEL INFORMATION")
        logger.info("="*60)
        logger.info(f"Embedding Model: {self.metadata['embedding_model']}")
        logger.info(f"Pre-trained on: {self.metadata['pretrained_on']}")
        logger.info(f"Embedding Dimension: {self.metadata['embedding_dim']}")
        logger.info(f"Classifier: {self.metadata['classifier_type']}")
        logger.info(f"Training Accuracy: {self.metadata['accuracy']:.4f}")
        logger.info(f"Confidence Threshold: {self.metadata['threshold']:.4f}")
        logger.info(f"Training Date: {self.metadata['training_date']}")
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
            # Fallback: resize directly
            from torchvision import transforms
            transform = transforms.Compose([
                transforms.Resize((160, 160)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
            ])
            face_tensor = transform(img)
        
        # Extract embedding
        with torch.no_grad():
            face_tensor = face_tensor.unsqueeze(0).to(self.device)
            embedding = self.facenet(face_tensor).cpu().numpy().flatten()
        
        # Verify dimension
        if embedding.shape[0] != self.metadata['embedding_dim']:
            logger.error(f"✗ Invalid embedding dimension: {embedding.shape[0]}")
            return None, 0.0
        
        # Scale embedding
        embedding_scaled = self.scaler.transform(embedding.reshape(1, -1))
        
        # Predict
        prediction = self.classifier.predict(embedding_scaled)[0]
        probabilities = self.classifier.predict_proba(embedding_scaled)[0]
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
            
            # Show top 3 predictions
            top_3_idx = np.argsort(probabilities)[-3:][::-1]
            logger.info("  Top 3 predictions:")
            for idx in top_3_idx:
                student = self.label_encoder.inverse_transform([idx])[0]
                prob = probabilities[idx]
                logger.info(f"    {student}: {prob:.4f}")
            
            return student_id, confidence
    
    def test_dataset(self, dataset_path='dataset/processed'):
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
            
            # Get all image files
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                image_files.extend(list(student_dir.glob(ext)))
            
            if len(image_files) == 0:
                continue
            
            logger.info(f"\nTesting {true_id}: {len(image_files)} images")
            logger.info("-" * 60)
            
            correct = 0
            for img_path in image_files[:5]:  # Test first 5 images per student
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
            
            accuracy = correct / min(5, len(image_files))
            logger.info(f"\n{true_id} Accuracy: {correct}/{min(5, len(image_files))} ({accuracy:.2%})")
        
        # Overall statistics
        overall_accuracy = total_correct / total_images if total_images > 0 else 0
        
        logger.info("\n" + "="*60)
        logger.info("OVERALL TEST RESULTS")
        logger.info("="*60)
        logger.info(f"Total images tested: {total_images}")
        logger.info(f"Correct predictions: {total_correct}")
        logger.info(f"Overall accuracy: {overall_accuracy:.2%}")
        logger.info("="*60)
        
        # Show misclassifications
        errors = [r for r in results if not r['correct']]
        if errors:
            logger.info(f"\nMisclassifications ({len(errors)}):")
            for err in errors:
                logger.info(f"  True: {err['true_id']}, Predicted: {err['pred_id']}, Confidence: {err['confidence']:.4f}")
        else:
            logger.info("\n✓ No misclassifications!")
    
    def test_unknown_detection(self):
        """Test unknown face detection"""
        logger.info("\n" + "="*60)
        logger.info("UNKNOWN DETECTION TEST")
        logger.info("="*60)
        logger.info("To test unknown detection, provide an image of a person")
        logger.info("not in the training set and verify it's marked as 'Unknown'")
        logger.info("="*60 + "\n")


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test production face recognition model')
    parser.add_argument('--model', type=str, default='models/Classifier',
                       help='Path to model directory')
    parser.add_argument('--image', type=str,
                       help='Test single image')
    parser.add_argument('--dataset', type=str, default='dataset/processed',
                       help='Test entire dataset')
    parser.add_argument('--test-all', action='store_true',
                       help='Test model on entire dataset')
    
    args = parser.parse_args()
    
    # Create tester
    tester = ProductionModelTester(model_path=args.model)
    
    if args.image:
        # Test single image
        student_id, confidence = tester.predict_image(args.image)
        if student_id:
            print(f"\nResult: {student_id} (confidence: {confidence:.4f})")
    
    elif args.test_all:
        # Test entire dataset
        tester.test_dataset(dataset_path=args.dataset)
        tester.test_unknown_detection()
    
    else:
        logger.info("\nModel loaded successfully!")
        logger.info("\nUsage:")
        logger.info("  Test single image: python test_production_model.py --image path/to/image.jpg")
        logger.info("  Test dataset: python test_production_model.py --test-all")


if __name__ == '__main__':
    main()
