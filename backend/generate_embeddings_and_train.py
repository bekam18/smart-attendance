"""
Generate Embeddings and Train Model
This script generates embeddings from face images using the CURRENT embedding generator
and trains a classifier that matches the runtime system.

Usage:
    python generate_embeddings_and_train.py
"""

import os
import sys
import numpy as np
import pickle
import cv2
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Import current recognizer components
from recognizer.detector import face_detector
from recognizer.embeddings import embedding_generator
from config import config

def generate_embeddings_from_images():
    """Generate embeddings from face images in uploads/faces/"""
    
    print("=" * 70)
    print("GENERATE EMBEDDINGS AND TRAIN MODEL")
    print("=" * 70)
    print()
    
    # Path to face images
    faces_dir = os.path.join(config.UPLOAD_FOLDER, 'faces')
    
    print(f"📁 Looking for face images in: {faces_dir}")
    print(f"📁 Absolute path: {os.path.abspath(faces_dir)}")
    print()
    
    if not os.path.exists(faces_dir):
        print(f"❌ Faces directory not found: {faces_dir}")
        print()
        print("💡 Please ensure face images are organized as:")
        print("   uploads/faces/STU001/image1.jpg")
        print("   uploads/faces/STU001/image2.jpg")
        print("   uploads/faces/STU002/image1.jpg")
        print("   ...")
        return False
    
    # Collect all student folders
    student_folders = [d for d in os.listdir(faces_dir) 
                      if os.path.isdir(os.path.join(faces_dir, d)) and not d.startswith('.')]
    
    if len(student_folders) == 0:
        print("❌ No student folders found!")
        print()
        print("💡 Create folders for each student:")
        print("   mkdir uploads/faces/STU001")
        print("   mkdir uploads/faces/STU002")
        print("   ...")
        print()
        print("Then add face images to each folder.")
        return False
    
    print(f"✅ Found {len(student_folders)} student folders:")
    for folder in sorted(student_folders):
        print(f"   - {folder}")
    print()
    
    # Generate embeddings
    print("🔍 Generating embeddings from face images...")
    print("-" * 70)
    
    X = []  # Embeddings
    y = []  # Labels
    
    total_images = 0
    successful_embeddings = 0
    
    for student_id in sorted(student_folders):
        student_path = os.path.join(faces_dir, student_id)
        
        # Get all image files
        image_files = [f for f in os.listdir(student_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"\n📸 Processing {student_id}: {len(image_files)} images")
        
        for img_file in image_files:
            total_images += 1
            img_path = os.path.join(student_path, img_file)
            
            try:
                # Read image
                img = cv2.imread(img_path)
                if img is None:
                    print(f"   ⚠️  Could not read: {img_file}")
                    continue
                
                # Detect face
                faces = face_detector.detect_faces(img)
                if len(faces) == 0:
                    print(f"   ⚠️  No face detected: {img_file}")
                    continue
                
                # Extract face
                face_img = face_detector.extract_face(img, faces[0])
                
                # Generate embedding using CURRENT embedding generator
                embedding = embedding_generator.generate_embedding(face_img)
                
                # Add to dataset
                X.append(embedding)
                y.append(student_id)
                successful_embeddings += 1
                
                print(f"   ✅ {img_file}: embedding shape {embedding.shape}")
                
            except Exception as e:
                print(f"   ❌ Error processing {img_file}: {e}")
    
    print()
    print("=" * 70)
    print(f"📊 Embedding Generation Summary:")
    print(f"   Total images processed: {total_images}")
    print(f"   Successful embeddings: {successful_embeddings}")
    print(f"   Failed: {total_images - successful_embeddings}")
    print("=" * 70)
    print()
    
    if successful_embeddings < 2:
        print("❌ Not enough embeddings generated (need at least 2)")
        return False
    
    # Convert to numpy arrays
    X = np.array(X)
    y = np.array(y)
    
    print(f"✅ Dataset created:")
    print(f"   X shape: {X.shape}")
    print(f"   y shape: {y.shape}")
    print(f"   Unique classes: {len(np.unique(y))}")
    print(f"   Classes: {np.unique(y)}")
    print()
    
    # Save dataset
    model_dir = config.MODEL_PATH
    os.makedirs(model_dir, exist_ok=True)
    
    X_path = os.path.join(model_dir, 'X.npy')
    y_path = os.path.join(model_dir, 'y.npy')
    
    np.save(X_path, X)
    np.save(y_path, y)
    
    print(f"💾 Saved dataset:")
    print(f"   {X_path}")
    print(f"   {y_path}")
    print()
    
    # Train model
    print("🤖 Training classifier...")
    print("-" * 70)
    
    # Create label encoder
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split data if enough samples
    if X.shape[0] >= 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        print(f"✅ Data split:")
        print(f"   Training: {X_train.shape[0]} samples")
        print(f"   Testing: {X_test.shape[0]} samples")
        has_test_set = True
    else:
        X_train = X
        y_train = y_encoded
        has_test_set = False
        print(f"⚠️  Using all {X.shape[0]} samples for training (too few for split)")
    
    print()
    
    # Train SVM
    classifier = SVC(
        kernel='rbf',
        probability=True,
        gamma='scale',
        C=1.0,
        random_state=42
    )
    
    classifier.fit(X_train, y_train)
    
    print(f"✅ Classifier trained")
    print(f"   Model: {type(classifier).__name__}")
    print(f"   Kernel: {classifier.kernel}")
    print()
    
    # Evaluate
    y_train_pred = classifier.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    print(f"📊 Training accuracy: {train_accuracy:.2%}")
    
    if has_test_set:
        y_test_pred = classifier.predict(X_test)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        print(f"📊 Testing accuracy: {test_accuracy:.2%}")
        print()
        print("Classification Report:")
        print(classification_report(y_test, y_test_pred, target_names=label_encoder.classes_))
    
    print()
    
    # Save models
    print("💾 Saving model files...")
    print("-" * 70)
    
    classifier_path = os.path.join(model_dir, 'face_classifier_v1.pkl')
    encoder_path = os.path.join(model_dir, 'label_encoder.pkl')
    classes_path = os.path.join(model_dir, 'label_encoder_classes.npy')
    
    with open(classifier_path, 'wb') as f:
        pickle.dump(classifier, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"✅ Saved: {classifier_path}")
    
    with open(encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"✅ Saved: {encoder_path}")
    
    np.save(classes_path, label_encoder.classes_)
    print(f"✅ Saved: {classes_path}")
    
    print()
    print("=" * 70)
    print("✅ SUCCESS!")
    print("=" * 70)
    print()
    print(f"📋 Summary:")
    print(f"   ✅ Generated {successful_embeddings} embeddings")
    print(f"   ✅ Embedding dimension: {X.shape[1]} features")
    print(f"   ✅ Trained on {X.shape[0]} samples")
    print(f"   ✅ {len(np.unique(y))} classes")
    print(f"   ✅ Training accuracy: {train_accuracy:.2%}")
    if has_test_set:
        print(f"   ✅ Testing accuracy: {test_accuracy:.2%}")
    print()
    print("🎉 Your model now matches the current embedding generator!")
    print()
    print("Next steps:")
    print("1. Restart backend: python app.py")
    print("2. Test recognition")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = generate_embeddings_from_images()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
