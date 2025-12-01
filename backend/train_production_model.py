"""
Production Face Recognition Training Pipeline
Trains MTCNN + FaceNet model compatible with SmartAttendance backend
Outputs: face_classifier_v1.pkl, label_encoder_classes.npy, X.npy, y.npy
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from PIL import Image
import torch

from torchvision import transforms
from facenet_pytorch import MTCNN, InceptionResnetV1
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import logging
from tqdm import tqdm

# Set random seeds for reproducibility
np.random.seed(42)
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProductionTrainer:
    """Production-ready face recognition trainer"""
    
    def __init__(self, dataset_path='dataset/processed', output_path='models/Classifier'):
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Device setup
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Initialize models
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
        logger.info("Loaded FaceNet InceptionResnetV1 (vggface2) - 512-dim embeddings")
        
        # Data augmentation transforms
        self.transform = transforms.Compose([
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        
        # Storage
        self.image_paths = []
        self.labels = []
        self.embeddings = None
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.classifier = None
        
    def load_dataset(self):
        """Load dataset from processed folder structure"""
        logger.info(f"Loading dataset from: {self.dataset_path}")
        
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset path not found: {self.dataset_path}")
        
        student_dirs = [d for d in self.dataset_path.iterdir() if d.is_dir()]
        
        if len(student_dirs) == 0:
            raise ValueError(f"No student directories found in {self.dataset_path}")
        
        logger.info(f"Found {len(student_dirs)} student directories")
        
        for student_dir in sorted(student_dirs):
            student_id = student_dir.name
            
            # Get all image files
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                image_files.extend(list(student_dir.glob(ext)))
            
            if len(image_files) == 0:
                logger.warning(f"No images found for {student_id}")
                continue
            
            logger.info(f"Loading {student_id}: {len(image_files)} images")
            
            for img_path in image_files:
                self.image_paths.append(str(img_path))
                self.labels.append(student_id)
        
        logger.info(f"Total images loaded: {len(self.image_paths)}")
        logger.info(f"Unique students: {len(set(self.labels))}")
        
        if len(self.image_paths) == 0:
            raise ValueError("No images found in dataset")
        
    def extract_embeddings(self, batch_size=32):
        """Extract 512-dimensional embeddings from all images"""
        logger.info("Extracting embeddings...")
        
        embeddings_list = []
        valid_labels = []
        valid_paths = []
        failed_count = 0
        
        # Process images one by one (simpler and more reliable)
        with torch.no_grad():
            for img_path, label in tqdm(zip(self.image_paths, self.labels), 
                                       total=len(self.image_paths), 
                                       desc="Extracting embeddings"):
                try:
                    # Load and detect face
                    img = Image.open(img_path).convert('RGB')
                    
                    # Try MTCNN detection first
                    face_tensor = self.mtcnn(img)
                    
                    # If MTCNN fails, use direct resize (images are pre-cropped)
                    if face_tensor is None:
                        img_resized = img.resize((160, 160))
                        face_tensor = self.transform(img_resized).unsqueeze(0)
                    else:
                        face_tensor = face_tensor.unsqueeze(0)
                    
                    # Extract embedding
                    face_tensor = face_tensor.to(self.device)
                    embedding = self.facenet(face_tensor).cpu().numpy().flatten()
                    
                    # Verify dimension
                    if embedding.shape[0] != 512:
                        logger.error(f"Invalid embedding dimension: {embedding.shape[0]} for {img_path}")
                        failed_count += 1
                        continue
                    
                    embeddings_list.append(embedding)
                    valid_labels.append(label)
                    valid_paths.append(img_path)
                    
                except Exception as e:
                    logger.error(f"Error processing {img_path}: {e}")
                    failed_count += 1
        
        self.embeddings = np.array(embeddings_list)
        self.labels = valid_labels
        self.image_paths = valid_paths
        
        logger.info(f"Successfully extracted {len(self.embeddings)} embeddings")
        logger.info(f"Failed: {failed_count} images")
        logger.info(f"Embeddings shape: {self.embeddings.shape}")
        
        if len(self.embeddings) == 0:
            raise ValueError("No valid embeddings extracted")
        
    def train_classifier(self, classifier_type='svm', test_size=0.2):
        """Train classifier with stratified split"""
        logger.info(f"Training {classifier_type.upper()} classifier...")
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(self.labels)
        
        # Stratified split
        X_train, X_test, y_train, y_test = train_test_split(
            self.embeddings, y_encoded,
            test_size=test_size,
            random_state=42,
            stratify=y_encoded
        )
        
        logger.info(f"Training set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        # Scale embeddings
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train classifier
        if classifier_type == 'svm':
            self.classifier = SVC(
                kernel='linear',
                probability=True,
                C=1.0,
                random_state=42,
                verbose=False
            )
        elif classifier_type == 'logistic':
            self.classifier = LogisticRegression(
                max_iter=2000,
                random_state=42,
                multi_class='ovr',
                verbose=0
            )
        else:
            raise ValueError(f"Unknown classifier type: {classifier_type}")
        
        logger.info("Fitting classifier...")
        self.classifier.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Test Accuracy: {accuracy:.4f}")
        logger.info(f"{'='*60}\n")
        
        # Classification report
        logger.info("Classification Report:")
        report = classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            zero_division=0
        )
        logger.info(f"\n{report}")
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        logger.info(f"Confusion Matrix:\n{cm}")
        
        return accuracy, X_train_scaled, y_train, X_test_scaled, y_test
    
    def calculate_threshold(self, X_train_scaled, percentile=95):
        """Calculate confidence threshold for open-set recognition"""
        logger.info("Calculating confidence threshold...")
        
        # Get prediction probabilities
        probabilities = self.classifier.predict_proba(X_train_scaled)
        max_probs = np.max(probabilities, axis=1)
        
        # Calculate threshold
        threshold = np.percentile(max_probs, percentile)
        
        logger.info(f"Confidence threshold (percentile={percentile}): {threshold:.4f}")
        logger.info(f"Min confidence: {max_probs.min():.4f}")
        logger.info(f"Max confidence: {max_probs.max():.4f}")
        logger.info(f"Mean confidence: {max_probs.mean():.4f}")
        logger.info(f"Std confidence: {max_probs.std():.4f}")
        
        return threshold
    
    def save_model(self, threshold, accuracy):
        """Save model artifacts in backend-compatible format"""
        logger.info("Saving model artifacts...")
        
        # Prepare metadata
        metadata = {
            'embedding_model': 'InceptionResnetV1',
            'pretrained_on': 'vggface2',
            'embedding_dim': 512,
            'num_classes': len(self.label_encoder.classes_),
            'classes': self.label_encoder.classes_.tolist(),
            'threshold': float(threshold),
            'classifier_type': type(self.classifier).__name__,
            'accuracy': float(accuracy),
            'training_date': datetime.now().isoformat(),
            'python_version': sys.version,
            'torch_version': torch.__version__,
            'num_training_samples': len(self.embeddings)
        }
        
        # Save main classifier file (backend expects this exact name)
        classifier_data = {
            'classifier': self.classifier,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'metadata': metadata
        }
        
        classifier_path = self.output_path / 'face_classifier_v1.pkl'
        with open(classifier_path, 'wb') as f:
            pickle.dump(classifier_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"✓ Saved: {classifier_path}")
        
        # Save label encoder classes (backend expects this)
        classes_path = self.output_path / 'label_encoder_classes.npy'
        np.save(classes_path, self.label_encoder.classes_)
        logger.info(f"✓ Saved: {classes_path}")
        
        # Save embeddings and labels (optional, for analysis)
        X_path = self.output_path / 'X.npy'
        y_path = self.output_path / 'y.npy'
        np.save(X_path, self.embeddings)
        np.save(y_path, self.label_encoder.transform(self.labels))
        logger.info(f"✓ Saved: {X_path}")
        logger.info(f"✓ Saved: {y_path}")
        
        # Save metadata as separate JSON for easy reading
        import json
        metadata_path = self.output_path / 'training_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✓ Saved: {metadata_path}")
        
        # Save training summary
        summary_path = self.output_path / 'training_summary.txt'
        with open(summary_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("FACE RECOGNITION MODEL TRAINING SUMMARY\n")
            f.write("="*60 + "\n\n")
            f.write(f"Training Date: {metadata['training_date']}\n")
            f.write(f"Embedding Model: {metadata['embedding_model']} ({metadata['pretrained_on']})\n")
            f.write(f"Embedding Dimension: {metadata['embedding_dim']}\n")
            f.write(f"Classifier: {metadata['classifier_type']}\n")
            f.write(f"Number of Students: {metadata['num_classes']}\n")
            f.write(f"Training Samples: {metadata['num_training_samples']}\n")
            f.write(f"Test Accuracy: {metadata['accuracy']:.4f}\n")
            f.write(f"Confidence Threshold: {metadata['threshold']:.4f}\n\n")
            f.write("Student IDs:\n")
            for i, student_id in enumerate(metadata['classes'], 1):
                f.write(f"  {i}. {student_id}\n")
            f.write("\n" + "="*60 + "\n")
        logger.info(f"✓ Saved: {summary_path}")
        
        logger.info("\n" + "="*60)
        logger.info("MODEL TRAINING COMPLETE")
        logger.info("="*60)
        logger.info(f"Output directory: {self.output_path}")
        logger.info(f"Files created:")
        logger.info(f"  - face_classifier_v1.pkl (main model)")
        logger.info(f"  - label_encoder_classes.npy (student IDs)")
        logger.info(f"  - X.npy (embeddings)")
        logger.info(f"  - y.npy (labels)")
        logger.info(f"  - training_metadata.json (metadata)")
        logger.info(f"  - training_summary.txt (summary)")
        logger.info("="*60)
        
    def train(self, classifier_type='svm', threshold_percentile=95):
        """Complete training pipeline"""
        try:
            logger.info("\n" + "="*60)
            logger.info("STARTING FACE RECOGNITION TRAINING")
            logger.info("="*60 + "\n")
            
            # Step 1: Load dataset
            self.load_dataset()
            
            # Step 2: Extract embeddings
            self.extract_embeddings(batch_size=16)
            
            # Step 3: Train classifier
            accuracy, X_train_scaled, y_train, X_test_scaled, y_test = self.train_classifier(
                classifier_type=classifier_type
            )
            
            # Step 4: Calculate threshold
            threshold = self.calculate_threshold(X_train_scaled, percentile=threshold_percentile)
            
            # Step 5: Save model
            self.save_model(threshold, accuracy)
            
            logger.info("\n✓ Training completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"\n✗ Training failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main training function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train production face recognition model')
    parser.add_argument('--dataset', type=str, default='dataset/processed',
                       help='Path to processed dataset directory')
    parser.add_argument('--output', type=str, default='models/Classifier',
                       help='Path to save model artifacts')
    parser.add_argument('--classifier', type=str, default='svm',
                       choices=['svm', 'logistic'],
                       help='Classifier type')
    parser.add_argument('--threshold-percentile', type=int, default=95,
                       help='Percentile for confidence threshold (1-100)')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = ProductionTrainer(
        dataset_path=args.dataset,
        output_path=args.output
    )
    
    # Train model
    success = trainer.train(
        classifier_type=args.classifier,
        threshold_percentile=args.threshold_percentile
    )
    
    if success:
        logger.info("\n" + "="*60)
        logger.info("READY FOR PRODUCTION")
        logger.info("="*60)
        logger.info("Next steps:")
        logger.info("1. Test model: python test_production_model.py")
        logger.info("2. Start backend: python app.py")
        logger.info("3. Test live recognition in frontend")
        logger.info("="*60 + "\n")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
