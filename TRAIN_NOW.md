# Train Your Model NOW - Quick Commands

## 🚀 Fastest Way to Train

```bash
# 1. Install dependencies (one time only)
cd backend
venv\Scripts\activate
pip install torch torchvision facenet-pytorch tqdm

# 2. Train model (from root directory)
train_production.bat
```

**That's it!** Your model will be ready in 2-15 minutes depending on dataset size.

---

## 📋 What You Need

### Before Training

✅ Images organized in `backend/dataset/processed/`
```
backend/dataset/processed/
├── STU001/
│   ├── frame_001.jpg
│   ├── frame_002.jpg
│   └── ... (10-20+ images)
├── STU002/
│   └── ...
└── STU003/
    └── ...
```

✅ Virtual environment activated
```bash
cd backend
venv\Scripts\activate
```

✅ Dependencies installed
```bash
pip install torch torchvision facenet-pytorch tqdm
```

---

## ⚡ Training Commands

### Option 1: Batch Script (Easiest)
```bash
train_production.bat
```

### Option 2: Python Script
```bash
cd backend
venv\Scripts\activate
python train_production_model.py
```

### Option 3: Custom Training
```bash
# Logistic Regression (faster)
python train_production_model.py --classifier logistic

# Stricter threshold (fewer false positives)
python train_production_model.py --threshold-percentile 90

# More lenient threshold (fewer false negatives)
python train_production_model.py --threshold-percentile 98
```

---

## ✅ After Training

### Test Your Model
```bash
test_production.bat
```

Or:
```bash
cd backend
python test_production_model.py --test-all
```

### Start Backend
```bash
cd backend
venv\Scripts\activate
python app.py
```

### Test Live Recognition
1. Start frontend: `cd frontend && npm run dev`
2. Login as Instructor
3. Create attendance session
4. Test with camera

---

## 📊 Expected Output

```
============================================================
STARTING FACE RECOGNITION TRAINING
============================================================

Loading dataset from: dataset/processed
Found 10 student directories
Total images loaded: 250

Extracting embeddings...
100%|████████████████████| 250/250 [00:45<00:00]
Successfully extracted 250 embeddings

Training SVM classifier...
Test Accuracy: 0.9800

Confidence threshold: 0.8542

Saving model artifacts...
✓ Saved: face_classifier_v1.pkl
✓ Saved: label_encoder_classes.npy

============================================================
MODEL TRAINING COMPLETE
============================================================
```

---

## 🎯 Success Checklist

After training, verify:

- [ ] Training completed without errors
- [ ] Test accuracy > 90%
- [ ] Files exist in `backend/models/Classifier/`:
  - [ ] `face_classifier_v1.pkl`
  - [ ] `label_encoder_classes.npy`
- [ ] Test script shows good results
- [ ] Backend starts without errors
- [ ] Live recognition works

---

## 🐛 Quick Troubleshooting

### "No module named 'torch'"
```bash
pip install torch torchvision facenet-pytorch tqdm
```

### "No student directories found"
Check your dataset:
```bash
dir backend\dataset\processed
```
Should show student folders (STU001, STU002, etc.)

### Low accuracy (<90%)
- Add more images per student (20+ recommended)
- Remove poor quality images
- Check folder names match student IDs

### Too many "Unknown" predictions
```bash
python train_production_model.py --threshold-percentile 90
```

---

## 📚 Full Documentation

- **Complete Guide**: [PRODUCTION_TRAINING_GUIDE.md](PRODUCTION_TRAINING_GUIDE.md)
- **Summary**: [PRODUCTION_TRAINING_SUMMARY.md](PRODUCTION_TRAINING_SUMMARY.md)
- **General Training**: [TRAINING_GUIDE.md](TRAINING_GUIDE.md)

---

## 🎉 Ready to Train?

```bash
train_production.bat
```

**Go!** 🚀
