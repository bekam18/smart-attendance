# Fix 500 Errors - Quick Guide

## 🚀 Quick Diagnosis

Run this command to diagnose the issue:

```bash
cd backend
venv\Scripts\activate
python test_model_loading.py
```

This will show you exactly what's wrong.

## ✅ Most Common Fix

The backend needs to be **restarted** after training to load the new model:

```bash
# In your backend terminal:
# Press Ctrl+C to stop

# Then restart:
python app.py
```

You should see:
```
✅ [Loader] Loaded classifier from models\Classifier\face_classifier_v1.pkl
✅ [Loader] Detected new model format with metadata
✅ [Loader] Embedding dim: 512
```

## 🔍 If Still Getting 500 Errors

### Check 1: Dependencies Installed?

```bash
pip list | findstr torch
pip list | findstr facenet
```

Should show:
- `torch`
- `torchvision`
- `facenet-pytorch`

If missing:
```bash
pip install torch torchvision facenet-pytorch
```

### Check 2: Model Files Exist?

```bash
dir models\Classifier
```

Should show:
- `face_classifier_v1.pkl`
- `label_encoder_classes.npy`

If missing, train the model:
```bash
python train_production_model.py
```

### Check 3: Backend Logs

Look at your backend terminal for errors. Common ones:

**"ModuleNotFoundError: No module named 'torch'"**
→ Install: `pip install torch torchvision facenet-pytorch`

**"Model not found"**
→ Train model: `python train_production_model.py`

**"Embedding dimension mismatch"**
→ Retrain model with new script

## 📋 Complete Fix Procedure

```bash
# 1. Stop backend (Ctrl+C)

# 2. Run diagnostics
cd backend
venv\Scripts\activate
python test_model_loading.py

# 3. Fix any issues shown

# 4. Restart backend
python app.py

# 5. Test in frontend
```

## 🎯 Expected Backend Output

When working correctly, you should see:

```
🔍 [Loader] Model directory: models\Classifier
✅ [Loader] Loaded classifier from models\Classifier\face_classifier_v1.pkl
✅ [Loader] Detected new model format with metadata
✅ [Loader] Classifier type: SVC
✅ [Loader] Embedding dim: 512
✅ [Loader] Threshold: 0.9707
✅ [Loader] Num classes: 19
✅ [Loader] All models loaded successfully!
🚀 SmartAttendance API running on http://0.0.0.0:5000
```

## 📚 Detailed Documentation

For comprehensive debugging, see:
- **[DEBUGGING_500_ERRORS.md](DEBUGGING_500_ERRORS.md)** - Complete debugging guide

## ⚡ TL;DR

1. **Run diagnostics**: `python test_model_loading.py`
2. **Restart backend**: Stop (Ctrl+C) and run `python app.py`
3. **Check logs**: Look for "✅ Model loaded successfully"
4. **Test frontend**: Try face recognition again

**Most likely you just need to restart the backend!** 🚀
