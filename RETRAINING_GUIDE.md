# SmartAttendance Face Recognition Retraining Guide

## Overview

This guide explains how to completely retrain the face recognition classifier from scratch using the new pipeline:

- **Detection**: InsightFace FaceAnalysis (SCRFD)
- **Embeddings**: FaceNet InceptionResnetV1 (pretrained on VGGFace2)
- **Classifier**: SVM with linear kernel

## Quick Start

```bash
# Run complete retraining
python retrain_model.py

# Or use the batch file
retrain_clean.bat
```

## What Gets Deleted

The retraining script performs a **clean reset** by removing:

- `backend/models/Classifier/face_classifier_v1.pkl`
- `backend/models/Classifier/label_encoder.pkl`
- `backend/models/Classifier/label_encoder_classes.npy`
- `backend/models/Classifier/*.pkl` (all pickle files)
- `models/X.npy`
- `models/y.npy`
- `models/labels.csv`
- `models/training_report.txt`
- `models/MODEL_README.md`
- `models/temp/` (entire directory)
- Any embedding cache files

**Important**: Student images in `backend/dataset/processed/` are **NEVER** deleted.

## Dataset Structure

Your dataset should be organized as:

```
backend/dataset/processed/
├── STU001_StudentName/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── STU002_StudentName/
│   ├── image1.jpg
│   └── ...
└── ...
```

- Folder names should follow: `STUxxx_Name` or just `STUxxx`
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`
- Minimum 5-10 images per student recommended

## Training Pipeline

### Step 1: Cleanup
Removes all previous model artifacts (see "What Gets Deleted" above)

### Step 2: Dataset Indexing
- Scans `backend/dataset/processed/` for student folders
- Builds index of all images
- Creates `models/labels.csv` with student ID mapping

### Step 3: Embedding Extraction
For each image:
1. Load image (BGR → RGB)
2. Detect face using InsightFace SCRFD
3. Choose largest face if multiple detected
4. Crop and align face using detected landmarks
5. Resize to 160×160 pixels
6. Normalize to [-1, 1] range
7. Extract 512-dim FaceNet embedding
8. L2-normalize embedding (unit length)

Saves:
- `models/X.npy` - Embeddings (N × 512)
- `models/y.npy` - Labels (N,)

### Step 4: Classifier Training
1. Encode labels with LabelEncoder
2. Scale embeddings with StandardScaler
3. Train SVM classifier (linear kernel, probability=True)
4. Save classifier with metadata

Saves:
- `backend/models/Classifier/face_classifier_v1.pkl` (main model)
- `backend/models/Classifier/label_encoder.pkl`
- `backend/models/Classifier/label_encoder_classes.npy`

### Step 5: Evaluation
- Stratified 80/20 train/test split
- Compute accuracy, classification report, confusion matrix
- Analyze confidence thresholds (0.50 to 0.98)
- Recommend optimal threshold

### Step 6: Reporting
Generates `models/training_report.txt` with:
- Dataset statistics
- Model performance metrics
- Confusion matrix
- Threshold analysis
- Skipped images log
- Error log

### Step 7: Documentation
Creates `models/MODEL_README.md` with:
- Pipeline summary
- Model artifacts structure
- Retraining instructions
- Inference configuration
- Technical details

### Step 8: Backend Verification
Verifies that `backend/recognizer/loader.py` exists and is compatible

## Output Files

After successful training:

```
backend/models/Classifier/
├── face_classifier_v1.pkl      # Main model (SVM + scaler + label_encoder)
├── label_encoder.pkl           # Label encoder
└── label_encoder_classes.npy   # Student IDs array

models/
├── X.npy                       # Training embeddings (N × 512)
├── y.npy                       # Training labels
├── labels.csv                  # Student ID mapping
├── training_report.txt         # Detailed metrics
└── MODEL_README.md             # Technical documentation
```

## Command Line Options

```bash
# Default paths
python retrain_model.py

# Custom data directory
python retrain_model.py --data-dir backend/dataset/processed

# Custom output directories
python retrain_model.py \
  --data-dir backend/dataset/processed \
  --out-dir backend/models/Classifier \
  --embeds-out models
```

## Testing the Model

After training, test the model:

```bash
# Test model loading and inference
python test_retrained_model.py

# Test with backend
cd backend
python test_production_model.py
```

## Confidence Threshold

The training script analyzes multiple thresholds and recommends one based on:
- High accuracy (>95%)
- Low rejection rate (<15%)
- Balance between false positives and unknowns

**Default**: 0.70 (adjustable in `backend/config.py`)

### Threshold Guidelines

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| 0.50-0.60 | Very permissive | High recall, more false positives |
| 0.70-0.80 | Balanced | Recommended for most cases |
| 0.85-0.95 | Strict | Low false positives, more unknowns |

## Troubleshooting

### No faces detected
- Ensure images contain clear, frontal faces
- Check image quality and lighting
- Verify InsightFace is installed: `pip install insightface`

### Low accuracy
- Add more training images per student (10-20 recommended)
- Ensure diverse poses, lighting, expressions
- Check for mislabeled images

### Embedding dimension mismatch
- Verify FaceNet model: `InceptionResnetV1(pretrained='vggface2')`
- Should output 512-dimensional embeddings
- Check `facenet-pytorch` installation

### Model loading errors
- Ensure Python version consistency
- Check pickle protocol compatibility
- Verify all dependencies installed

## Dependencies

Required packages:
```bash
pip install torch torchvision
pip install facenet-pytorch
pip install insightface
pip install opencv-python
pip install scikit-learn
pip install pandas numpy tqdm
```

## Performance Tips

1. **GPU Acceleration**: Use CUDA if available (automatic)
2. **Batch Processing**: Script processes images sequentially for reliability
3. **Memory**: ~2GB RAM for 1000 images
4. **Time**: ~5-10 minutes for 3000 images on CPU

## Next Steps

After successful retraining:

1. Review `models/training_report.txt` for metrics
2. Test model: `python test_retrained_model.py`
3. Start backend: `cd backend && python app.py`
4. Test live recognition in frontend
5. Adjust threshold if needed in `backend/config.py`

## Support

For issues:
1. Check `models/training_error.log` if training fails
2. Review `models/training_report.txt` for skipped images
3. Verify dataset structure matches requirements
4. Ensure all dependencies are installed

---

**Last Updated**: 2024-12-01
