"""
FIXED Production Face Recognition Training Pipeline
Ensures training and inference use IDENTICAL preprocessing
Fixes embedding distribution mismatch causing low confidence scores
"""

import os
import sys
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from PIL import Image
import torch

from torchvision import transforms
from facenet_pytorch import MTCNN, InceptionResnetV1
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import logging
from tqdm import tqdm

# Set random seeds
np.random.seed(42)
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_fixed.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FixedProductionTrainer:
    """
    Fixed trainer that ensures training and inference use IDENTICAL preprocessing
    
    KEY FIX: Applies L2 normalization to embeddings BEFORE training,
    matching the normalization applied during inference
    """
    
    def __init__(self, dataset_path='dataset/processed', output_path='models/Classifier'):
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Device setup
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Initialize MTCNN (same as inference)
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
        
        # Initialize FaceNet (same as inference)
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        logger.info("✅ Loaded FaceNet InceptionResnetV1 (vggface2) - 512-dim embeddings")
        
        # Transform (same as inference)
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
    
    def extract_embeddings(self):
        """
        Extract 512-dimensional embeddings with L2 normalization
        
        CRITICAL FIX: Applies L2 normalization to match inference pipeline
        """
        logger.info("Extracting embeddings with L2 normalization...")
        logger.info("⚠️  IMPORTANT: Embeddings will be L2-normalized to match inference")
        
        embeddings_list = []
        valid_labels = []
        valid_paths = []
        failed_count = 0
        
        with torch.no_grad():
            for img_path, label in tqdm(zip(self.image_paths, self.labels), 
                                       total=len(self.image_paths), 
                                       desc="Extracting embeddings"):
                try:
                    # Load image
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
                    
                    # ⭐ CRITICAL FIX: L2-normalize embedding (same as inference)
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding = embedding / norm
                    
                    embeddings_list.append(embedding)
                    valid_labels.append(label)
                    valid_paths.append(img_path)
                    
                except Exception as e:
                    logger.error(f"Error processing {img_path}: {e}")
                    failed_count += 1
        
        self.embeddings = np.array(embeddings_list)
        self.labels = valid_labels
        self.image_paths = valid_paths
        
        logger.info(f"✅ Successfully extracted {len(self.embeddings)} embeddings")
        logger.info(f"❌ Failed: {failed_count} images")
        logger.info(f"📊 Embeddings shape: {self.embeddings.shape}")
        logger.info(f"📊 Embeddings are L2-normalized (unit length)")
        
        # Verify normalization
        norms = np.linalg.norm(self.embeddings, axis=1)
        logger.info(f"📊 Embedding norms - min: {norms.min():.4f}, max: {norms.max():.4f}, mean: {norms.mean():.4f}")
        
        if len(self.embeddings) == 0:
            raise ValueError("No valid embeddings extracted")
    
    def train_classifier(self, test_size=0.2):
        """Train SVM classifier on normalized embeddings"""
        logger.info("Training SVM classifier...")
        
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
        
        # ⭐ CRITICAL: Scale AFTER L2 normalization
        # StandardScaler on normalized embeddings helps SVM convergence
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        logger.info("📊 Scaler statistics:")
        logger.info(f"   Mean: {self.scaler.mean_[:5]}... (first 5 dims)")
        logger.info(f"   Std: {self.scaler.scale_[:5]}... (first 5 dims)")
        
        # Train SVM with probability estimates
        self.classifier = SVC(
            kernel='linear',
            probability=True,
            C=1.0,
            random_state=42,
            verbose=False
        )
        
        logger.info("Fitting SVM classifier...")
        self.classifier.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        logger.info(f"{'='*60}\n")
        
        # Classification report
        logger.info("Classification Report:")
        report = classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            zero_division=0
        )
        logger.info(f"\n{report}")
        
        return accuracy, X_train_scaled, y_train, X_test_scaled, y_test
    
    def calculate_adaptive_threshold(self, X_train_scaled, y_train, percentile=5):
        """
        Calculate adaptive confidence threshold using training data
        
        Uses the percentile of CORRECT predictions as threshold
        This ensures most training samples are above threshold
        """
        logger.info("Calculating adaptive confidence threshold...")
        
        # Get prediction probabilities for training data
        probabilities = self.classifier.predict_proba(X_train_scaled)
        
        # Get max probability for each sample
        max_probs = np.max(probabilities, axis=1)
        
        # Get predicted classes
        y_pred = self.classifier.predict(X_train_scaled)
        
        # Get probabilities for CORRECT predictions only
        correct_mask = (y_pred == y_train)
        correct_probs = max_probs[correct_mask]
        
        # Calculate threshold as low percentile of correct predictions
        # This means X% of correct predictions will be below threshold
        threshold = np.percentile(correct_probs, percentile)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 Confidence Statistics (Training Set):")
        logger.info(f"{'='*60}")
        logger.info(f"Total samples: {len(max_probs)}")
        logger.info(f"Correct predictions: {correct_mask.sum()} ({correct_mask.sum()/len(max_probs)*100:.1f}%)")
        logger.info(f"Incorrect predictions: {(~correct_mask).sum()}")
        logger.info(f"\nAll predictions:")
        logger.info(f"  Min confidence: {max_probs.min():.4f}")
        logger.info(f"  Max confidence: {max_probs.max():.4f}")
        logger.info(f"  Mean confidence: {max_probs.mean():.4f}")
        logger.info(f"  Median confidence: {np.median(max_probs):.4f}")
        logger.info(f"\nCorrect predictions only:")
        logger.info(f"  Min confidence: {correct_probs.min():.4f}")
        logger.info(f"  Max confidence: {correct_probs.max():.4f}")
        logger.info(f"  Mean confidence: {correct_probs.mean():.4f}")
        logger.info(f"  Median confidence: {np.median(correct_probs):.4f}")
        logger.info(f"\n⭐ Adaptive Threshold ({percentile}th percentile): {threshold:.4f}")
        logger.info(f"   This means {100-percentile}% of correct predictions are above threshold")
        logger.info(f"{'='*60}\n")
        
        return threshold
    
    def save_model(self, threshold, accuracy):
        """Save model artifacts with metadata"""
        logger.info("Saving model artifacts...")
        
        # Prepare metadata
        metadata = {
            'embedding_model': 'InceptionResnetV1',
            'pretrained_on': 'vggface2',
            'embedding_dim': 512,
            'normalize_embeddings': True,  # ⭐ CRITICAL FLAG
            'num_classes': len(self.label_encoder.classes_),
            'classes': self.label_encoder.classes_.tolist(),
            'threshold': float(threshold),
            'classifier_type': 'SVC',
            'kernel': 'linear',
            'accuracy': float(accuracy),
            'training_date': datetime.now().isoformat(),
            'python_version': sys.version,
            'torch_version': torch.__version__,
            'num_training_samples': len(self.embeddings),
            'preprocessing_pipeline': [
                '1. MTCNN face detection (160x160, margin=20)',
                '2. FaceNet embedding extraction (512-dim)',
                '3. L2 normalization (unit length)',
                '4. StandardScaler normalization',
                '5. SVM classification'
            ]
        }
        
        # Save main classifier file
        classifier_data = {
            'classifier': self.classifier,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'metadata': metadata
        }
        
        classifier_path = self.output_path / 'face_classifier_v1.pkl'
        with open(classifier_path, 'wb') as f:
            pickle.dump(classifier_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"✅ Saved: {classifier_path}")
        
        # Save label encoder classes
        classes_path = self.output_path / 'label_encoder_classes.npy'
        np.save(classes_path, self.label_encoder.classes_)
        logger.info(f"✅ Saved: {classes_path}")
        
        # Save embeddings (L2-normalized)
        X_path = self.output_path / 'X.npy'
        y_path = self.output_path / 'y.npy'
        np.save(X_path, self.embeddings)
        np.save(y_path, self.label_encoder.transform(self.labels))
        logger.info(f"✅ Saved: {X_path} (L2-normalized embeddings)")
        logger.info(f"✅ Saved: {y_path}")
        
        # Save metadata as JSON
        import json
        metadata_path = self.output_path / 'training_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"✅ Saved: {metadata_path}")
        
        # Save training summary
        summary_path = self.output_path / 'training_summary.txt'
        with open(summary_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("FIXED FACE RECOGNITION MODEL - TRAINING SUMMARY\n")
            f.write("="*60 + "\n\n")
            f.write("⭐ KEY FIX: Embeddings are L2-normalized during training\n")
            f.write("   This matches the normalization applied during inference\n\n")
            f.write(f"Training Date: {metadata['training_date']}\n")
            f.write(f"Embedding Model: {metadata['embedding_model']} ({metadata['pretrained_on']})\n")
            f.write(f"Embedding Dimension: {metadata['embedding_dim']}\n")
            f.write(f"L2 Normalized: {metadata['normalize_embeddings']}\n")
            f.write(f"Classifier: {metadata['classifier_type']} ({metadata['kernel']} kernel)\n")
            f.write(f"Number of Students: {metadata['num_classes']}\n")
            f.write(f"Training Samples: {metadata['num_training_samples']}\n")
            f.write(f"Test Accuracy: {metadata['accuracy']:.4f} ({metadata['accuracy']*100:.2f}%)\n")
            f.write(f"Confidence Threshold: {metadata['threshold']:.4f}\n\n")
            f.write("Preprocessing Pipeline:\n")
            for step in metadata['preprocessing_pipeline']:
                f.write(f"  {step}\n")
            f.write("\nStudent IDs:\n")
            for i, student_id in enumerate(metadata['classes'], 1):
                f.write(f"  {i}. {student_id}\n")
            f.write("\n" + "="*60 + "\n")
        logger.info(f"✅ Saved: {summary_path}")
        
        logger.info("\n" + "="*60)
        logger.info("✅ MODEL TRAINING COMPLETE")
        logger.info("="*60)
        logger.info(f"Output directory: {self.output_path}")
        logger.info("="*60)
        
    def train(self, threshold_percentile=5):
        """Complete training pipeline"""
        try:
            logger.info("\n" + "="*60)
            logger.info("🔧 STARTING FIXED FACE RECOGNITION TRAINING")
            logger.info("="*60)
            logger.info("⭐ KEY FIX: L2 normalization applied to embeddings")
            logger.info("="*60 + "\n")
            
            # Step 1: Load dataset
            self.load_dataset()
            
            # Step 2: Extract embeddings with L2 normalization
            self.extract_embeddings()
            
            # Step 3: Train classifier
            accuracy, X_train_scaled, y_train, X_test_scaled, y_test = self.train_classifier()
            
            # Step 4: Calculate adaptive threshold
            threshold = self.calculate_adaptive_threshold(X_train_scaled, y_train, percentile=threshold_percentile)
            
            # Step 5: Save model
            self.save_model(threshold, accuracy)
            
            logger.info("\n✅ Training completed successfully!")
            logger.info("⭐ Model is now compatible with inference pipeline")
            return True
            
        except Exception as e:
            logger.error(f"\n❌ Training failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main training function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train FIXED face recognition model')
    parser.add_argument('--dataset', type=str, default='dataset/processed',
                       help='Path to processed dataset directory')
    parser.add_argument('--output', type=str, default='models/Classifier',
                       help='Path to save model artifacts')
    parser.add_argument('--threshold-percentile', type=int, default=5,
                       help='Percentile for confidence threshold (1-100, lower=stricter)')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = FixedProductionTrainer(
        dataset_path=args.dataset,
        output_path=args.output
    )
    
    # Train model
    success = trainer.train(threshold_percentile=args.threshold_percentile)
    
    if success:
        logger.info("\n" + "="*60)
        logger.info("✅ READY FOR PRODUCTION")
        logger.info("="*60)
        logger.info("Next steps:")
        logger.info("1. Test model: python test_fixed_model.py")
        logger.info("2. Start backend: python app.py")
        logger.info("3. Test live recognition in frontend")
        logger.info("="*60 + "\n")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
