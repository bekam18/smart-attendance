# SmartAttendance Retraining - Quick Summary

## ✅ What Was Created

### 1. Main Retraining Script
**File**: `retrain_model.py`
- Complete clean reset + retrain pipeline
- InsightFace (SCRFD) for detection/alignment
- FaceNet (InceptionResnetV1, vggface2) for 512-dim embeddings
- StandardScaler + SVM classifier
- Comprehensive error handling and logging

### 2. Batch File
**File**: `retrain_clean.bat`
- Windows batch file to run retraining
- Simple double-click execution

### 3. Test Script
**File**: `test_retrained_model.py`
- Verifies model loading
- Tests inference with random embedding
- Checks embedding normalization
- Validates model format

### 4. Documentation
**File**: `RETRAINING_GUIDE.md`
- Complete retraining guide
- Dataset structure requirements
- Step-by-step pipeline explanation
- Troubleshooting tips
- Command line options

### 5. Updated Dependencies
**File**: `backend/requirements.txt`
- Added `pandas==2.1.4`
- Added `tqdm==4.66.1`

## 🚀 How to Use

### Option 1: Batch File (Easiest)
```bash
retrain_clean.bat
```

### Option 2: Python Command
```bash
python retrain_model.py
```

### Option 3: Custom Paths
```bash
python retrain_model.py --data-dir backend/dataset/processed --out-dir backend/models/Classifier --embeds-out models
```

## 📊 What Happens During Retraining

### Step 0: Path Confirmation
- Verifies dataset directory exists
- Counts student folders

### Step 1: Cleanup (Clean Reset)
Deletes these files if they exist:
- `backend/models/Classifier/face_classifier_v1.pkl`
- `backend/models/Classifier/label_encoder.pkl`
- `backend/models/Classifier/label_encoder_classes.npy`
- `backend/models/Classifier/*.pkl`
- `models/X.npy`
- `models/y.npy`
- `models/labels.csv`
- `models/training_report.txt`
- `models/MODEL_README.md`
- `models/temp/`

**IMPORTANT**: Student images in `backend/dataset/processed/` are NEVER deleted!

### Step 2: Dataset Indexing
- Scans student folders
- Builds image index
- Creates `models/labels.csv`

### Step 3: Embedding Extraction
For each image:
1. Load image (BGR → RGB)
2. Detect face with InsightFace SCRFD
3. Choose largest face if multiple
4. Crop and align using landmarks
5. Resize to 160×160
6. Normalize to [-1, 1]
7. Extract 512-dim FaceNet embedding
8. L2-normalize (unit length)

Saves:
- `models/X.npy` (embeddings)
- `models/y.npy` (labels)

### Step 4: Classifier Training
1. Encode labels (LabelEncoder)
2. Scale embeddings (StandardScaler)
3. Train SVM (linear kernel, probability=True, class_weight='balanced')

Saves:
- `backend/models/Classifier/face_classifier_v1.pkl` (main model)
- `backend/models/Classifier/label_encoder.pkl`
- `backend/models/Classifier/label_encoder_classes.npy`

### Step 5: Evaluation
- 80/20 stratified train/test split
- Compute accuracy, classification report, confusion matrix
- Analyze thresholds (0.50 to 0.98)
- Recommend optimal threshold

### Step 6: Training Report
Creates `models/training_report.txt` with:
- Dataset statistics
- Performance metrics
- Confusion matrix
- Threshold analysis
- Skipped images
- Error log

### Step 7: Model README
Creates `models/MODEL_README.md` with:
- Pipeline summary
- Artifact structure
- Retraining instructions
- Inference configuration
- Technical details

### Step 8: Backend Verification
- Checks if `backend/recognizer/loader.py` exists
- Confirms compatibility

## 📁 Output Files

After successful training:

```
backend/models/Classifier/
├── face_classifier_v1.pkl      # Main model (includes SVM, scaler, label_encoder, metadata)
├── label_encoder.pkl           # Label encoder (backup)
└── label_encoder_classes.npy   # Student IDs array

models/
├── X.npy                       # Training embeddings (N × 512)
├── y.npy                       # Training labels (N,)
├── labels.csv                  # Student ID → Name mapping
├── training_report.txt         # Detailed metrics and analysis
└── MODEL_README.md             # Technical documentation
```

## 🧪 Testing

After training:

```bash
# Test model loading and inference
python test_retrained_model.py

# Test with backend
cd backend
python test_production_model.py

# Start backend
cd backend
python app.py
```

## ⚙️ Configuration

### Confidence Threshold

Default: **0.70** (recommended by training analysis)

To change:
1. Edit `backend/config.py`
2. Update `RECOGNITION_CONFIDENCE_THRESHOLD`
3. Restart backend

### Threshold Guidelines

| Value | Behavior |
|-------|----------|
| 0.50-0.60 | Very permissive, more false positives |
| 0.70-0.80 | Balanced (recommended) |
| 0.85-0.95 | Strict, more unknowns |

## 🔍 What to Check

### 1. Files Deleted
Script prints all deleted files during Step 1

### 2. Images Processed
Script shows progress bar and final count:
- Total images found
- Successfully extracted embeddings
- Skipped/failed images

### 3. Final Accuracy
Printed at end of training:
- Test accuracy (should be >95%)
- Confusion matrix
- Per-class metrics

### 4. Recommended Threshold
Script analyzes multiple thresholds and recommends optimal value

### 5. Saved Artifacts
Script lists all saved files with full paths

## 📋 Requirements

### Dataset Structure
```
backend/dataset/processed/
├── STU001_Name/
│   ├── img1.jpg
│   ├── img2.jpg
│   └── ...
├── STU002_Name/
│   └── ...
└── ...
```

### Minimum Images
- 5-10 images per student (minimum)
- 10-20 images per student (recommended)
- Diverse poses, lighting, expressions

### Dependencies
All required packages in `backend/requirements.txt`:
- torch, torchvision
- facenet-pytorch
- insightface
- opencv-python
- scikit-learn
- pandas, numpy, tqdm

## 🐛 Troubleshooting

### No faces detected
- Check image quality
- Ensure frontal faces
- Verify InsightFace installed

### Low accuracy
- Add more training images
- Check for mislabeled data
- Ensure diverse images

### Model loading errors
- Check Python version consistency
- Verify all dependencies installed
- Review `models/training_error.log`

## 📊 Expected Output

```
================================================================================
✔ TRAINING COMPLETED SUCCESSFULLY
================================================================================

📊 RESULTS:
  • Images processed: 3442
  • Embeddings extracted: 3398
  • Students: 19
  • Test accuracy: 0.9876
  • Recommended threshold: 0.75

📁 ARTIFACTS SAVED:
  • backend/models/Classifier/face_classifier_v1.pkl
  • backend/models/Classifier/label_encoder.pkl
  • backend/models/Classifier/label_encoder_classes.npy
  • models/X.npy
  • models/y.npy
  • models/labels.csv
  • models/training_report.txt
  • models/MODEL_README.md

🗑️  FILES DELETED: 8
  • backend/models/Classifier/face_classifier_v1.pkl
  • backend/models/Classifier/label_encoder.pkl
  • ...

⚙️  CONFUSION MATRIX:
[[45  0  0 ...]
 [ 0 42  0 ...]
 [ 0  0 38 ...]]

================================================================================
✓ Training completed. Artifacts saved to backend/models/Classifier and models/
================================================================================
```

## 🎯 Next Steps

1. ✅ Review `models/training_report.txt`
2. ✅ Test model: `python test_retrained_model.py`
3. ✅ Start backend: `cd backend && python app.py`
4. ✅ Test live recognition in frontend
5. ✅ Adjust threshold if needed

---

**Ready to retrain?** Run: `retrain_clean.bat` or `python retrain_model.py`
