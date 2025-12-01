"""
Face Recognition Model Training Script
Trains from scratch using MTCNN + FaceNet + SVM/LogisticRegression
Implements open-set recognition for unknown face detection
"""

import os
import sys
import pickle
import numpy as np
from pathlib import Path
from PIL import Image
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FaceRecognitionTrainer:
    """Train face recognition model from scratch"""
    
    def __init__(self, dataset_path='backend/dataset', output_path='backend/models/Classifier'):
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Initialize MTCNN for face detection
        self.mtcnn = MTCNN(
            image_size=160,
            margin=20,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            device=self.device,
            keep_all=False  # Only detect the most prominent face
        )
        
        # Initialize FaceNet for embeddings (512-dimensional)
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        logger.info("Loaded FaceNet model (vggface2) - 512-dimensional embeddings")
        
        self.embeddings = []
        self.labels = []
        self.label_encoder = LabelEncoder()
        
    def load_dataset(self):
        """
        Load images from dataset directory structure:
        dataset/
            student_id_1/
                image1.jpg
                image2.jpg
            student_id_2/
                image1.jpg
        """
        logger.info(f"Loading dataset from: {self.dataset_path}")
        
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset path not found: {self.dataset_path}")
        
        student_dirs = [d for d in self.dataset_path.iterdir() if d.is_dir()]
        
        if len(student_dirs) == 0:
            raise ValueError(f"No student directories found in {self.dataset_path}")
        
        logger.info(f"Found {len(student_dirs)} student directories")
        
        total_images = 0
        failed_images = 0
        
        for student_dir in student_dirs:
            student_id = student_dir.name
            image_files = list(student_dir.glob('*.jpg')) + \
                         list(student_dir.glob('*.jpeg')) + \
                         list(student_dir.glob('*.png'))
            
            logger.info(f"Processing {student_id}: {len(image_files)} images")
            
            for img_path in image_files:
                try:
                    # Load and detect face
                    img = Image.open(img_path).convert('RGB')
                    face_tensor = self.mtcnn(img)
                    
                    if face_tensor is None:
                        logger.warning(f"No face detected in {img_path}")
                        failed_images += 1
                        continue
                    
                    # Extract embedding
                    with torch.no_grad():
                        face_tensor = face_tensor.unsqueeze(0).to(self.device)
                        embedding = self.facenet(face_tensor).cpu().numpy().flatten()
                    
                    # Verify embedding dimension
                    if embedding.shape[0] != 512:
                        logger.error(f"Invalid embedding dimension: {embedding.shape[0]}")
                        failed_images += 1
                        continue
                    
                    self.embeddings.append(embedding)
                    self.labels.append(student_id)
                    total_images += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {img_path}: {e}")
                    failed_images += 1
        
        logger.info(f"Successfully processed {total_images} images")
        logger.info(f"Failed to process {failed_images} images")
        
        if total_images == 0:
            raise ValueError("No valid face embeddings extracted from dataset")
        
        # Convert to numpy arrays
        self.embeddings = np.array(self.embeddings)
        self.labels = np.array(self.labels)
        
        logger.info(f"Embeddings shape: {self.embeddings.shape}")
        logger.info(f"Unique students: {len(np.unique(self.labels))}")
        
    def train_classifier(self, classifier_type='svm', test_size=0.2):
        """
        Train classifier on embeddings
        
        Args:
            classifier_type: 'svm' or 'logistic'
            test_size: Proportion of data for testing
        """
        logger.info(f"Training {classifier_type.upper()} classifier...")
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(self.labels)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            self.embeddings, y_encoded, 
            test_size=test_size, 
            random_state=42,
            stratify=y_encoded
        )
        
        logger.info(f"Training set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        # Train classifier
        if classifier_type == 'svm':
            self.classifier = SVC(
                kernel='linear',
                probability=True,
                C=1.0,
                random_state=42
            )
        elif classifier_type == 'logistic':
            self.classifier = LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='ovr'
            )
        else:
            raise ValueError(f"Unknown classifier type: {classifier_type}")
        
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Test Accuracy: {accuracy:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_
        ))
        
        return accuracy
    
    def calculate_threshold(self, percentile=95):
        """
        Calculate confidence threshold for open-set recognition
        Uses training data to determine threshold for unknown detection
        """
        logger.info("Calculating confidence threshold for open-set recognition...")
        
        # Get prediction probabilities for training data
        probabilities = self.classifier.predict_proba(self.embeddings)
        max_probs = np.max(probabilities, axis=1)
        
        # Use percentile of max probabilities as threshold
        threshold = np.percentile(max_probs, percentile)
        
        logger.info(f"Confidence threshold (percentile={percentile}): {threshold:.4f}")
        logger.info(f"Min confidence: {max_probs.min():.4f}")
        logger.info(f"Max confidence: {max_probs.max():.4f}")
        logger.info(f"Mean confidence: {max_probs.mean():.4f}")
        
        return threshold
    
    def save_model(self, threshold):
        """Save all model artifacts"""
        logger.info("Saving model artifacts...")
        
        # Save classifier
        classifier_path = self.output_path / 'face_classifier.pkl'
        with open(classifier_path, 'wb') as f:
            pickle.dump(self.classifier, f)
        logger.info(f"Saved classifier to {classifier_path}")
        
        # Save label encoder
        encoder_path = self.output_path / 'label_encoder.pkl'
        with open(encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        logger.info(f"Saved label encoder to {encoder_path}")
        
        # Save metadata
        metadata = {
            'embedding_dim': 512,
            'num_classes': len(self.label_encoder.classes_),
            'classes': self.label_encoder.classes_.tolist(),
            'threshold': threshold,
            'model_type': type(self.classifier).__name__,
            'facenet_model': 'vggface2',
            'detector': 'MTCNN'
        }
        
        metadata_path = self.output_path / 'model_metadata.pkl'
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        logger.info(f"Saved metadata to {metadata_path}")
        
        logger.info("\n" + "="*60)
        logger.info("MODEL TRAINING COMPLETE")
        logger.info("="*60)
        logger.info(f"Embedding dimension: {metadata['embedding_dim']}")
        logger.info(f"Number of students: {metadata['num_classes']}")
        logger.info(f"Confidence threshold: {metadata['threshold']:.4f}")
        logger.info(f"Classifier type: {metadata['model_type']}")
        logger.info("="*60)
        
    def train(self, classifier_type='svm', threshold_percentile=95):
        """Complete training pipeline"""
        try:
            # Load dataset
            self.load_dataset()
            
            # Train classifier
            accuracy = self.train_classifier(classifier_type=classifier_type)
            
            # Calculate threshold
            threshold = self.calculate_threshold(percentile=threshold_percentile)
            
            # Save model
            self.save_model(threshold)
            
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main training function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train face recognition model')
    parser.add_argument('--dataset', type=str, default='backend/dataset',
                       help='Path to dataset directory')
    parser.add_argument('--output', type=str, default='backend/models/Classifier',
                       help='Path to save model artifacts')
    parser.add_argument('--classifier', type=str, default='svm',
                       choices=['svm', 'logistic'],
                       help='Classifier type')
    parser.add_argument('--threshold-percentile', type=int, default=95,
                       help='Percentile for confidence threshold (1-100)')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = FaceRecognitionTrainer(
        dataset_path=args.dataset,
        output_path=args.output
    )
    
    # Train model
    success = trainer.train(
        classifier_type=args.classifier,
        threshold_percentile=args.threshold_percentile
    )
    
    if success:
        logger.info("\n✓ Training completed successfully!")
        sys.exit(0)
    else:
        logger.error("\n✗ Training failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
