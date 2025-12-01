"""
Train from scratch: MTCNN -> InceptionResnetV1 (facenet_pytorch) -> classifier

This script:
- Walks the dataset at `uploads/faces/{student_id}/*.jpg`
- Detects and crops the largest face using MTCNN
- Extracts 512-d embeddings using InceptionResnetV1(pretrained='vggface2')
- Trains a classifier (SVM by default, or LogisticRegression)
- Computes a recommended open-set threshold from validation probabilities
- Saves artifacts to `backend/models/Classifier/`:
  - face_classifier_v1.pkl
  - label_encoder.pkl
  - label_encoder_classes.npy
  - X.npy, y.npy

Usage (from repo root):
    python backend/train_from_scratch.py --dataset uploads/faces --model-dir backend/models/Classifier \
        --classifier svm --threshold 0.6

Notes:
- Requires facenet-pytorch and torch. On Windows, install a matching torch wheel for your CUDA/Python.
  pip install facenet-pytorch torch torchvision

"""

import os
import sys
import argparse
import pickle
from pathlib import Path
from typing import List, Tuple

import numpy as np

try:
    from PIL import Image
    import torch
    from facenet_pytorch import MTCNN, InceptionResnetV1
except Exception as e:
    print("❌ Missing required packages: facenet-pytorch and torch are required.")
    print("   Install with: pip install facenet-pytorch torch torchvision")
    raise

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression


def find_image_files(dataset_dir: Path) -> List[Tuple[str, Path]]:
    """Return list of tuples (student_id, image_path)"""
    pairs = []
    for student_dir in sorted(dataset_dir.iterdir()):
        if not student_dir.is_dir():
            continue
        student_id = student_dir.name
        for p in student_dir.iterdir():
            if p.suffix.lower() in ['.jpg', '.jpeg', '.png'] and p.is_file():
                pairs.append((student_id, p))
    return pairs


def extract_embedding(mtcnn: MTCNN, resnet: InceptionResnetV1, img_path: Path, device: torch.device):
    try:
        img = Image.open(img_path).convert('RGB')
    except Exception as e:
        print(f"   ⚠️  Could not open image {img_path}: {e}")
        return None

    # mtcnn with keep_all=False returns the largest face or None
    face_tensor = mtcnn(img)
    if face_tensor is None:
        return None

    # Ensure batch dim
    if face_tensor.ndim == 3:
        face_tensor = face_tensor.unsqueeze(0)

    face_tensor = face_tensor.to(device)
    with torch.no_grad():
        embedding = resnet(face_tensor)
    embedding = embedding.cpu().numpy().reshape(-1)
    return embedding


def main(argv=None):
    parser = argparse.ArgumentParser(description='Train face recognition model from scratch')
    parser.add_argument('--dataset', type=str, default='uploads/faces', help='Path to dataset root (student folders)')
    parser.add_argument('--model-dir', type=str, default='backend/models/Classifier', help='Directory to save artifacts')
    parser.add_argument('--classifier', choices=['svm', 'logreg'], default='svm', help='Classifier type')
    parser.add_argument('--test-size', type=float, default=0.2, help='Validation split fraction')
    parser.add_argument('--threshold', type=float, default=None, help='Open-set threshold (probability). If omitted, a recommended threshold will be printed')
    parser.add_argument('--device', type=str, default=None, help='Torch device: cpu or cuda (auto by default)')
    args = parser.parse_args(argv)

    dataset_dir = Path(args.dataset)
    model_dir = Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    if not dataset_dir.exists():
        print(f"❌ Dataset not found: {dataset_dir}")
        sys.exit(2)

    # Device
    if args.device:
        device = torch.device(args.device)
    else:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    print(f"Using device: {device}")

    # Create detectors/embedders
    mtcnn = MTCNN(image_size=160, margin=0, min_face_size=20, keep_all=False, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

    # Walk dataset
    pairs = find_image_files(dataset_dir)
    if len(pairs) == 0:
        print("❌ No images found in dataset. Ensure structure: uploads/faces/STU001/*.jpg")
        sys.exit(2)

    print(f"📁 Found {len(pairs)} images across student folders")

    X = []
    y = []
    skipped = 0
    for student_id, img_path in pairs:
        embedding = extract_embedding(mtcnn, resnet, img_path, device)
        if embedding is None:
            skipped += 1
            continue
        X.append(embedding)
        y.append(student_id)
        if len(X) % 50 == 0:
            print(f"   · {len(X)} embeddings extracted so far...")

    print()
    print(f"🔍 Extraction complete. Total embeddings: {len(X)}. Skipped: {skipped}")
    if len(X) < 2:
        print("❌ Not enough embeddings to train (need >=2)")
        sys.exit(3)

    X = np.stack(X)
    y = np.array(y)

    print(f"   X shape: {X.shape}")
    print(f"   y shape: {y.shape}")

    # L2-normalize embeddings (FaceNet standard) so training and inference
    # are consistent. This produces unit-length vectors which work well with
    # cosine similarity and with classifiers trained on normalized embeddings.
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    X = X / norms

    # Save raw embeddings/dataset
    np.save(model_dir / 'X.npy', X)
    np.save(model_dir / 'y.npy', y)
    print(f"💾 Saved X.npy and y.npy to {model_dir} (embeddings L2-normalized)")

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    print(f"✅ Found {len(le.classes_)} classes: {le.classes_}")

    # Train/validation split
    if len(X) >= 10 and args.test_size > 0:
        X_train, X_val, y_train, y_val = train_test_split(X, y_enc, test_size=args.test_size, random_state=42, stratify=y_enc)
        print(f"✅ Data split: train={len(X_train)} val={len(X_val)}")
        has_val = True
    else:
        X_train, y_train = X, y_enc
        X_val, y_val = None, None
        has_val = False
        print(f"⚠️  Not enough data for validation split; using all samples for training")

    # Choose classifier
    if args.classifier == 'svm':
        clf = SVC(kernel='rbf', probability=True, gamma='scale', C=1.0, random_state=42)
    else:
        clf = LogisticRegression(max_iter=1000, multi_class='multinomial')

    print(f"🤖 Training classifier: {type(clf).__name__}")
    clf.fit(X_train, y_train)

    # Evaluate
    y_train_pred = clf.predict(X_train)
    train_acc = accuracy_score(y_train, y_train_pred)
    print(f"📊 Training accuracy: {train_acc:.2%}")
    if has_val:
        y_val_pred = clf.predict(X_val)
        val_acc = accuracy_score(y_val, y_val_pred)
        print(f"📊 Validation accuracy: {val_acc:.2%}")
        print(classification_report(y_val, y_val_pred, target_names=le.classes_))

    # Compute recommended open-set threshold from validation set probabilities (if available)
    recommended_threshold = None
    if has_val:
        probs = clf.predict_proba(X_val)
        max_probs = probs.max(axis=1)
        # Use a robust statistic instead of min(): take the 5th percentile of
        # the per-sample max-probabilities on the validation set. This avoids
        # a single outlier forcing an unrealistically high threshold.
        recommended_threshold = float(np.percentile(max_probs, 5))
        print(f"🔎 Recommended open-set threshold (5th percentile of val max-probs): {recommended_threshold:.4f}")
        mean_mp = float(max_probs.mean())
        std_mp = float(max_probs.std())
        print(f"   mean: {mean_mp:.4f}, std: {std_mp:.4f}")
    if args.threshold is not None:
        threshold = float(args.threshold)
    elif recommended_threshold is not None:
        threshold = recommended_threshold
    else:
        threshold = 0.6

    print(f"🎯 Using open-set threshold = {threshold:.4f}")

    # Save artifacts
    classifier_path = model_dir / 'face_classifier_v1.pkl'
    encoder_path = model_dir / 'label_encoder.pkl'
    classes_path = model_dir / 'label_encoder_classes.npy'
    threshold_path = model_dir / 'open_set_threshold.txt'

    # Save model as a dict with metadata so loader can pick it up reliably
    model_package = {
        'classifier': clf,
        'label_encoder': le,
        'metadata': {
            'embedding_dim': X.shape[1],
            'threshold': threshold,
            'num_classes': len(le.classes_),
            'normalize_embeddings': True,
        }
    }

    with open(classifier_path, 'wb') as f:
        pickle.dump(model_package, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Still save label encoder and classes for backward compatibility
    with open(encoder_path, 'wb') as f:
        pickle.dump(le, f, protocol=pickle.HIGHEST_PROTOCOL)
    np.save(classes_path, le.classes_)
    with open(threshold_path, 'w') as f:
        f.write(str(threshold))

    print(f"💾 Saved classifier to {classifier_path}")
    print(f"💾 Saved label encoder to {encoder_path}")
    print(f"💾 Saved label classes to {classes_path}")
    print(f"💾 Saved open-set threshold to {threshold_path}")

    print('\n✅ Training complete. Artifacts are ready to be used by the backend.')
    print('Next steps:')
    print(' 1. Restart the backend: python backend/app.py')
    print(' 2. Test model status: GET /api/debug/model-status')


if __name__ == '__main__':
    main()
