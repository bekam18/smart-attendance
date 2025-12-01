# Model Retraining - Quick Start

## Run Retraining

```bash
retrain_clean.bat
```

That's it! The script will:
1. ✅ Delete old model artifacts
2. ✅ Extract embeddings from all student images
3. ✅ Train new SVM classifier
4. ✅ Evaluate and find optimal threshold
5. ✅ Save all artifacts

## What You Need

- Student images in `backend/dataset/processed/STUxxx_Name/` folders
- At least 10-15 images per student
- Python dependencies installed (`pip install -r backend/requirements.txt`)

## Output Files

After training completes, check:

- `models/training_report.txt` - Accuracy and evaluation results
- `backend/models/Classifier/face_classifier_v1.pkl` - New trained model
- `models/MODEL_README.md` - Complete documentation

## Expected Results

- **Accuracy**: 95-99% (with good quality images)
- **Training Time**: 1-2 minutes for 20 students
- **Recommended Threshold**: Shown in training_report.txt

## Update Backend

After training, update `backend/config.py`:

```python
RECOGNITION_THRESHOLD = 0.75  # Use value from training_report.txt
```

Then restart the backend server.

## Verify

Test the new model:

```bash
cd backend
python test_production_model.py
```

## Troubleshooting

- **No images found**: Check `backend/dataset/processed/` has student folders
- **Low accuracy**: Add more varied images per student
- **Crashes**: Check `models/training_error.log` for details

## Full Documentation

See `RETRAINING_COMPLETE_GUIDE.md` for detailed information.
