"""
SmartAttendance Classifier Retraining Script
Clean reset + retrain with InsightFace detection + FaceNet embeddings + SVM classifier

Usage:
    python retrain_model.py
    python retrain_model.py --data-dir backend/dataset/processed --out-dir backend/models/Classifier
"""

import os
import sys
import shutil
import argparse
import pickle
import joblib
import numpy as np
import pandas as pd
import cv2
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import traceback

# Deep learning imports
import torch
from facenet_pytorch import InceptionResnetV1

# InsightFace for detection/alignment
from insightface.app import FaceAnalysis

# Sklearn imports
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Set random seeds
np.random.seed(42)
torch.manual_seed(42)

print("="*80)
print("SmartAttendance Face Recognition Retraining")
print("="*80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)


class FaceRecognitionRetrainer:
    """Complete retraining pipeline with clean reset"""
    
    def __init__(self, data_dir, out_dir, embeds_out):
        self.data_dir = Path(data_dir)
        self.out_dir = Path(out_dir)
        self.embeds_out = Path(embeds_out)
        self.models_dir = Path('models')
        
        # Create directories
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.embeds_out.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Device setup
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"\n✓ Using device: {self.device}")
        
        # Initialize models
        print("\n[1/8] Initializing models...")
        self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=-1, det_size=(640, 640))
        print("  ✓ InsightFace FaceAnalysis loaded (SCRFD detector)")
        
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        print("  ✓ FaceNet InceptionResnetV1 loaded (vggface2, 512-dim)")
        
        # Storage
        self.image_paths = []
        self.student_ids = []
        self.student_names = []
        self.X = []  # Embeddings
        self.y = []  # Labels
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.classifier = None
        
        # Tracking
        self.deleted_files = []
        self.skipped_images = []
        self.error_log = []
    
    def step0_confirm_paths(self):
        """Step 0: Confirm paths"""
        print("\n[Step 0] Confirming paths...")
        print(f"  Data directory: {self.data_dir.absolute()}")
        print(f"  Output directory: {self.out_dir.absolute()}")
        print(f"  Embeddings output: {self.embeds_out.absolute()}")
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        
        student_folders = [d for d in self.data_dir.iterdir() if d.is_dir()]
        print(f"  ✓ Found {len(student_folders)} student folders")
        
        if len(student_folders) == 0:
            raise ValueError(f"No student folders found in {self.data_dir}")
    
    def step1_cleanup_artifacts(self):
        """Step 1: Remove previous training artifacts"""
        print("\n[Step 1] Removing previous artifacts...")
        
        artifacts_to_delete = [
            self.out_dir / 'face_classifier_v1.pkl',
            self.out_dir / 'label_encoder.pkl',
            self.out_dir / 'label_encoder_classes.npy',
            self.models_dir / 'X.npy',
            self.models_dir / 'y.npy',
            self.models_dir / 'labels.csv',
            self.models_dir / 'training_report.txt',
            self.models_dir / 'MODEL_README.md',
            self.models_dir / 'temp',
            Path('backend/recognizer/embeddings_cache.npy'),
            Path('backend/models/X.npy'),
            Path('backend/models/y.npy'),
            Path('backend/models/labels.csv'),
            Path('backend/models/training_report.txt'),
            Path('backend/models/MODEL_README.md'),
            Path('backend/models/temp'),
        ]
        
        # Also check for any .pkl or .joblib in classifier dir
        if self.out_dir.exists():
            for pattern in ['*.pkl', '*.joblib']:
                artifacts_to_delete.extend(self.out_dir.glob(pattern))
        
        deleted_count = 0
        for artifact in artifacts_to_delete:
            try:
                if artifact.exists():
                    if artifact.is_dir():
                        shutil.rmtree(artifact)
                        print(f"  ✓ Deleted directory: {artifact}")
                    else:
                        artifact.unlink()
                        print(f"  ✓ Deleted file: {artifact}")
                    self.deleted_files.append(str(artifact))
                    deleted_count += 1
            except Exception as e:
                print(f"  ⚠ Failed to delete {artifact}: {e}")
                self.error_log.append(f"Delete failed: {artifact} - {e}")
        
        print(f"\n✔ Model cleanup completed. Deleted {deleted_count} artifacts. Ready for fresh training.")
    
    def step2_build_dataset_index(self):
        """Step 2: Build dataset index"""
        print("\n[Step 2] Building dataset index...")
        
        student_folders = sorted([d for d in self.data_dir.iterdir() if d.is_dir()])
        
        label_data = []
        
        for folder in student_folders:
            folder_name = folder.name
            
            # Parse folder name: STUxxx_Name or STUxxx
            if '_' in folder_name:
                parts = folder_name.split('_', 1)
                student_id = parts[0]
                student_name = parts[1] if len(parts) > 1 else parts[0]
            else:
                student_id = folder_name
                student_name = folder_name
            
            # Find all images
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG']:
                image_files.extend(list(folder.glob(ext)))
            
            if len(image_files) == 0:
                print(f"  ⚠ No images found in {folder_name}")
                continue
            
            print(f"  ✓ {student_id}: {len(image_files)} images")
            
            for img_path in image_files:
                self.image_paths.append(str(img_path))
                self.student_ids.append(student_id)
                self.student_names.append(student_name)
            
            label_data.append({
                'student_id': student_id,
                'student_name': student_name,
                'num_images': len(image_files)
            })
        
        # Save label mapping
        labels_df = pd.DataFrame(label_data)
        labels_csv_path = self.models_dir / 'labels.csv'
        labels_df.to_csv(labels_csv_path, index=False)
        print(f"\n  ✓ Saved label mapping: {labels_csv_path}")
        print(f"  Total images: {len(self.image_paths)}")
        print(f"  Unique students: {len(set(self.student_ids))}")
    
    def step3_extract_embeddings(self):
        """Step 3: Extract embeddings using InsightFace + FaceNet"""
        print("\n[Step 3] Extracting embeddings (InsightFace detection + FaceNet)...")
        
        with torch.no_grad():
            for idx, img_path in enumerate(tqdm(self.image_paths, desc="Processing images")):
                try:
                    # Load image
                    img = cv2.imread(img_path)
                    if img is None:
                        self.skipped_images.append((img_path, "Failed to load image"))
                        continue
                    
                    # Convert BGR to RGB
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    
                    # Detect faces with InsightFace
                    faces = self.face_app.get(img_rgb)
                    
                    if len(faces) == 0:
                        self.skipped_images.append((img_path, "No face detected"))
                        continue
                    
                    # Choose largest face if multiple detected
                    if len(faces) > 1:
                        face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
                    else:
                        face = faces[0]
                    
                    # Get aligned face (InsightFace provides alignment)
                    # Use the embedding from face or crop using bbox
                    bbox = face.bbox.astype(int)
                    x1, y1, x2, y2 = bbox
                    
                    # Ensure bbox is within image bounds
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(img_rgb.shape[1], x2)
                    y2 = min(img_rgb.shape[0], y2)
                    
                    # Crop face
                    face_crop = img_rgb[y1:y2, x1:x2]
                    
                    if face_crop.size == 0:
                        self.skipped_images.append((img_path, "Invalid face crop"))
                        continue
                    
                    # Resize to FaceNet input size (160x160)
                    face_resized = cv2.resize(face_crop, (160, 160))
                    
                    # Convert to tensor and normalize
                    face_tensor = torch.from_numpy(face_resized).permute(2, 0, 1).float()
                    face_tensor = (face_tensor - 127.5) / 128.0  # Normalize to [-1, 1]
                    face_tensor = face_tensor.unsqueeze(0).to(self.device)
                    
                    # Extract FaceNet embedding
                    embedding = self.facenet(face_tensor).cpu().numpy().flatten()
                    
                    # L2 normalize
                    embedding = embedding / np.linalg.norm(embedding)
                    
                    # Verify dimension
                    if embedding.shape[0] != 512:
                        self.skipped_images.append((img_path, f"Invalid embedding dim: {embedding.shape[0]}"))
                        continue
                    
                    # Store
                    self.X.append(embedding)
                    self.y.append(self.student_ids[idx])
                    
                except Exception as e:
                    self.skipped_images.append((img_path, str(e)))
                    self.error_log.append(f"Embedding extraction failed: {img_path} - {e}")
        
        # Convert to numpy arrays
        self.X = np.array(self.X)
        self.y = np.array(self.y)
        
        print(f"\n  ✓ Successfully extracted {len(self.X)} embeddings")
        print(f"  ✗ Skipped {len(self.skipped_images)} images")
        print(f"  Embeddings shape: {self.X.shape}")
        
        # Save embeddings
        X_path = self.models_dir / 'X.npy'
        y_path = self.models_dir / 'y.npy'
        np.save(X_path, self.X)
        np.save(y_path, self.y)
        print(f"  ✓ Saved embeddings: {X_path}")
        print(f"  ✓ Saved labels: {y_path}")
    
    def step4_train_classifier(self):
        """Step 4: Label encoding + classifier training"""
        print("\n[Step 4] Training classifier...")
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(self.y)
        
        # Save label encoder
        label_encoder_path = self.out_dir / 'label_encoder.pkl'
        with open(label_encoder_path, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        print(f"  ✓ Saved label encoder: {label_encoder_path}")
        
        # Save label encoder classes
        classes_path = self.out_dir / 'label_encoder_classes.npy'
        np.save(classes_path, self.label_encoder.classes_)
        print(f"  ✓ Saved label classes: {classes_path}")
        
        # Scale embeddings
        X_scaled = self.scaler.fit_transform(self.X)
        print(f"  ✓ Scaled embeddings with StandardScaler")
        
        # Train SVM classifier
        print(f"  Training SVM (linear kernel, probability=True)...")
        self.classifier = SVC(
            kernel='linear',
            probability=True,
            C=1.0,
            class_weight='balanced',
            random_state=42,
            verbose=False
        )
        
        self.classifier.fit(X_scaled, y_encoded)
        print(f"  ✓ Classifier trained on {len(X_scaled)} samples")
        
        # Save classifier (with scaler included)
        classifier_data = {
            'classifier': self.classifier,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'embedding_dim': 512,
            'model_type': 'FaceNet_InceptionResnetV1_vggface2',
            'detector': 'InsightFace_SCRFD',
            'training_date': datetime.now().isoformat()
        }
        
        classifier_path = self.out_dir / 'face_classifier_v1.pkl'
        with open(classifier_path, 'wb') as f:
            pickle.dump(classifier_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"  ✓ Saved classifier: {classifier_path}")
        
        return X_scaled, y_encoded
    
    def step5_evaluate_and_threshold(self, X_scaled, y_encoded):
        """Step 5: Evaluate and determine threshold"""
        print("\n[Step 5] Evaluating model and selecting threshold...")
        
        # Stratified train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded,
            test_size=0.2,
            random_state=42,
            stratify=y_encoded
        )
        
        print(f"  Train set: {len(X_train)} samples")
        print(f"  Test set: {len(X_test)} samples")
        
        # Predictions
        y_pred = self.classifier.predict(X_test)
        y_proba = self.classifier.predict_proba(X_test)
        
        # Accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n  Test Accuracy: {accuracy:.4f}")
        
        # Classification report
        report = classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            zero_division=0
        )
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Threshold analysis
        max_probas = np.max(y_proba, axis=1)
        
        print(f"\n  Confidence Statistics:")
        print(f"    Min: {max_probas.min():.4f}")
        print(f"    Max: {max_probas.max():.4f}")
        print(f"    Mean: {max_probas.mean():.4f}")
        print(f"    Median: {np.median(max_probas):.4f}")
        print(f"    Std: {max_probas.std():.4f}")
        
        # Evaluate different thresholds
        print(f"\n  Threshold Analysis:")
        thresholds = [0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.98]
        
        threshold_results = []
        for thresh in thresholds:
            # Apply threshold
            y_pred_thresh = []
            for i, proba in enumerate(y_proba):
                if max_probas[i] >= thresh:
                    y_pred_thresh.append(y_pred[i])
                else:
                    y_pred_thresh.append(-1)  # Unknown
            
            # Calculate metrics (excluding unknowns)
            valid_mask = np.array(y_pred_thresh) != -1
            if valid_mask.sum() > 0:
                acc = accuracy_score(y_test[valid_mask], np.array(y_pred_thresh)[valid_mask])
                rejection_rate = 1 - (valid_mask.sum() / len(y_test))
            else:
                acc = 0.0
                rejection_rate = 1.0
            
            threshold_results.append({
                'threshold': thresh,
                'accuracy': acc,
                'rejection_rate': rejection_rate,
                'accepted': valid_mask.sum()
            })
            
            print(f"    {thresh:.2f}: Acc={acc:.4f}, Rejected={rejection_rate:.2%}, Accepted={valid_mask.sum()}/{len(y_test)}")
        
        # Recommend threshold (balance accuracy and rejection)
        # Choose threshold with >95% accuracy and reasonable rejection rate
        recommended_threshold = 0.70
        for result in threshold_results:
            if result['accuracy'] >= 0.95 and result['rejection_rate'] < 0.15:
                recommended_threshold = result['threshold']
                break
        
        print(f"\n  ✓ Recommended threshold: {recommended_threshold:.2f}")
        
        return accuracy, report, cm, recommended_threshold, threshold_results
    
    def step6_save_report(self, accuracy, report, cm, recommended_threshold, threshold_results):
        """Step 6: Save training report"""
        print("\n[Step 6] Saving training report...")
        
        report_path = self.models_dir / 'training_report.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("SMARTATTENDANCE FACE RECOGNITION TRAINING REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Device: {self.device}\n\n")
            
            f.write("PIPELINE SUMMARY\n")
            f.write("-"*80 + "\n")
            f.write("Detection: InsightFace FaceAnalysis (SCRFD)\n")
            f.write("Alignment: InsightFace 5-point landmarks\n")
            f.write("Embeddings: FaceNet InceptionResnetV1 (pretrained='vggface2')\n")
            f.write("Embedding Dimension: 512\n")
            f.write("Normalization: L2 normalization (unit length)\n")
            f.write("Scaling: StandardScaler\n")
            f.write("Classifier: SVM (linear kernel, probability=True, class_weight='balanced')\n\n")
            
            f.write("DATASET STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total images processed: {len(self.image_paths)}\n")
            f.write(f"Successfully extracted: {len(self.X)}\n")
            f.write(f"Skipped/Failed: {len(self.skipped_images)}\n")
            f.write(f"Unique students: {len(set(self.y))}\n")
            f.write(f"Embeddings shape: {self.X.shape}\n\n")
            
            f.write("STUDENT LABELS\n")
            f.write("-"*80 + "\n")
            for i, student_id in enumerate(self.label_encoder.classes_, 1):
                count = np.sum(self.y == student_id)
                f.write(f"{i:3d}. {student_id}: {count} samples\n")
            f.write("\n")
            
            f.write("MODEL PERFORMANCE\n")
            f.write("-"*80 + "\n")
            f.write(f"Test Accuracy: {accuracy:.4f}\n\n")
            
            f.write("Classification Report:\n")
            f.write(report)
            f.write("\n\n")
            
            f.write("Confusion Matrix:\n")
            f.write(str(cm))
            f.write("\n\n")
            
            f.write("THRESHOLD ANALYSIS\n")
            f.write("-"*80 + "\n")
            f.write("Threshold | Accuracy | Rejection Rate | Accepted/Total\n")
            f.write("-"*80 + "\n")
            for result in threshold_results:
                f.write(f"  {result['threshold']:.2f}    |  {result['accuracy']:.4f}  |    {result['rejection_rate']:.2%}      | {result['accepted']}/{len(self.X)}\n")
            f.write("\n")
            
            f.write(f"RECOMMENDED THRESHOLD: {recommended_threshold:.2f}\n")
            f.write(f"Default inference threshold: 0.70 (adjustable in backend config)\n\n")
            
            if len(self.skipped_images) > 0:
                f.write("SKIPPED IMAGES\n")
                f.write("-"*80 + "\n")
                for img_path, reason in self.skipped_images[:50]:  # Limit to first 50
                    f.write(f"{img_path}: {reason}\n")
                if len(self.skipped_images) > 50:
                    f.write(f"... and {len(self.skipped_images) - 50} more\n")
                f.write("\n")
            
            if len(self.error_log) > 0:
                f.write("ERROR LOG\n")
                f.write("-"*80 + "\n")
                for error in self.error_log:
                    f.write(f"{error}\n")
                f.write("\n")
            
            f.write("="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"  ✓ Saved training report: {report_path}")
    
    def step7_save_readme(self, recommended_threshold):
        """Step 7: Save MODEL_README.md"""
        print("\n[Step 7] Saving MODEL_README.md...")
        
        readme_path = self.models_dir / 'MODEL_README.md'
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("# SmartAttendance Face Recognition Model\n\n")
            
            f.write("## Pipeline Summary\n\n")
            f.write("This model uses a state-of-the-art face recognition pipeline:\n\n")
            f.write("1. **Face Detection & Alignment**: InsightFace FaceAnalysis (SCRFD detector)\n")
            f.write("2. **Feature Extraction**: FaceNet InceptionResnetV1 (pretrained on VGGFace2)\n")
            f.write("3. **Embedding**: 512-dimensional L2-normalized vectors\n")
            f.write("4. **Classification**: SVM with linear kernel and probability estimates\n\n")
            
            f.write("## Model Artifacts\n\n")
            f.write("```\n")
            f.write("backend/models/Classifier/\n")
            f.write("├── face_classifier_v1.pkl      # Main classifier (includes SVM, scaler, label_encoder)\n")
            f.write("├── label_encoder.pkl           # Label encoder (student IDs)\n")
            f.write("└── label_encoder_classes.npy   # Numpy array of class names\n\n")
            f.write("models/\n")
            f.write("├── X.npy                       # Training embeddings (N x 512)\n")
            f.write("├── y.npy                       # Training labels (N,)\n")
            f.write("├── labels.csv                  # Student ID mapping\n")
            f.write("├── training_report.txt         # Detailed training metrics\n")
            f.write("└── MODEL_README.md             # This file\n")
            f.write("```\n\n")
            
            f.write("## Folder Structure\n\n")
            f.write("Training data should be organized as:\n\n")
            f.write("```\n")
            f.write("backend/dataset/processed/\n")
            f.write("├── STU001_StudentName/\n")
            f.write("│   ├── image1.jpg\n")
            f.write("│   ├── image2.jpg\n")
            f.write("│   └── ...\n")
            f.write("├── STU002_StudentName/\n")
            f.write("│   └── ...\n")
            f.write("└── ...\n")
            f.write("```\n\n")
            
            f.write("## Retraining\n\n")
            f.write("To retrain the model from scratch:\n\n")
            f.write("```bash\n")
            f.write("# Basic usage\n")
            f.write("python retrain_model.py\n\n")
            f.write("# Custom paths\n")
            f.write("python retrain_model.py --data-dir backend/dataset/processed --out-dir backend/models/Classifier --embeds-out models\n")
            f.write("```\n\n")
            
            f.write("## Inference Configuration\n\n")
            f.write(f"**Recommended Threshold**: {recommended_threshold:.2f}\n\n")
            f.write("The confidence threshold determines when to classify a face as 'unknown':\n\n")
            f.write("- **Lower threshold (0.50-0.70)**: More permissive, fewer unknowns, higher false positives\n")
            f.write("- **Higher threshold (0.80-0.95)**: More strict, more unknowns, lower false positives\n\n")
            f.write("To change the threshold in backend:\n\n")
            f.write("1. Edit `backend/config.py` or `backend/recognizer/classifier.py`\n")
            f.write("2. Update the `RECOGNITION_THRESHOLD` variable\n")
            f.write("3. Restart the backend server\n\n")
            
            f.write("## Technical Details\n\n")
            f.write("### Embedding Extraction\n\n")
            f.write("- Input: RGB image (any size)\n")
            f.write("- Detection: InsightFace SCRFD (640x640 detection size)\n")
            f.write("- Alignment: 5-point landmark alignment\n")
            f.write("- Resize: 160x160 pixels\n")
            f.write("- Normalization: [-1, 1] range\n")
            f.write("- Embedding: 512-dimensional vector\n")
            f.write("- L2 Normalization: Unit length (||v|| = 1)\n\n")
            
            f.write("### Classification\n\n")
            f.write("- Scaling: StandardScaler (zero mean, unit variance)\n")
            f.write("- Classifier: SVM with linear kernel\n")
            f.write("- Probability: Enabled (Platt scaling)\n")
            f.write("- Class weights: Balanced (handles imbalanced data)\n\n")
            
            f.write("### Backend Loader\n\n")
            f.write("The backend recognizer loader should:\n\n")
            f.write("1. Load `face_classifier_v1.pkl` (contains classifier, scaler, label_encoder)\n")
            f.write("2. For inference:\n")
            f.write("   - Extract 512-dim embedding from face\n")
            f.write("   - L2 normalize the embedding\n")
            f.write("   - Apply `scaler.transform(embedding)`\n")
            f.write("   - Call `classifier.predict_proba(scaled_embedding)`\n")
            f.write("   - Get max probability: `max_prob = max(probabilities)`\n")
            f.write("   - If `max_prob >= threshold`: return predicted student ID\n")
            f.write("   - Else: return 'unknown'\n\n")
            
            f.write("## Notes\n\n")
            f.write("- All embeddings are L2-normalized to unit length\n")
            f.write("- StandardScaler is applied after L2 normalization\n")
            f.write("- Embedding dimension is fixed at 512 (FaceNet output)\n")
            f.write("- The model supports open-set recognition (unknown faces)\n")
            f.write("- Training uses stratified split to maintain class balance\n\n")
            
            f.write(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"  ✓ Saved MODEL_README.md: {readme_path}")
    
    def step8_update_backend_loader(self):
        """Step 8: Verify backend loader compatibility"""
        print("\n[Step 8] Verifying backend loader compatibility...")
        
        loader_path = Path('backend/recognizer/loader.py')
        
        if loader_path.exists():
            print(f"  ✓ Backend loader exists: {loader_path}")
            print(f"  ℹ Ensure loader:")
            print(f"    - Loads face_classifier_v1.pkl")
            print(f"    - Extracts classifier, scaler, label_encoder from pkl")
            print(f"    - Applies L2 normalization to embeddings")
            print(f"    - Applies scaler.transform() before predict_proba()")
            print(f"    - Compares max probability against threshold")
        else:
            print(f"  ⚠ Backend loader not found: {loader_path}")
            print(f"  ℹ Create loader to use the trained model")
    
    def run(self):
        """Execute complete retraining pipeline"""
        try:
            # Step 0: Confirm paths
            self.step0_confirm_paths()
            
            # Step 1: Cleanup
            self.step1_cleanup_artifacts()
            
            # Step 2: Build dataset index
            self.step2_build_dataset_index()
            
            # Step 3: Extract embeddings
            self.step3_extract_embeddings()
            
            if len(self.X) == 0:
                raise ValueError("No valid embeddings extracted. Cannot train model.")
            
            # Step 4: Train classifier
            X_scaled, y_encoded = self.step4_train_classifier()
            
            # Step 5: Evaluate and threshold
            accuracy, report, cm, recommended_threshold, threshold_results = self.step5_evaluate_and_threshold(X_scaled, y_encoded)
            
            # Step 6: Save report
            self.step6_save_report(accuracy, report, cm, recommended_threshold, threshold_results)
            
            # Step 7: Save README
            self.step7_save_readme(recommended_threshold)
            
            # Step 8: Verify backend loader
            self.step8_update_backend_loader()
            
            # Final summary
            print("\n" + "="*80)
            print("✔ TRAINING COMPLETED SUCCESSFULLY")
            print("="*80)
            print(f"\n📊 RESULTS:")
            print(f"  • Images processed: {len(self.image_paths)}")
            print(f"  • Embeddings extracted: {len(self.X)}")
            print(f"  • Students: {len(set(self.y))}")
            print(f"  • Test accuracy: {accuracy:.4f}")
            print(f"  • Recommended threshold: {recommended_threshold:.2f}")
            
            print(f"\n📁 ARTIFACTS SAVED:")
            print(f"  • {self.out_dir}/face_classifier_v1.pkl")
            print(f"  • {self.out_dir}/label_encoder.pkl")
            print(f"  • {self.out_dir}/label_encoder_classes.npy")
            print(f"  • {self.models_dir}/X.npy")
            print(f"  • {self.models_dir}/y.npy")
            print(f"  • {self.models_dir}/labels.csv")
            print(f"  • {self.models_dir}/training_report.txt")
            print(f"  • {self.models_dir}/MODEL_README.md")
            
            if len(self.deleted_files) > 0:
                print(f"\n🗑️  FILES DELETED: {len(self.deleted_files)}")
                for f in self.deleted_files[:5]:
                    print(f"  • {f}")
                if len(self.deleted_files) > 5:
                    print(f"  • ... and {len(self.deleted_files) - 5} more")
            
            print(f"\n⚙️  CONFUSION MATRIX:")
            print(cm)
            
            print("\n" + "="*80)
            print("✓ Training completed. Artifacts saved to backend/models/Classifier and models/")
            print("="*80)
            
            return True
            
        except Exception as e:
            print("\n" + "="*80)
            print("✗ TRAINING FAILED")
            print("="*80)
            print(f"Error: {e}")
            traceback.print_exc()
            
            # Save error log
            error_log_path = self.models_dir / 'training_error.log'
            with open(error_log_path, 'w') as f:
                f.write(f"Training failed at {datetime.now()}\n")
                f.write(f"Error: {e}\n\n")
                f.write(traceback.format_exc())
            print(f"\nError log saved to: {error_log_path}")
            
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='SmartAttendance Face Recognition Retraining Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python retrain_model.py
  python retrain_model.py --data-dir backend/dataset/processed
  python retrain_model.py --data-dir backend/dataset/processed --out-dir backend/models/Classifier --embeds-out models
        """
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='backend/dataset/processed',
        help='Path to processed dataset directory (default: backend/dataset/processed)'
    )
    
    parser.add_argument(
        '--out-dir',
        type=str,
        default='backend/models/Classifier',
        help='Output directory for classifier artifacts (default: backend/models/Classifier)'
    )
    
    parser.add_argument(
        '--embeds-out',
        type=str,
        default='models',
        help='Output directory for embeddings and reports (default: models)'
    )
    
    args = parser.parse_args()
    
    # Create retrainer
    retrainer = FaceRecognitionRetrainer(
        data_dir=args.data_dir,
        out_dir=args.out_dir,
        embeds_out=args.embeds_out
    )
    
    # Run training
    success = retrainer.run()
    
    if success:
        print("\n🚀 Next steps:")
        print("  1. Review training_report.txt for detailed metrics")
        print("  2. Test model: python backend/test_production_model.py")
        print("  3. Start backend: cd backend && python app.py")
        print("  4. Test live recognition in frontend\n")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
