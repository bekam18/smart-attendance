# Face Recognition Training Checklist

Use this checklist to ensure successful model training.

## Pre-Training Checklist

### Environment Setup
- [ ] Python 3.9+ installed
- [ ] Virtual environment created (`backend/venv/`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] PyTorch and facenet-pytorch installed successfully
- [ ] Test imports: `python -c "import torch; import facenet_pytorch; print('OK')"`

### Dataset Preparation
- [ ] Dataset directory created (`backend/dataset/`)
- [ ] Student folders created (named with student IDs)
- [ ] Student IDs match MongoDB records
- [ ] Minimum 3 images per student (5-10 recommended)
- [ ] Images are clear and well-lit
- [ ] Images show frontal or near-frontal faces
- [ ] Image formats are JPG, JPEG, or PNG
- [ ] Image resolution is at least 160x160 pixels
- [ ] No sunglasses, masks, or face obstructions
- [ ] One face per image

### Dataset Validation
- [ ] Run validation: `python prepare_dataset.py --validate`
- [ ] No critical errors reported
- [ ] All students have sufficient images
- [ ] Image quality warnings addressed
- [ ] Dataset statistics reviewed: `python prepare_dataset.py --stats`

## Training Checklist

### Quick Training (Recommended)
- [ ] Run: `train_model.bat` or `prepare_and_train.bat`
- [ ] Training completes without errors
- [ ] Test accuracy > 90%
- [ ] Model files created in `backend/models/Classifier/`

### Advanced Training (Optional)
- [ ] Choose classifier type (SVM or Logistic Regression)
- [ ] Set confidence threshold percentile (90-98)
- [ ] Run: `python train_model.py --classifier svm --threshold-percentile 95`
- [ ] Review training logs
- [ ] Check classification report
- [ ] Verify embedding dimension is 512

### Training Output Verification
- [ ] `face_classifier.pkl` exists
- [ ] `label_encoder.pkl` exists
- [ ] `model_metadata.pkl` exists
- [ ] No "invalid load key" errors
- [ ] No embedding dimension mismatches
- [ ] Confidence threshold calculated successfully

## Post-Training Checklist

### Model Testing
- [ ] Test single image: `python test_trained_model.py --image path/to/image.jpg`
- [ ] Test entire dataset: `python test_trained_model.py --test-all`
- [ ] Overall accuracy > 90%
- [ ] No unexpected "Unknown" predictions for training data
- [ ] Review misclassifications (if any)

### Integration Testing
- [ ] Backend starts without errors: `python app.py`
- [ ] Model loads successfully (check logs)
- [ ] No "Model not found" errors
- [ ] No embedding dimension errors
- [ ] API endpoints respond correctly

### Live Testing
- [ ] Frontend starts: `cd frontend && npm run dev`
- [ ] Login as Instructor
- [ ] Create attendance session
- [ ] Camera preview works
- [ ] Face detection works (green box around face)
- [ ] Recognition works (student ID displayed)
- [ ] Confidence scores are reasonable (>0.80 for known faces)
- [ ] Unknown faces detected correctly
- [ ] Attendance records saved to database

### Performance Verification
- [ ] Recognition speed < 500ms per frame
- [ ] No memory leaks during extended use
- [ ] CPU/GPU usage is reasonable
- [ ] No crashes or freezes
- [ ] Logs show no errors

## Troubleshooting Checklist

### If Training Fails
- [ ] Check dataset structure matches requirements
- [ ] Verify all images are valid (not corrupted)
- [ ] Ensure sufficient images per student (3+ minimum)
- [ ] Check Python version (3.9+ required)
- [ ] Verify all dependencies installed
- [ ] Review error messages in console
- [ ] Check disk space for model files

### If Accuracy is Low (<90%)
- [ ] Add more training images per student
- [ ] Remove poor quality images
- [ ] Ensure diverse poses and lighting
- [ ] Check for mislabeled data (wrong folders)
- [ ] Verify student IDs are correct
- [ ] Consider retraining with different threshold

### If Recognition Fails
- [ ] Verify model files exist and are not corrupted
- [ ] Check embedding dimension is 512
- [ ] Ensure backend loaded model successfully
- [ ] Test with training images first
- [ ] Check camera quality and lighting
- [ ] Verify face detection is working
- [ ] Review confidence threshold setting

### If "Unknown" Predictions are Too Frequent
- [ ] Increase threshold percentile (e.g., 98)
- [ ] Retrain model: `python train_model.py --threshold-percentile 98`
- [ ] Add more training images
- [ ] Improve training image quality
- [ ] Check lighting conditions match training data

### If False Positives Occur
- [ ] Decrease threshold percentile (e.g., 90)
- [ ] Retrain model: `python train_model.py --threshold-percentile 90`
- [ ] Add more diverse training images
- [ ] Ensure training data quality
- [ ] Consider using SVM instead of Logistic Regression

## Retraining Checklist

### When to Retrain
- [ ] Adding new students
- [ ] Recognition accuracy has degraded
- [ ] Better quality images available
- [ ] Threshold needs adjustment
- [ ] Switching classifier type

### Retraining Steps
- [ ] Backup current model files (optional)
- [ ] Update dataset with new images
- [ ] Validate updated dataset
- [ ] Run training script
- [ ] Test new model
- [ ] Compare accuracy with old model
- [ ] Deploy if accuracy improved
- [ ] Restart backend server

## Deployment Checklist

### Pre-Deployment
- [ ] Model tested thoroughly
- [ ] Accuracy meets requirements (>90%)
- [ ] Performance is acceptable
- [ ] No known bugs or issues
- [ ] Documentation updated
- [ ] Backup of working model created

### Deployment
- [ ] Copy model files to production server
- [ ] Update backend configuration if needed
- [ ] Restart backend service
- [ ] Verify model loads successfully
- [ ] Test with production data
- [ ] Monitor logs for errors
- [ ] Test all user roles (Admin, Instructor, Student)

### Post-Deployment
- [ ] Monitor recognition accuracy
- [ ] Track false positive/negative rates
- [ ] Collect user feedback
- [ ] Log problematic cases
- [ ] Plan retraining if needed
- [ ] Document any issues

## Maintenance Checklist

### Regular Maintenance
- [ ] Review recognition logs weekly
- [ ] Monitor accuracy metrics
- [ ] Collect problematic cases
- [ ] Update training data as needed
- [ ] Retrain model quarterly (or as needed)
- [ ] Keep documentation updated

### When Issues Arise
- [ ] Document the issue
- [ ] Collect example images
- [ ] Test with current model
- [ ] Determine if retraining needed
- [ ] Update dataset if necessary
- [ ] Retrain and test
- [ ] Deploy updated model
- [ ] Verify issue resolved

## Success Criteria

Your training is successful when:

✅ Training completes without errors
✅ Test accuracy > 90%
✅ Model files generated correctly
✅ Backend loads model successfully
✅ Live recognition works in frontend
✅ Known faces recognized correctly (>90%)
✅ Unknown faces detected appropriately
✅ Confidence scores are reasonable
✅ Performance is acceptable (<500ms)
✅ No crashes or errors in production

## Quick Reference

### Essential Commands

```bash
# Validate dataset
cd backend && venv\Scripts\activate
python prepare_dataset.py --validate

# Train model (quick)
train_model.bat

# Train model (advanced)
python train_model.py --classifier svm --threshold-percentile 95

# Test model
python test_trained_model.py --test-all

# Start backend
python app.py
```

### File Locations

- Dataset: `backend/dataset/`
- Models: `backend/models/Classifier/`
- Training script: `backend/train_model.py`
- Validation script: `backend/prepare_dataset.py`
- Test script: `backend/test_trained_model.py`

### Documentation

- Quick Start: `TRAINING_QUICK_START.md`
- Full Guide: `TRAINING_GUIDE.md`
- Summary: `TRAINING_SUMMARY.md`
- This Checklist: `TRAINING_CHECKLIST.md`

---

**Note**: Check off items as you complete them. If any item fails, refer to the troubleshooting section or relevant documentation.
