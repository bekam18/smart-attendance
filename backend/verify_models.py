"""
Model Path Verification Script
Checks if all required model files exist and are loadable
"""
import os
import sys
import pickle
import numpy as np
from config import config

def verify_model_files():
    """Verify all model files exist and can be loaded"""
    
    print("=" * 60)
    print("MODEL PATH VERIFICATION")
    print("=" * 60)
    print()
    
    model_path = config.MODEL_PATH
    print(f"📁 Model directory: {model_path}")
    print(f"📁 Absolute path: {os.path.abspath(model_path)}")
    print()
    
    # Check if directory exists
    if not os.path.exists(model_path):
        print(f"❌ Model directory does not exist!")
        print(f"💡 Create it with: mkdir -p {model_path}")
        return False
    
    print("✅ Model directory exists")
    print()
    
    # Define required files
    required_files = {
        'face_classifier_v1.pkl': 'Classifier model',
        'label_encoder.pkl': 'Label encoder',
        'label_encoder_classes.npy': 'Class labels'
    }
    
    optional_files = {
        'labels.csv': 'Label mapping (optional)',
        'X.npy': 'Training features (optional)',
        'y.npy': 'Training labels (optional)'
    }
    
    all_files_ok = True
    
    # Check required files
    print("📋 REQUIRED FILES:")
    print("-" * 60)
    for filename, description in required_files.items():
        filepath = os.path.join(model_path, filename)
        exists = os.path.exists(filepath)
        
        if exists:
            size = os.path.getsize(filepath)
            print(f"✅ {filename}")
            print(f"   {description}")
            print(f"   Size: {size:,} bytes")
            
            # Try to load the file
            try:
                if filename.endswith('.pkl'):
                    with open(filepath, 'rb') as f:
                        obj = pickle.load(f)
                    print(f"   ✅ Successfully loaded (type: {type(obj).__name__})")
                elif filename.endswith('.npy'):
                    arr = np.load(filepath, allow_pickle=True)
                    print(f"   ✅ Successfully loaded (shape: {arr.shape if hasattr(arr, 'shape') else len(arr)})")
            except Exception as e:
                print(f"   ❌ Error loading: {e}")
                all_files_ok = False
        else:
            print(f"❌ {filename}")
            print(f"   {description}")
            print(f"   FILE NOT FOUND!")
            all_files_ok = False
        
        print()
    
    # Check optional files
    print("📋 OPTIONAL FILES:")
    print("-" * 60)
    for filename, description in optional_files.items():
        filepath = os.path.join(model_path, filename)
        exists = os.path.exists(filepath)
        
        if exists:
            size = os.path.getsize(filepath)
            print(f"✅ {filename}")
            print(f"   {description}")
            print(f"   Size: {size:,} bytes")
        else:
            print(f"⚠️  {filename}")
            print(f"   {description}")
            print(f"   Not found (optional)")
        
        print()
    
    # List all files in directory
    print("📋 ALL FILES IN MODEL DIRECTORY:")
    print("-" * 60)
    try:
        all_files = os.listdir(model_path)
        if all_files:
            for f in sorted(all_files):
                if not f.startswith('.'):
                    filepath = os.path.join(model_path, f)
                    size = os.path.getsize(filepath)
                    print(f"  📄 {f} ({size:,} bytes)")
        else:
            print("  (empty directory)")
    except Exception as e:
        print(f"  ❌ Error listing directory: {e}")
    
    print()
    print("=" * 60)
    
    if all_files_ok:
        print("✅ ALL REQUIRED MODEL FILES ARE PRESENT AND LOADABLE")
        print()
        print("🎉 Your model files are correctly configured!")
        print()
        print("Next steps:")
        print("1. Start the backend: python app.py")
        print("2. Test recognition: curl http://localhost:5000/api/debug/model-status")
        return True
    else:
        print("❌ SOME REQUIRED MODEL FILES ARE MISSING OR CORRUPTED")
        print()
        print("💡 Solutions:")
        print("1. Ensure your model files are in: backend/models/Classifier/")
        print("2. Required files:")
        print("   - face_classifier_v1.pkl")
        print("   - label_encoder.pkl")
        print("   - label_encoder_classes.npy")
        print()
        print("3. If you have model files with different names, rename them:")
        print("   - classifier.pkl → face_classifier_v1.pkl")
        print("   - encoder.pkl → label_encoder.pkl")
        print("   - classes.npy → label_encoder_classes.npy")
        return False

if __name__ == '__main__':
    success = verify_model_files()
    sys.exit(0 if success else 1)
