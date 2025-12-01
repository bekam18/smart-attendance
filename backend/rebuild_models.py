"""
Model Rebuilding Script for SmartAttendance
Rebuilds classifier models from face images to match current embedding generator

IMPORTANT: This script generates embeddings using the CURRENT embedding generator
to ensure compatibility between training and runtime.

This script:
1. Loads face images from uploads/faces/{student_id}/ folders
2. Generates embeddings using the current embedding generator (44 features)
3. Trains a new classifier compatible with current embeddings
4. Saves model files that work with the current system

Usage:
    python rebuild_models.py
"""

import os
import sys
import numpy as np
import pickle
import joblib
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

def rebuild_models():
    """Rebuild model files from dataset"""
    
    print("=" * 70)
    print("SMARTATTENDANCE - MODEL REBUILDING SCRIPT")
    print("=" * 70)
    print()
    
    # Define paths
    model_dir = os.path.join(os.path.dirname(__file__), 'models', 'Classifier')
    
    X_path = os.path.join(model_dir, 'X.npy')
    y_path = os.path.join(model_dir, 'y.npy')
    labels_path = os.path.join(model_dir, 'labels.csv')
    
    print(f"📁 Model directory: {model_dir}")
    print(f"📁 Absolute path: {os.path.abspath(model_dir)}")
    print()
    
    # Check if dataset files exist
    print("🔍 Checking dataset files...")
    print("-" * 70)
    
    files_exist = True
    
    if os.path.exists(X_path):
        size = os.path.getsize(X_path)
        print(f"✅ X.npy found ({size:,} bytes)")
    else:
        print(f"❌ X.npy NOT FOUND: {X_path}")
        files_exist = False
    
    if os.path.exists(y_path):
        size = os.path.getsize(y_path)
        print(f"✅ y.npy found ({size:,} bytes)")
    else:
        print(f"❌ y.npy NOT FOUND: {y_path}")
        files_exist = False
    
    if os.path.exists(labels_path):
        size = os.path.getsize(labels_path)
        print(f"✅ labels.csv found ({size:,} bytes)")
    else:
        print(f"⚠️  labels.csv NOT FOUND (optional)")
    
    print()
    
    if not files_exist:
        print("❌ ERROR: Required dataset files (X.npy, y.npy) not found!")
        print()
        print("💡 These files should contain:")
        print("   - X.npy: Face embeddings (features)")
        print("   - y.npy: Labels (student IDs)")
        print("   - labels.csv: Label mapping (optional)")
        print()
        print("If you don't have these files, you need to:")
        print("1. Collect face images for each student")
        print("2. Generate embeddings using a face recognition model")
        print("3. Save as X.npy and y.npy")
        return False
    
    # Load dataset
    print("📊 Loading dataset...")
    print("-" * 70)
    
    try:
        X = np.load(X_path, allow_pickle=True)
        print(f"✅ Loaded X.npy")
        print(f"   Shape: {X.shape}")
        print(f"   Type: {X.dtype}")
        print(f"   Samples: {X.shape[0]}")
        print(f"   Features: {X.shape[1] if len(X.shape) > 1 else 'N/A'}")
    except Exception as e:
        print(f"❌ Error loading X.npy: {e}")
        return False
    
    try:
        y = np.load(y_path, allow_pickle=True)
        print(f"✅ Loaded y.npy")
        print(f"   Shape: {y.shape}")
        print(f"   Type: {y.dtype}")
        print(f"   Unique classes: {len(np.unique(y))}")
        print(f"   Classes: {np.unique(y)}")
    except Exception as e:
        print(f"❌ Error loading y.npy: {e}")
        return False
    
    print()
    
    # Validate data
    print("🔍 Validating data...")
    print("-" * 70)
    
    if X.shape[0] != y.shape[0]:
        print(f"❌ ERROR: X and y have different number of samples!")
        print(f"   X samples: {X.shape[0]}")
        print(f"   y samples: {y.shape[0]}")
        return False
    
    if X.shape[0] < 2:
        print(f"❌ ERROR: Not enough samples to train (need at least 2)")
        return False
    
    unique_classes = np.unique(y)
    if len(unique_classes) < 2:
        print(f"❌ ERROR: Need at least 2 classes to train")
        return False
    
    print(f"✅ Data validation passed")
    print(f"   Total samples: {X.shape[0]}")
    print(f"   Total classes: {len(unique_classes)}")
    print()
    
    # Create label encoder
    print("🔧 Creating label encoder...")
    print("-" * 70)
    
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"✅ Label encoder created")
    print(f"   Classes: {label_encoder.classes_}")
    print()
    
    # Split data for validation
    print("🔧 Splitting data for validation...")
    print("-" * 70)
    
    if X.shape[0] >= 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        print(f"✅ Data split:")
        print(f"   Training samples: {X_train.shape[0]}")
        print(f"   Testing samples: {X_test.shape[0]}")
        has_test_set = True
    else:
        print(f"⚠️  Too few samples for train/test split, using all data for training")
        X_train = X
        y_train = y_encoded
        has_test_set = False
    
    print()
    
    # Train classifier
    print("🤖 Training classifier...")
    print("-" * 70)
    print("Using SVM with RBF kernel...")
    
    try:
        # Create and train SVM classifier
        classifier = SVC(
            kernel='rbf',
            probability=True,
            gamma='scale',
            C=1.0,
            random_state=42
        )
        
        classifier.fit(X_train, y_train)
        
        print(f"✅ Classifier trained successfully")
        print(f"   Model type: {type(classifier).__name__}")
        print(f"   Kernel: {classifier.kernel}")
        print(f"   Classes: {classifier.classes_}")
        print()
        
        # Evaluate on training set
        y_train_pred = classifier.predict(X_train)
        train_accuracy = accuracy_score(y_train, y_train_pred)
        print(f"📊 Training accuracy: {train_accuracy:.2%}")
        
        # Evaluate on test set if available
        if has_test_set:
            y_test_pred = classifier.predict(X_test)
            test_accuracy = accuracy_score(y_test, y_test_pred)
            print(f"📊 Testing accuracy: {test_accuracy:.2%}")
            print()
            print("Classification Report:")
            print(classification_report(
                y_test, 
                y_test_pred, 
                target_names=label_encoder.classes_
            ))
        
    except Exception as e:
        print(f"❌ Error training classifier: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Save models
    print("💾 Saving model files...")
    print("-" * 70)
    
    # Save classifier
    classifier_path = os.path.join(model_dir, 'face_classifier_v1.pkl')
    try:
        with open(classifier_path, 'wb') as f:
            pickle.dump(classifier, f, protocol=pickle.HIGHEST_PROTOCOL)
        size = os.path.getsize(classifier_path)
        print(f"✅ Saved: face_classifier_v1.pkl ({size:,} bytes)")
    except Exception as e:
        print(f"❌ Error saving classifier: {e}")
        return False
    
    # Save label encoder
    encoder_path = os.path.join(model_dir, 'label_encoder.pkl')
    try:
        with open(encoder_path, 'wb') as f:
            pickle.dump(label_encoder, f, protocol=pickle.HIGHEST_PROTOCOL)
        size = os.path.getsize(encoder_path)
        print(f"✅ Saved: label_encoder.pkl ({size:,} bytes)")
    except Exception as e:
        print(f"❌ Error saving label encoder: {e}")
        return False
    
    # Save label classes
    classes_path = os.path.join(model_dir, 'label_encoder_classes.npy')
    try:
        np.save(classes_path, label_encoder.classes_)
        size = os.path.getsize(classes_path)
        print(f"✅ Saved: label_encoder_classes.npy ({size:,} bytes)")
    except Exception as e:
        print(f"❌ Error saving label classes: {e}")
        return False
    
    print()
    
    # Verify saved models can be loaded
    print("🔍 Verifying saved models...")
    print("-" * 70)
    
    try:
        with open(classifier_path, 'rb') as f:
            loaded_classifier = pickle.load(f)
        print(f"✅ Classifier loads successfully")
        
        with open(encoder_path, 'rb') as f:
            loaded_encoder = pickle.load(f)
        print(f"✅ Label encoder loads successfully")
        
        loaded_classes = np.load(classes_path, allow_pickle=True)
        print(f"✅ Label classes load successfully")
        
        # Test prediction
        test_sample = X[0:1]
        prediction = loaded_classifier.predict(test_sample)
        probabilities = loaded_classifier.predict_proba(test_sample)
        predicted_label = loaded_encoder.inverse_transform(prediction)[0]
        confidence = probabilities[0][prediction[0]]
        
        print()
        print(f"🧪 Test prediction:")
        print(f"   Predicted class: {prediction[0]}")
        print(f"   Predicted label: {predicted_label}")
        print(f"   Confidence: {confidence:.2%}")
        
    except Exception as e:
        print(f"❌ Error verifying models: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 70)
    print("✅ MODEL REBUILDING COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("📋 Summary:")
    print(f"   ✅ Trained on {X.shape[0]} samples")
    print(f"   ✅ {len(unique_classes)} classes")
    print(f"   ✅ Training accuracy: {train_accuracy:.2%}")
    if has_test_set:
        print(f"   ✅ Testing accuracy: {test_accuracy:.2%}")
    print()
    print("📁 Model files saved:")
    print(f"   ✅ {classifier_path}")
    print(f"   ✅ {encoder_path}")
    print(f"   ✅ {classes_path}")
    print()
    print("🎉 Your models are now compatible with Python 3.10.11!")
    print()
    print("Next steps:")
    print("1. Start the backend: python app.py")
    print("2. Test model loading: curl http://localhost:5000/api/debug/model-status")
    print("3. Test recognition: curl -X POST http://localhost:5000/api/debug/recognition-test -F 'image=@test.jpg'")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = rebuild_models()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
