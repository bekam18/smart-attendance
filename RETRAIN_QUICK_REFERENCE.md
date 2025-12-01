# SmartAttendance Retraining - Quick Reference Card

## 🚀 Run Retraining

```bash
# Option 1: Batch file (easiest)
retrain_clean.bat

# Option 2: Python command
python retrain_model.py

# Option 3: Custom paths
python retrain_model.py --data-dir backend/dataset/processed --out-dir backend/models/Classifier
```

## 📋 What It Does

1. **Deletes** old model artifacts (NOT student images!)
2. **Scans** `backend/dataset/processed/` for student folders
3. **Extracts** 512-dim FaceNet embeddings (InsightFace detection)
4. **Trains** SVM classifier with StandardScaler
5. **Evaluates** accuracy and recommends threshold
6. **Saves** all artifacts and reports

## 📁 Output Files

```
backend/models/Classifier/
├── face_classifier_v1.pkl      # Main model
├── label_encoder.pkl           # Label encoder
└── label_encoder_classes.npy   # Student IDs

models/
├── X.npy                       # Embeddings (N × 512)
├── y.npy                       # Labels
├── labels.csv                  # ID mapping
├── training_report.txt         # Metrics
└── MODEL_README.md             # Docs
```

## 🧪 Test Model

```bash
# Test loading and inference
python test_retrained_model.py

# Test with backend
cd backend
python test_production_model.py
```

## ⚙️ Configuration

**Threshold**: Edit `backend/config.py` → `RECOGNITION_CONFIDENCE_THRESHOLD`

| Value | Behavior |
|-------|----------|
| 0.50-0.60 | Permissive (more false positives) |
| 0.70-0.80 | Balanced (recommended) |
| 0.85-0.95 | Strict (more unknowns) |

## 📊 Expected Results

- **Accuracy**: >95%
- **Time**: 5-10 minutes for 3000 images
- **Embeddings**: 512-dimensional, L2-normalized
- **Threshold**: Recommended by analysis (typically 0.70-0.80)

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No faces detected | Check image quality, ensure frontal faces |
| Low accuracy | Add more images (10-20 per student) |
| Import errors | `pip install -r backend/requirements.txt` |
| Model loading fails | Check `models/training_error.log` |

## 📚 Documentation

- **Complete Guide**: `RETRAINING_GUIDE.md`
- **Summary**: `RETRAIN_SUMMARY.md`
- **Deliverables**: `RETRAIN_DELIVERABLES.md`
- **Model Docs**: `models/MODEL_README.md` (after training)
- **Training Report**: `models/training_report.txt` (after training)

## ✅ Safety

- ✅ Student images in `backend/dataset/processed/` are NEVER deleted
- ✅ Only model artifacts are removed
- ✅ All deletions are logged
- ✅ Errors are saved to `models/training_error.log`

## 🎯 Next Steps After Training

1. Review `models/training_report.txt`
2. Test: `python test_retrained_model.py`
3. Start backend: `cd backend && python app.py`
4. Test live recognition in frontend
5. Adjust threshold if needed

---

**Quick Start**: Just run `retrain_clean.bat` and wait 5-10 minutes!
