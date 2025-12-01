# Production Model Training Guide

Complete guide for training face recognition model from your processed dataset.

## 🎯 Overview

This training pipeline:
- Uses your existing `backend/dataset/processed/` images
- Extracts 512-dimensional FaceNet embeddings
- Trains SVM/Logistic Regression classifier
- Implements open-set recognition for unknown faces
- Outputs backend-compatible model files

## 📁 Dataset Structure

Your dataset should be organized as:

```
backend/dataset/processed/
├── STU001/
│   ├── frame_001.jpg
│   ├── frame_002.jpg
│   └── ... (10-20+ images)
├── STU002/
│   ├── frame_001.jpg
│   └── ...
└── STU003/
    └── ...
```

**Requirements:**
- Folder names = Student IDs (must match MongoDB)
- 10-20+ images per student (pre-cropped/aligned)
- Supported formats: JPG, JPEG, PNG, BMP

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd backend
venv\Scripts\activate
pip install torch torchvision facenet-pytorch tqdm
```

### Step 2: Train Model

```bash
# From root directory
train_production.bat
```

Or manually:

```bash
cd backend
venv\Scripts\activate
python train_production_model.py
```

### Step 3: Test Model

```bash
test_production.bat
```

Or manually:

```bash
python test_production_model.py --test-all
```

## 📋 Training Options

### Basic Training (Recommended)

```bash
python train_production_model.py
```

Uses defaults:
- Dataset: `dataset/processed`
- Output: `models/Classifier`
- Classifier: SVM
- Threshold: 95th percentile

### Advanced Options

```bash
# Use Logistic Regression
python train_production_model.py --classifier logistic

# Adjust confidence threshold
python train_production_model.py --threshold-percentile 90  # Stricter
python train_production_model.py --threshold-percentile 98  # More lenient

# Custom paths
python train_production_model.py --dataset path/to/dataset --output path/to/output

# Full custom
python train_production_model.py \
  --dataset dataset/processed \
  --output models/Classifier \
  --classifier svm \
  --threshold-percentile 95
```

## 📦 Output Files

Training produces these files in `backend/models/Classifier/`:

### Required Files (Backend Compatible)

1. **`face_classifier_v1.pkl`** - Main model file
   - Contains: classifier, scaler, label_encoder, metadata
   - Size: 1-10 MB
   - Format: Python pickle

2. **`label_encoder_classes.npy`** - Student ID mapping
   - Contains: Array of student IDs
   - Size: <1 MB
   - Format: NumPy array

### Optional Files (For Analysis)

3. **`X.npy`** - Training embeddings (512-dim)
4. **`y.npy`** - Training labels (encoded)
5. **`training_metadata.json`** - Human-readable metadata
6. **`training_summary.txt`** - Training summary report
7. **`training.log`** - Detailed training logs

## 🔍 Training Pipeline

### Step 1: Dataset Loading
```
Load images from dataset/processed/
├─ Walk student folders
├─ Map folder name → student_id
└─ Collect all image paths
```

### Step 2: Embedding Extraction
```
For each image:
├─ Load image
├─ Detect face with MTCNN (or resize if pre-cropped)
├─ Extract 512-dim embedding with FaceNet
└─ Store embedding + label
```

### Step 3: Classifier Training
```
├─ Encode labels (student_id → numeric)
├─ Split 80% train / 20% test (stratified)
├─ Scale embeddings with StandardScaler
├─ Train SVM or Logistic Regression
└─ Evaluate on test set
```

### Step 4: Threshold Calculation
```
├─ Get prediction probabilities on training set
├─ Calculate percentile of max probabilities
└─ Use as confidence threshold for unknown detection
```

### Step 5: Model Saving
```
Save to models/Classifier/:
├─ face_classifier_v1.pkl (main model)
├─ label_encoder_classes.npy (student IDs)
├─ X.npy, y.npy (embeddings & labels)
└─ metadata files
```

## ✅ Expected Output

### Successful Training

```
============================================================
STARTING FACE RECOGNITION TRAINING
============================================================

Loading dataset from: dataset/processed
Found 10 student directories
Loading STU001: 25 images
Loading STU002: 30 images
...
Total images loaded: 250
Unique students: 10

Extracting embeddings...
100%|████████████████████| 250/250 [00:45<00:00,  5.50it/s]
Successfully extracted 250 embeddings
Failed: 0 images
Embeddings shape: (250, 512)

Training SVM classifier...
Training set: 200 samples
Test set: 50 samples

============================================================
Test Accuracy: 0.9800
============================================================

Classification Report:
              precision    recall  f1-score   support
      STU001       1.00      1.00      1.00         5
      STU002       0.96      1.00      0.98         5
      ...

Calculating confidence threshold...
Confidence threshold (percentile=95): 0.8542

Saving model artifacts...
✓ Saved: models/Classifier/face_classifier_v1.pkl
✓ Saved: models/Classifier/label_encoder_classes.npy
✓ Saved: models/Classifier/X.npy
✓ Saved: models/Classifier/y.npy
✓ Saved: models/Classifier/training_metadata.json
✓ Saved: models/Classifier/training_summary.txt

============================================================
MODEL TRAINING COMPLETE
============================================================
```

## 🧪 Testing

### Test Single Image

```bash
python test_production_model.py --image dataset/processed/STU001/frame_001.jpg
```

Output:
```
Processing: dataset/processed/STU001/frame_001.jpg
✓ Prediction: STU001 (confidence: 0.9234)
  Top 3 predictions:
    STU001: 0.9234
    STU002: 0.0456
    STU003: 0.0234
```

### Test Entire Dataset

```bash
python test_production_model.py --test-all
```

Output:
```
Testing STU001: 25 images
✓ Prediction: STU001 (confidence: 0.9234)
...
STU001 Accuracy: 5/5 (100%)

============================================================
OVERALL TEST RESULTS
============================================================
Total images tested: 50
Correct predictions: 49
Overall accuracy: 98.00%
============================================================
```

## 🎯 Performance Expectations

### Training Time

| Dataset Size | CPU Time | GPU Time |
|--------------|----------|----------|
| 10 students, 100 images | 2-3 min | 30-60 sec |
| 20 students, 200 images | 4-6 min | 1-2 min |
| 50 students, 500 images | 10-15 min | 3-5 min |

### Accuracy

| Images per Student | Expected Accuracy |
|--------------------|-------------------|
| 10-20 images | 90-95% |
| 20-50 images | 95-98% |
| 50+ images | 98-99% |

### Recognition Speed

- Face detection: 50-100ms
- Embedding extraction: 20-50ms
- Classification: <1ms
- **Total: 100-200ms per frame**

## 🔧 Troubleshooting

### Issue: "No module named 'torch'"

**Solution:**
```bash
pip install torch torchvision facenet-pytorch
```

### Issue: "No student directories found"

**Solution:**
Check dataset structure:
```bash
dir backend\dataset\processed
```

Should show student folders (STU001, STU002, etc.)

### Issue: "No images found for STUXXX"

**Solution:**
Ensure images are in correct format (JPG, JPEG, PNG, BMP):
```bash
dir backend\dataset\processed\STU001
```

### Issue: Low accuracy (<90%)

**Solutions:**
1. Add more images per student (20+ recommended)
2. Ensure images are clear and well-lit
3. Remove poor quality images
4. Check for mislabeled folders

### Issue: "Invalid embedding dimension"

**Solution:**
This should not occur with the new script. If it does:
```bash
pip uninstall facenet-pytorch
pip install facenet-pytorch==2.5.3
```

### Issue: Too many "Unknown" predictions

**Solution:**
Lower the threshold percentile:
```bash
python train_production_model.py --threshold-percentile 90
```

### Issue: False positives (wrong student recognized)

**Solution:**
Raise the threshold percentile:
```bash
python train_production_model.py --threshold-percentile 98
```

## 🔄 Retraining

### When to Retrain

- Adding new students
- Updating student images
- Accuracy has degraded
- Changing threshold settings

### Retraining Steps

```bash
# 1. Update dataset (add new student folders or images)

# 2. Retrain model
train_production.bat

# 3. Test new model
test_production.bat

# 4. If satisfied, restart backend
cd backend
python app.py
```

Old model files will be overwritten automatically.

## 🚀 Deployment

### After Training

1. **Verify model files exist:**
   ```bash
   dir backend\models\Classifier
   ```
   Should show: `face_classifier_v1.pkl`, `label_encoder_classes.npy`

2. **Test model:**
   ```bash
   python test_production_model.py --test-all
   ```

3. **Start backend:**
   ```bash
   cd backend
   venv\Scripts\activate
   python app.py
   ```

4. **Test live recognition:**
   - Start frontend: `cd frontend && npm run dev`
   - Login as Instructor
   - Create attendance session
   - Test with camera

### Backend Integration

The backend automatically:
- Loads the new model format
- Uses the scaler for embeddings
- Applies the trained threshold
- Returns student IDs or "Unknown"

**No code changes needed!**

## 📊 Model Metadata

The trained model includes metadata:

```json
{
  "embedding_model": "InceptionResnetV1",
  "pretrained_on": "vggface2",
  "embedding_dim": 512,
  "num_classes": 10,
  "classes": ["STU001", "STU002", ...],
  "threshold": 0.8542,
  "classifier_type": "SVC",
  "accuracy": 0.98,
  "training_date": "2024-11-24T22:30:00",
  "num_training_samples": 250
}
```

Access in code:
```python
from recognizer.loader import model_loader
metadata = model_loader.get_metadata()
threshold = model_loader.get_threshold()
```

## 🎓 Best Practices

### Dataset Quality

1. **Image quantity:** 20+ images per student
2. **Image diversity:** Various lighting, expressions, angles
3. **Image quality:** Clear, sharp, well-lit
4. **Consistency:** Similar quality across all students

### Training

1. **Start with defaults:** SVM, 95th percentile
2. **Test thoroughly:** Use test script before deployment
3. **Monitor accuracy:** Should be >90%
4. **Adjust threshold:** Based on false positive/negative rates

### Deployment

1. **Backup old model:** Before retraining
2. **Test new model:** Before deploying
3. **Monitor performance:** Track recognition accuracy
4. **Retrain periodically:** When adding students or accuracy drops

## 📝 Summary

**Training Command:**
```bash
train_production.bat
```

**Testing Command:**
```bash
test_production.bat
```

**Output Files:**
- `backend/models/Classifier/face_classifier_v1.pkl`
- `backend/models/Classifier/label_encoder_classes.npy`
- Plus optional analysis files

**Next Steps:**
1. Train model
2. Test accuracy
3. Start backend
4. Test live recognition

The system is production-ready and fully compatible with your SmartAttendance backend!
