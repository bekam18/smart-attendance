"""
Test script to verify model loading and recognition pipeline
Run this to diagnose issues before starting the server
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_dependencies():
    """Test if all dependencies are installed"""
    print("\n" + "="*60)
    print("TESTING DEPENDENCIES")
    print("="*60)
    
    deps = {
        'torch': 'PyTorch',
        'torchvision': 'TorchVision',
        'facenet_pytorch': 'FaceNet PyTorch',
        'PIL': 'Pillow',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'sklearn': 'Scikit-learn'
    }
    
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - NOT INSTALLED")
    
    print("="*60)

def test_model_files():
    """Test if model files exist"""
    print("\n" + "="*60)
    print("TESTING MODEL FILES")
    print("="*60)
    
    from config import config
    
    model_path = config.MODEL_PATH
    print(f"Model directory: {model_path}")
    print(f"Exists: {os.path.exists(model_path)}")
    
    files = {
        'face_classifier_v1.pkl': 'Main classifier',
        'label_encoder_classes.npy': 'Student IDs',
        'X.npy': 'Embeddings (optional)',
        'y.npy': 'Labels (optional)',
        'training_metadata.json': 'Metadata (optional)'
    }
    
    for filename, desc in files.items():
        filepath = os.path.join(model_path, filename)
        exists = os.path.exists(filepath)
        size = os.path.getsize(filepath) if exists else 0
        status = "✅" if exists else "❌"
        print(f"{status} {desc}: {filename} ({size} bytes)")
    
    print("="*60)

def test_model_loading():
    """Test model loading"""
    print("\n" + "="*60)
    print("TESTING MODEL LOADING")
    print("="*60)
    
    try:
        from recognizer.loader import model_loader
        
        success = model_loader.load_models()
        
        if success:
            print("✅ Model loaded successfully")
            
            metadata = model_loader.get_metadata()
            if metadata:
                print(f"   Embedding dimension: {metadata.get('embedding_dim')}")
                print(f"   Number of classes: {metadata.get('num_classes')}")
                print(f"   Confidence threshold: {metadata.get('threshold')}")
                print(f"   Classifier type: {metadata.get('classifier_type')}")
                classes = metadata.get('classes', [])
                if len(classes) > 5:
                    print(f"   Students: {', '.join(classes[:5])}... ({len(classes)} total)")
                else:
                    print(f"   Students: {', '.join(classes)}")
        else:
            print("❌ Model loading failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*60)

def test_facenet():
    """Test FaceNet initialization"""
    print("\n" + "="*60)
    print("TESTING FACENET")
    print("="*60)
    
    try:
        from recognizer.embeddings_facenet import embedding_generator
        
        if embedding_generator and embedding_generator.is_available():
            print("✅ FaceNet available")
            
            # Test embedding generation
            import numpy as np
            test_img = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
            embedding = embedding_generator.generate_embedding(test_img)
            
            print(f"   Embedding shape: {embedding.shape}")
            print(f"   Embedding dimension: {embedding.shape[0]}")
            
            if embedding.shape[0] == 512:
                print("✅ Correct embedding dimension (512)")
            else:
                print(f"❌ Wrong embedding dimension: {embedding.shape[0]}, expected 512")
        else:
            print("❌ FaceNet not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*60)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FACE RECOGNITION SYSTEM DIAGNOSTICS")
    print("="*60)
    
    test_dependencies()
    test_model_files()
    test_model_loading()
    test_facenet()
    
    print("\n" + "="*60)
    print("DIAGNOSTICS COMPLETE")
    print("="*60)
    print("\nIf all tests pass, the system should work correctly.")
    print("If any tests fail, fix the issues before starting the server.\n")

if __name__ == '__main__':
    main()
