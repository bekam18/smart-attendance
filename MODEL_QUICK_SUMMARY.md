# Face Recognition Model - Quick Summary

## What We're Using

**Method**: Transfer Learning (Pretrained FaceNet + Trained SVM)

**Pipeline**:
```
Image → Face Detection → Embedding (FaceNet) → Classification (SVM) → Student ID
```

## Key Components

1. **Face Detector**: OpenCV Haar Cascade
2. **Embedding Model**: FaceNet InceptionResnetV1 (pretrained on VGGFace2)
3. **Classifier**: Linear SVM with probability
4. **Preprocessing**: L2 normalization + StandardScaler

## Training Stats

- **Students**: 19
- **Images**: 2,907 (~153 per student)
- **Accuracy**: 99.8%
- **Embedding Dim**: 512
- **Threshold**: 0.60 (runtime), 0.89 (trained)

## What Was Trained?

✅ **Trained**: SVM classifier, StandardScaler, LabelEncoder
❌ **Not Trained**: FaceNet (pretrained, frozen)

## Performance

- **Inference Time**: 300-400ms (CPU), 100-150ms (GPU)
- **Memory**: ~100MB
- **Accuracy**: 99.8% on training set

## Current Issues

1. **Low threshold (0.60)** → Some false positives
2. **Lighting sensitive** → Poor performance in dark/bright
3. **Similar faces** → Can confuse students

## Quick Fixes

1. **Increase threshold to 0.75**: Reduces false positives
2. **Collect more images**: 200-300 per student
3. **Better lighting**: Improve camera setup

## Files

- `face_classifier_v1.pkl` - Main model
- `label_encoder_classes.npy` - Student IDs
- `X.npy` - Training embeddings
- `training_metadata.json` - Model info

## Retraining

```bash
cd backend
python train_production_model.py
```

---

**For full details, see**: `FACE_RECOGNITION_TECHNICAL_README.md`
