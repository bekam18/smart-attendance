"""
Diagnostic script to check why trained students are recognized as unknown
Tests the complete recognition pipeline
"""

import sys
import os
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("="*80)
print("RECOGNITION DIAGNOSTIC TOOL")
print("="*80)

# Test 1: Load model
print("\n[Test 1] Loading model...")
try:
    from recognizer.loader import model_loader
    
    success = model_loader.load_models()
    if not success:
        print("❌ Model loading failed")
        sys.exit(1)
    
    classifier = model_loader.get_classifier()
    scaler = model_loader.get_scaler()
    label_encoder = model_loader.get_label_encoder()
    classes = model_loader.get_classes()
    metadata = model_loader.get_metadata()
    
    print(f"✅ Model loaded")
    print(f"  Classifier type: {type(classifier).__name__}")
    print(f"  Scaler: {type(scaler).__name__ if scaler else 'None'}")
    print(f"  Label encoder: {type(label_encoder).__name__ if label_encoder else 'None'}")
    print(f"  Classes: {len(classes)} students")
    print(f"  Metadata: {metadata}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Load embedding generator
print("\n[Test 2] Loading embedding generator...")
try:
    from recognizer.embeddings_facenet import embedding_generator
    
    if not embedding_generator.is_available():
        print("❌ FaceNet not available")
        sys.exit(1)
    
    print("✅ FaceNet available")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test with training image
print("\n[Test 3] Testing with training image...")
try:
    import cv2
    
    # Find a training image
    dataset_path = Path('backend/dataset/processed')
    if not dataset_path.exists():
        print(f"❌ Dataset not found: {dataset_path}")
        sys.exit(1)
    
    # Get first student folder
    student_folders = sorted([d for d in dataset_path.iterdir() if d.is_dir()])
    if len(student_folders) == 0:
        print("❌ No student folders found")
        sys.exit(1)
    
    first_student = student_folders[0]
    student_id = first_student.name.split('_')[0]
    
    # Get first image
    images = list(first_student.glob('*.jpg')) + list(first_student.glob('*.png'))
    if len(images) == 0:
        print(f"❌ No images found in {first_student}")
        sys.exit(1)
    
    test_image_path = images[0]
    print(f"  Testing with: {test_image_path}")
    print(f"  Expected student: {student_id}")
    
    # Load image
    img = cv2.imread(str(test_image_path))
    if img is None:
        print(f"❌ Failed to load image")
        sys.exit(1)
    
    print(f"  Image shape: {img.shape}")
    
    # Generate embedding
    print("  Generating embedding...")
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Generate embedding (this will resize to 160x160 internally)
    embedding = embedding_generator.generate_embedding(img_rgb)
    
    print(f"  ✅ Embedding generated: shape {embedding.shape}")
    print(f"  Embedding norm: {np.linalg.norm(embedding):.6f}")
    print(f"  Embedding min: {embedding.min():.6f}")
    print(f"  Embedding max: {embedding.max():.6f}")
    print(f"  Embedding mean: {embedding.mean():.6f}")
    print(f"  Embedding std: {embedding.std():.6f}")
    
    # Reshape for prediction
    embedding_reshaped = embedding.reshape(1, -1)
    
    # Apply scaler if available
    if scaler is not None:
        print("  Applying scaler...")
        embedding_scaled = scaler.transform(embedding_reshaped)
        print(f"  ✅ Scaled embedding")
        print(f"  Scaled min: {embedding_scaled.min():.6f}")
        print(f"  Scaled max: {embedding_scaled.max():.6f}")
        print(f"  Scaled mean: {embedding_scaled.mean():.6f}")
        print(f"  Scaled std: {embedding_scaled.std():.6f}")
    else:
        embedding_scaled = embedding_reshaped
        print("  ⚠ No scaler available")
    
    # Predict
    print("  Predicting...")
    probabilities = classifier.predict_proba(embedding_scaled)[0]
    max_prob_idx = np.argmax(probabilities)
    confidence = probabilities[max_prob_idx]
    
    # Get predicted label
    if label_encoder:
        predicted_label = label_encoder.inverse_transform([max_prob_idx])[0]
    elif classes is not None:
        predicted_label = classes[max_prob_idx]
    else:
        predicted_label = f"CLASS_{max_prob_idx}"
    
    print(f"\n  RESULTS:")
    print(f"  Expected: {student_id}")
    print(f"  Predicted: {predicted_label}")
    print(f"  Confidence: {confidence:.4f}")
    print(f"  Match: {'✅ CORRECT' if predicted_label == student_id else '❌ WRONG'}")
    
    # Show top 5 predictions
    print(f"\n  Top 5 predictions:")
    top_5_indices = np.argsort(probabilities)[-5:][::-1]
    for i, idx in enumerate(top_5_indices, 1):
        prob = probabilities[idx]
        if label_encoder:
            label = label_encoder.inverse_transform([idx])[0]
        elif classes is not None:
            label = classes[idx]
        else:
            label = f"CLASS_{idx}"
        print(f"    {i}. {label}: {prob:.4f}")
    
    # Check threshold
    threshold = 0.60
    print(f"\n  Threshold check (0.60):")
    if confidence >= threshold:
        print(f"  ✅ PASS: {confidence:.4f} >= {threshold}")
    else:
        print(f"  ❌ FAIL: {confidence:.4f} < {threshold} (would be marked as unknown)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check training embeddings
print("\n[Test 4] Checking training embeddings...")
try:
    X_path = Path('backend/models/Classifier/X.npy')
    if not X_path.exists():
        X_path = Path('models/X.npy')
    
    if X_path.exists():
        X = np.load(X_path)
        print(f"  Training embeddings shape: {X.shape}")
        
        # Check if normalized
        norms = np.linalg.norm(X, axis=1)
        print(f"  Training embedding norms:")
        print(f"    Min: {norms.min():.6f}")
        print(f"    Max: {norms.max():.6f}")
        print(f"    Mean: {norms.mean():.6f}")
        print(f"    Std: {norms.std():.6f}")
        
        if np.allclose(norms, 1.0, atol=0.01):
            print(f"  ✅ Training embeddings are L2-normalized")
        else:
            print(f"  ⚠ Training embeddings may not be L2-normalized")
    else:
        print(f"  ⚠ Training embeddings not found")
        
except Exception as e:
    print(f"  ⚠ Error checking training embeddings: {e}")

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
