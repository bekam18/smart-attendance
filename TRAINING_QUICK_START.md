# Face Recognition Training - Quick Start

## 🚀 Quick Training (3 Steps)

### Step 1: Prepare Dataset

Create folder structure:
```
backend/dataset/
├── STU001/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── photo3.jpg
├── STU002/
│   └── ...
└── STU003/
    └── ...
```

**Requirements:**
- Folder names = Student IDs (must match MongoDB)
- 3-5+ images per student
- Clear, well-lit faces
- JPG/JPEG/PNG format

### Step 2: Validate Dataset

```bash
cd backend
venv\Scripts\activate
python prepare_dataset.py --validate
```

### Step 3: Train Model

```bash
train_model.bat
```

**Done!** Model files saved to `backend/models/Classifier/`

---

## 📋 Command Reference

### Validate Dataset
```bash
cd backend
venv\Scripts\activate
python prepare_dataset.py --validate
```

### Show Dataset Statistics
```bash
python prepare_dataset.py --stats
```

### Train with Default Settings (SVM, 95% threshold)
```bash
python train_model.py
```

### Train with Logistic Regression
```bash
python train_model.py --classifier logistic
```

### Adjust Confidence Threshold
```bash
# More strict (fewer false positives)
python train_model.py --threshold-percentile 90

# More lenient (fewer false negatives)
python train_model.py --threshold-percentile 98
```

---

## 🎯 What Gets Trained

| Component | Technology | Output |
|-----------|-----------|--------|
| Face Detection | MTCNN | Detects & crops faces |
| Feature Extraction | FaceNet (VGGFace2) | 512-dim embeddings |
| Classification | SVM / Logistic Regression | Student ID predictions |
| Unknown Detection | Confidence Threshold | Rejects low-confidence faces |

---

## 📦 Output Files

After training, you'll have:

```
backend/models/Classifier/
├── face_classifier.pkl      # Trained classifier
├── label_encoder.pkl        # Student ID mapping
└── model_metadata.pkl       # Config & threshold
```

---

## ✅ Success Indicators

Good training output looks like:
```
✓ Successfully processed 45 images
✓ Embeddings shape: (45, 512)
✓ Unique students: 9
✓ Test Accuracy: 0.9778
✓ Confidence threshold: 0.8542
```

---

## ⚠️ Common Issues

### "No face detected"
- Use clear, frontal face photos
- Ensure good lighting
- Check image quality

### "Only X images found"
- Add more images per student (3-5+ recommended)
- More images = better accuracy

### Low accuracy (<0.90)
- Add more training images
- Remove poor quality images
- Check for mislabeled folders

---

## 🔄 Retraining

To retrain with new students:

1. Add new student folders to `backend/dataset/`
2. Run `train_model.bat` again
3. Restart backend server

Old model files will be replaced automatically.

---

## 🧪 Testing

After training:

1. Start backend: `cd backend && venv\Scripts\activate && python app.py`
2. Start frontend: `cd frontend && npm run dev`
3. Login as Instructor
4. Create attendance session
5. Test face recognition with camera

---

## 📚 Full Documentation

See `TRAINING_GUIDE.md` for detailed information.
