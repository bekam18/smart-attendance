"""
Test script for retrained face recognition model
Verifies model loading and basic inference
"""

import os
import sys
import pickle
import numpy as np
from pathlib import Path

print("="*80)
print("Testing Retrained Model")
print("="*80)

# Check if model files exist
model_dir = Path('backend/models/Classifier')
classifier_path = model_dir / 'face_classifier_v1.pkl'
classes_path = model_dir / 'label_encoder_classes.npy'

print(f"\n[1] Checking model files...")
print(f"  Model directory: {model_dir.absolute()}")
print(f"  Classifier: {classifier_path.exists()} - {classifier_path}")
print(f"  Classes: {classes_path.exists()} - {classes_path}")

if not classifier_path.exists():
    print("\n❌ Classifier not found! Run retrain_model.py first.")
    sys.exit(1)

# Load classifier
print(f"\n[2] Loading classifier...")
try:
    with open(classifier_path, 'rb') as f:
        data = pickle.load(f)
    
    if isinstance(data, dict):
        classifier = data['classifier']
        scaler = data.get('scaler')
        label_encoder = data.get('label_encoder')
        metadata = data.get('metadata', {})
        
        print(f"  ✓ Loaded new format model")
        print(f"  Classifier type: {type(classifier).__name__}")
        print(f"  Scaler: {type(scaler).__name__ if scaler else 'None'}")
        print(f"  Label encoder: {type(label_encoder).__name__ if label_encoder else 'None'}")
        print(f"\n  Metadata:")
        for key, value in metadata.items():
            if key == 'classes':
                print(f"    {key}: {len(value)} classes")
            else:
                print(f"    {key}: {value}")
    else:
        print(f"  ⚠ Old format model (just classifier)")
        classifier = data
        scaler = None
        label_encoder = None
        metadata = {}
    
    print(f"\n  ✓ Classifier loaded successfully")
    
except Exception as e:
    print(f"\n  ❌ Error loading classifier: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Load classes
print(f"\n[3] Loading label classes...")
try:
    if classes_path.exists():
        classes = np.load(classes_path, allow_pickle=True)
        print(f"  ✓ Loaded {len(classes)} classes")
        print(f"  Classes: {classes}")
    else:
        print(f"  ⚠ Classes file not found")
        classes = None
except Exception as e:
    print(f"  ❌ Error loading classes: {e}")
    classes = None

# Test with random embedding
print(f"\n[4] Testing inference with random embedding...")
try:
    # Create random 512-dim embedding (L2 normalized)
    test_embedding = np.random.randn(1, 512)
    test_embedding = test_embedding / np.linalg.norm(test_embedding)
    
    print(f"  Test embedding shape: {test_embedding.shape}")
    print(f"  Test embedding norm: {np.linalg.norm(test_embedding):.4f}")
    
    # Apply scaler if available
    if scaler is not None:
        test_embedding_scaled = scaler.transform(test_embedding)
        print(f"  ✓ Applied StandardScaler")
    else:
        test_embedding_scaled = test_embedding
        print(f"  ⚠ No scaler available")
    
    # Predict
    prediction = classifier.predict(test_embedding_scaled)
    probabilities = classifier.predict_proba(test_embedding_scaled)
    max_prob = np.max(probabilities)
    predicted_class = prediction[0]
    
    print(f"\n  Prediction results:")
    print(f"    Predicted class index: {predicted_class}")
    if classes is not None and predicted_class < len(classes):
        print(f"    Predicted student ID: {classes[predicted_class]}")
    print(f"    Max probability: {max_prob:.4f}")
    print(f"    All probabilities shape: {probabilities.shape}")
    
    # Show top 3 predictions
    top_3_indices = np.argsort(probabilities[0])[-3:][::-1]
    print(f"\n  Top 3 predictions:")
    for i, idx in enumerate(top_3_indices, 1):
        prob = probabilities[0][idx]
        student_id = classes[idx] if classes is not None and idx < len(classes) else f"Class_{idx}"
        print(f"    {i}. {student_id}: {prob:.4f}")
    
    print(f"\n  ✓ Inference test passed")
    
except Exception as e:
    print(f"\n  ❌ Error during inference: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check embeddings
print(f"\n[5] Checking training embeddings...")
X_path = Path('models/X.npy')
y_path = Path('models/y.npy')

if X_path.exists() and y_path.exists():
    try:
        X = np.load(X_path)
        y = np.load(y_path)
        print(f"  ✓ Training embeddings: {X.shape}")
        print(f"  ✓ Training labels: {y.shape}")
        print(f"  Unique labels: {len(np.unique(y))}")
        
        # Check embedding norms
        norms = np.linalg.norm(X, axis=1)
        print(f"\n  Embedding norms:")
        print(f"    Min: {norms.min():.4f}")
        print(f"    Max: {norms.max():.4f}")
        print(f"    Mean: {norms.mean():.4f}")
        print(f"    Std: {norms.std():.4f}")
        
        if np.allclose(norms, 1.0, atol=0.01):
            print(f"  ✓ Embeddings are L2-normalized")
        else:
            print(f"  ⚠ Embeddings may not be L2-normalized")
        
    except Exception as e:
        print(f"  ❌ Error loading embeddings: {e}")
else:
    print(f"  ⚠ Training embeddings not found")

# Summary
print(f"\n" + "="*80)
print("✓ MODEL TEST COMPLETE")
print("="*80)
print(f"\nModel is ready for use!")
print(f"\nNext steps:")
print(f"  1. Start backend: cd backend && python app.py")
print(f"  2. Test live recognition in frontend")
print(f"  3. Review training_report.txt for detailed metrics")
print("="*80)
