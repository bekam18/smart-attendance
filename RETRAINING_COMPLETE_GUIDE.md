# Complete Model Retraining Guide

## Overview

This guide covers the complete retraining process for the SmartAttendance face recognition system using:
- **InsightFace (SCRFD)** for face detection and alignment
- **FaceNet (InceptionResnetV1 pretrained='vggface2')** for 512-dim embeddings
- **StandardScaler + SVM** for classification

## Quick Start

### Option 1: Run Batch File (Windows)
```bash
retrain_clean.bat
```

### Option 2: Run Python Script Directly
```bash
cd backend
python ../retrain_model.py
```

### Option 3: Custom Paths
```bash
python retrain_model.py --data-dir backend/dataset/processed --out-dir backend/models/Classifier --embeds-out models
```

## What Happens During Retraining

### Step 1: Cleanup Previous Artifacts
Deletes:
- `backend/models/Classifier/face_classifier_v1.pkl`
- `backend/models/Classifier/label_encoder.pkl`
- `backend/models/Classifier/label_encoder_classes.npy`
- `backend/models/Classifier/scaler.pkl`
- `models/X.npy`
- `models/y.npy`
- `models/labels.csv`
- `models/training_report.txt`
- `models/MODEL_README.md`
- `models/temp/` (entire folder)

**Important**: Does NOT delete any files in `backend/dataset/processed/` or `backend/dataset/raw/`

### Step 2: Build Dataset Index
- Scans `backend/dataset/processed/` for student folders
- Expects format: `STUxxx_Name/` (e.g., `STU001_John_Doe/`)
- Counts images per student
- Creates label mapping

### Step 3: Extract Embeddings
For each image:
1. Load image with OpenCV
2. Detect face using InsightFace SCRFD
3. If multiple faces, use largest bounding box
4. Align and crop face
5. Resize to 160x160 for FaceNet
6. Extract 512-dim embedding using FaceNet
7. L2 normalize embedding (unit length)
8. Save to X array

### Step 4: Train Classifier
1. Encode labels using LabelEncoder
2. Scale embeddings using StandardScaler
3. Train SVM classifier:
   - Kernel: linear
   - Probability: True
   - Class weight: balanced

### Step 5: Evaluate
1. Split data 80/20 train/test
2. Compute accuracy, classification report, confusion matrix
3. Test thresholds from 0.50 to 0.98
4. Find optimal threshold balancing accuracy and coverage
5. Recommend default threshold (~0.70-0.89)

### Step 6: Save Artifacts
Saves:
- `backend/models/Classifier/face_classifier_v1.pkl` - Trained SVM
- `backend/models/Classifier/label_encoder.pkl` - Label encoder
- `backend/models/Classifier/label_encoder_classes.npy` - Class names
- `backend/models/Classifier/scaler.pkl` - StandardScaler
- `models/X.npy` - Training embeddings (N x 512)
- `models/y.npy` - Training labels (N,)
- `models/labels.csv` - Student metadata
- `models/training_report.txt` - Evaluation results
- `models/MODEL_README.md` - Documentation

## Expected Output

```
======================================================================
SMARTATTENDANCE FACE RECOGNITION MODEL RETRAINING
======================================================================

======================================================================
STEP 1: Cleaning up previous artifacts
======================================================================
✓ Deleted: backend/models/Classifier/face_classifier_v1.pkl
✓ Deleted: models/X.npy
...
✔ Model cleanup completed. Deleted 8 files.

======================================================================
STEP 2: Building dataset index
======================================================================
✓ STU001: John Doe (15 images)
✓ STU002: Jane Smith (12 images)
...
✔ Found 20 students with 250 total images

======================================================================
STEP 3: Extracting embeddings
======================================================================
Processing 10/250...
Processing 20/250...
...
✔ Extracted 245 embeddings (skipped 5)
✔ Embedding shape: (245, 512)
✔ Labels shape: (245,)

======================================================================
STEP 4: Training classifier
======================================================================
✓ Encoded 20 classes
✓ Scaled embeddings
✓ Training SVM classifier...
✓ Classifier trained

======================================================================
STEP 5: Evaluating classifier
======================================================================
✓ Test Accuracy: 0.9800

              precision    recall  f1-score   support
     STU001       0.98      1.00      0.99         5
     STU002       1.00      0.96      0.98         4
     ...

Threshold Analysis:
--------------------------------------------------
Threshold 0.50: Acc=0.9800, Coverage=1.0000, Score=0.9800
Threshold 0.55: Acc=0.9850, Coverage=0.9800, Score=0.9653
...
Threshold 0.75: Acc=1.0000, Coverage=0.9200, Score=0.9200

✓ Recommended threshold: 0.75

======================================================================
STEP 6: Saving artifacts
======================================================================
✓ Saved classifier: backend/models/Classifier/face_classifier_v1.pkl
✓ Saved label encoder: backend/models/Classifier/label_encoder.pkl
...

======================================================================
✔ TRAINING COMPLETED SUCCESSFULLY!
======================================================================

Artifacts saved to:
  - Classifier: backend/models/Classifier
  - Embeddings: models

Final Accuracy: 0.9800
Recommended Threshold: 0.75
Total Students: 20
Total Embeddings: 245
```

## Troubleshooting

### Issue: "No images found in dataset"
**Solution**: 
- Check that `backend/dataset/processed/` contains student folders
- Verify folder names follow `STUxxx_Name/` format
- Ensure folders contain .jpg, .jpeg, .png, or .bmp files

### Issue: "No face detected" for many images
**Solution**:
- Check image quality (not too dark, blurry, or small)
- Ensure faces are visible and not occluded
- Images should be at least 100x100 pixels
- Face should occupy significant portion of image

### Issue: Low accuracy after training
**Solution**:
- Add more images per student (minimum 10-15 recommended)
- Ensure images have variety (different angles, lighting, expressions)
- Remove duplicate or very similar images
- Check for mislabeled images

### Issue: "Failed to extract embedding"
**Solution**:
- Ensure FaceNet model is properly installed: `pip install facenet-pytorch`
- Check if GPU is available (training is faster with GPU)
- Verify PyTorch is installed correctly

### Issue: Training crashes with memory error
**Solution**:
- Process images in smaller batches
- Reduce image resolution before processing
- Close other applications to free up RAM
- Use GPU if available

## Updating Backend Configuration

After training, update the threshold in `backend/config.py`:

```python
# Face Recognition Settings
RECOGNITION_THRESHOLD = 0.75  # Use recommended value from training_report.txt
```

## Verifying the New Model

Test the new model:

```bash
cd backend
python test_production_model.py
```

Or test via API:

```bash
test_detect_face_endpoint.bat
```

## Re-running Training

To retrain again:

1. Add/remove/update images in `backend/dataset/processed/`
2. Run `retrain_clean.bat` again
3. Old artifacts will be automatically deleted
4. New model will be trained from scratch

## Model Files Explained

### backend/models/Classifier/face_classifier_v1.pkl
The trained SVM classifier. Loaded during inference to predict student identity.

### backend/models/Classifier/label_encoder.pkl
Maps student IDs to numeric labels (0, 1, 2, ...).

### backend/models/Classifier/label_encoder_classes.npy
Array of student IDs in order (e.g., ['STU001', 'STU002', ...]).

### backend/models/Classifier/scaler.pkl
StandardScaler fitted on training embeddings. Must be applied to new embeddings before classification.

### models/X.npy
Training embeddings (N x 512 array). Used for analysis and debugging.

### models/y.npy
Training labels (N array of student IDs). Corresponds to X.npy.

### models/labels.csv
Student metadata: ID, name, number of images.

### models/training_report.txt
Complete evaluation results: accuracy, confusion matrix, per-class metrics, recommended threshold.

## Integration with Backend

The backend automatically loads the new model on restart. The loader (`backend/recognizer/loader.py`) expects:

1. `face_classifier_v1.pkl` - SVM classifier
2. `label_encoder.pkl` - Label encoder
3. `scaler.pkl` - StandardScaler

During inference:
```python
# 1. Detect face with InsightFace
# 2. Extract embedding with FaceNet
# 3. L2 normalize embedding
# 4. Apply scaler: embedding_scaled = scaler.transform(embedding)
# 5. Predict: probas = classifier.predict_proba(embedding_scaled)
# 6. Check threshold: if max(probas) >= threshold: return student_id else: return "unknown"
```

## Best Practices

1. **Image Quality**: Use clear, well-lit images with visible faces
2. **Quantity**: Minimum 10-15 images per student, ideally 20-30
3. **Variety**: Include different angles, expressions, lighting conditions
4. **Consistency**: All images should be similar quality and resolution
5. **Regular Retraining**: Retrain when adding new students or updating images
6. **Threshold Tuning**: Adjust threshold based on false positive/negative rates in production

## Performance Expectations

- **Training Time**: ~1-2 minutes for 20 students with 250 images (CPU)
- **Accuracy**: Typically 95-99% with good quality images
- **Inference Speed**: ~50-100ms per face (CPU), ~10-20ms (GPU)
- **Memory Usage**: ~500MB during training, ~100MB during inference

## Next Steps

After successful retraining:

1. ✅ Check `models/training_report.txt` for accuracy
2. ✅ Update threshold in `backend/config.py` if needed
3. ✅ Restart backend server to load new model
4. ✅ Test with real faces via attendance session
5. ✅ Monitor false positives/negatives in production
6. ✅ Retrain if accuracy is unsatisfactory

## Support

If you encounter issues:

1. Check `models/training_error.log` for detailed error messages
2. Verify all dependencies are installed: `pip install -r backend/requirements.txt`
3. Ensure InsightFace models are downloaded (happens automatically on first run)
4. Test individual components with provided test scripts

## Summary

The retraining script provides a complete, automated pipeline for training a production-ready face recognition model. It handles all steps from cleanup to evaluation, with comprehensive logging and error handling. The resulting model is optimized for the SmartAttendance system and ready for deployment.
