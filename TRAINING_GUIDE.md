# Face Recognition Model Training Guide

## Overview

This guide explains how to train the face recognition model from scratch using:
- **MTCNN** for face detection
- **FaceNet (InceptionResnetV1)** for 512-dimensional embeddings
- **SVM or Logistic Regression** for classification
- **Open-set recognition** for unknown face detection

## Dataset Structure

Organize your training images in the following structure:

```
backend/dataset/
├── student_id_1/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── image3.jpg
├── student_id_2/
│   ├── image1.jpg
│   └── image2.jpg
└── student_id_3/
    ├── image1.jpg
    ├── image2.jpg
    └── image3.jpg
```

### Dataset Requirements

1. **Directory Names**: Use student IDs as folder names (must match MongoDB student IDs)
2. **Image Formats**: JPG, JPEG, or PNG
3. **Images Per Student**: Minimum 3-5 images recommended for better accuracy
4. **Image Quality**:
   - Clear, well-lit faces
   - Frontal or near-frontal poses
   - Minimal occlusions (no sunglasses, masks)
   - Resolution: At least 160x160 pixels

### Example Dataset Creation

```bash
# Create dataset directory
mkdir -p backend/dataset

# Add student folders
mkdir backend/dataset/STU001
mkdir backend/dataset/STU002
mkdir backend/dataset/STU003

# Add images (copy your images to respective folders)
# backend/dataset/STU001/photo1.jpg
# backend/dataset/STU001/photo2.jpg
# etc.
```

## Installation

### 1. Install Dependencies

```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

The new requirements include:
- `torch` - PyTorch for deep learning
- `torchvision` - Computer vision utilities
- `facenet-pytorch` - Pre-trained FaceNet model

### 2. Verify Installation

```bash
python -c "import torch; import facenet_pytorch; print('Dependencies OK')"
```

## Training Process

### Quick Start (Recommended)

Simply run the batch script:

```bash
train_model.bat
```

This will:
1. Activate the virtual environment
2. Train the model using default settings (SVM classifier, 95% threshold)
3. Save model artifacts to `backend/models/Classifier/`

### Advanced Training Options

For more control, run the Python script directly:

```bash
cd backend
venv\Scripts\activate

# Basic training with SVM
python train_model.py

# Use Logistic Regression instead
python train_model.py --classifier logistic

# Adjust confidence threshold (lower = more strict)
python train_model.py --threshold-percentile 90

# Custom dataset and output paths
python train_model.py --dataset path/to/dataset --output path/to/output

# Full example
python train_model.py --dataset dataset --output models/Classifier --classifier svm --threshold-percentile 95
```

### Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dataset` | `backend/dataset` | Path to training images |
| `--output` | `backend/models/Classifier` | Where to save model files |
| `--classifier` | `svm` | Classifier type (`svm` or `logistic`) |
| `--threshold-percentile` | `95` | Confidence threshold (1-100) |

## Training Pipeline

The training script performs these steps:

### 1. Face Detection (MTCNN)
- Detects faces in each training image
- Crops and aligns faces to 160x160 pixels
- Skips images where no face is detected

### 2. Embedding Extraction (FaceNet)
- Uses InceptionResnetV1 pre-trained on VGGFace2
- Generates 512-dimensional embeddings for each face
- Embeddings capture facial features in a compact representation

### 3. Classifier Training
- Trains SVM or Logistic Regression on embeddings
- Maps embeddings to student IDs
- Evaluates on test set (20% of data)

### 4. Threshold Calculation
- Calculates confidence threshold for open-set recognition
- Uses percentile of training confidences
- Lower threshold = more strict (fewer false positives)
- Higher threshold = more lenient (fewer false negatives)

### 5. Model Saving
Saves three files to `backend/models/Classifier/`:
- `face_classifier.pkl` - Trained classifier
- `label_encoder.pkl` - Student ID encoder
- `model_metadata.pkl` - Model configuration and threshold

## Output Files

After training, you'll have:

```
backend/models/Classifier/
├── face_classifier.pkl      # SVM/LogisticRegression model
├── label_encoder.pkl        # Maps predictions to student IDs
└── model_metadata.pkl       # Contains:
                             #   - embedding_dim: 512
                             #   - num_classes: number of students
                             #   - classes: list of student IDs
                             #   - threshold: confidence threshold
                             #   - model_type: SVM or LogisticRegression
```

## Understanding the Output

### Training Logs

```
INFO - Using device: cuda  # or cpu
INFO - Loaded FaceNet model (vggface2) - 512-dimensional embeddings
INFO - Found 3 student directories
INFO - Processing STU001: 5 images
INFO - Processing STU002: 4 images
INFO - Processing STU003: 6 images
INFO - Successfully processed 15 images
INFO - Failed to process 0 images
INFO - Embeddings shape: (15, 512)
INFO - Unique students: 3
INFO - Training set: 12 samples
INFO - Test set: 3 samples
INFO - Test Accuracy: 1.0000
INFO - Confidence threshold (percentile=95): 0.8542
```

### Classification Report

```
              precision    recall  f1-score   support

      STU001       1.00      1.00      1.00         1
      STU002       1.00      1.00      1.00         1
      STU003       1.00      1.00      1.00         1

    accuracy                           1.00         3
   macro avg       1.00      1.00      1.00         3
weighted avg       1.00      1.00      1.00         3
```

## Open-Set Recognition

The model implements open-set recognition to detect unknown faces:

1. **Confidence Threshold**: Predictions below this threshold are marked as "Unknown"
2. **Threshold Calculation**: Based on training data confidence distribution
3. **Adjusting Threshold**:
   - **Lower percentile (e.g., 90)**: More strict, fewer false positives
   - **Higher percentile (e.g., 98)**: More lenient, fewer false negatives

### Example Scenarios

```python
# High confidence → Known student
Prediction: STU001, Confidence: 0.95 → "STU001"

# Low confidence → Unknown face
Prediction: STU001, Confidence: 0.65 → "Unknown"
```

## Troubleshooting

### No faces detected

**Problem**: "No face detected in image.jpg"

**Solutions**:
- Ensure faces are clearly visible and well-lit
- Check image quality and resolution
- Try different angles or lighting conditions
- Verify images are not corrupted

### Low accuracy

**Problem**: Test accuracy < 0.90

**Solutions**:
- Add more training images per student (5-10 recommended)
- Ensure diverse poses and lighting in training data
- Remove poor quality images
- Check for mislabeled data (wrong student ID folders)

### Embedding dimension error

**Problem**: "Invalid embedding dimension: X"

**Solutions**:
- This should not occur with the new script
- If it does, verify facenet-pytorch installation:
  ```bash
  pip uninstall facenet-pytorch
  pip install facenet-pytorch==2.5.3
  ```

### CUDA out of memory

**Problem**: "CUDA out of memory"

**Solutions**:
- The script will automatically fall back to CPU
- Or reduce batch size by processing fewer images at once
- Or use a machine with more GPU memory

### Import errors

**Problem**: "ModuleNotFoundError: No module named 'torch'"

**Solutions**:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

## Retraining the Model

To retrain with new students or updated images:

1. Update the dataset directory with new images
2. Run the training script again:
   ```bash
   train_model.bat
   ```
3. The old model files will be overwritten
4. Restart the backend server to load the new model

## Integration with Backend

The trained model integrates seamlessly with the existing backend:

1. **Model Loading**: `backend/recognizer/loader.py` loads the artifacts
2. **Face Detection**: `backend/recognizer/detector.py` uses MTCNN
3. **Embedding Extraction**: `backend/recognizer/embeddings.py` uses FaceNet
4. **Classification**: `backend/recognizer/classifier.py` uses the trained classifier
5. **Threshold Check**: Predictions below threshold are marked as "Unknown"

No code changes needed - the backend automatically uses the new model format!

## Best Practices

1. **Dataset Quality**:
   - Use high-quality, diverse images
   - Include different lighting conditions
   - Capture various facial expressions
   - Minimum 3-5 images per student

2. **Regular Retraining**:
   - Retrain when adding new students
   - Retrain if accuracy degrades
   - Update with better quality images

3. **Threshold Tuning**:
   - Start with default (95th percentile)
   - Lower if too many false positives (unknown faces recognized)
   - Raise if too many false negatives (known faces marked unknown)

4. **Testing**:
   - Test with real-world conditions
   - Verify accuracy with live camera feed
   - Monitor attendance logs for errors

## Next Steps

After training:

1. ✓ Verify model files exist in `backend/models/Classifier/`
2. ✓ Start the backend server: `cd backend && venv\Scripts\activate && python app.py`
3. ✓ Test face recognition via the attendance session page
4. ✓ Monitor logs for any recognition errors
5. ✓ Retrain if needed with additional images

## Support

If you encounter issues:

1. Check the training logs for specific errors
2. Verify dataset structure matches the required format
3. Ensure all dependencies are installed correctly
4. Review the troubleshooting section above
5. Check `backend/logs/` for detailed error messages
