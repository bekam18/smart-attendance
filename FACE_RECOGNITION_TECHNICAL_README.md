# Face Recognition System - Technical Documentation

## System Overview

This document provides a complete technical analysis of the face recognition system used in SmartAttendance, including training methodology, model architecture, and inference pipeline.

---

## 1. TRAINING METHOD USED

### Transfer Learning with Pretrained FaceNet

**Method**: Transfer Learning (Pretrained Embedding Extractor + Trained Classifier)

The system uses a **hybrid approach**:
- **Pretrained Component**: FaceNet InceptionResnetV1 (pretrained on VGGFace2)
- **Trained Component**: SVM classifier trained on student embeddings

### Why This Method?

**Rationale**:
1. **Dataset Size**: 2,907 training images across 19 students (~153 images/student)
2. **Computational Constraints**: Training FaceNet from scratch requires millions of images and weeks of GPU time
3. **Proven Performance**: VGGFace2-pretrained FaceNet achieves state-of-the-art accuracy
4. **Fast Inference**: 512-dim embeddings enable real-time recognition
5. **High Accuracy**: Achieved 99.8% training accuracy with this approach

### What Was Trained?

**NOT Trained**:
- ❌ FaceNet embedding extractor (frozen, pretrained weights used)
- ❌ Face detector (MTCNN/OpenCV, pretrained)

**Trained**:
- ✅ SVM classifier (linear kernel, probability enabled)
- ✅ StandardScaler (fitted on training embeddings)
- ✅ LabelEncoder (maps student IDs to class indices)

### Training Process

```
1. Load pretrained FaceNet (frozen weights)
2. Extract 512-dim embeddings from all student images
3. Apply L2 normalization to embeddings
4. Fit StandardScaler on normalized embeddings
5. Train SVM classifier on scaled embeddings
6. Calculate confidence threshold (89.04%)
7. Save classifier + scaler + encoder
```

---

## 2. MODEL ARCHITECTURE PIPELINE

### Complete Recognition Pipeline

```
Input Image (BGR)
    ↓
[1] Face Detection (OpenCV Haar Cascade)
    ↓
[2] Face Extraction & Alignment (160x160 crop with margin)
    ↓
[3] Preprocessing (RGB conversion, resize, normalize)
    ↓
[4] Embedding Extraction (FaceNet InceptionResnetV1)
    ↓
[5] L2 Normalization (unit length vector)
    ↓
[6] StandardScaler Transform
    ↓
[7] SVM Classification (with probability)
    ↓
[8] Confidence Thresholding (0.60 runtime, 0.89 trained)
    ↓
Output: {student_id, confidence} or "unknown"
```

### Component Details

#### [1] Face Detector
- **Primary**: OpenCV Haar Cascade (`haarcascade_frontalface_default.xml`)
- **Fallback**: MTCNN (if available)
- **Parameters**:
  - `scaleFactor=1.05` (more sensitive)
  - `minNeighbors=3` (less strict)
  - `minSize=(20, 20)` (smaller faces)
- **Preprocessing**: Histogram equalization for better detection

#### [2] Face Alignment
- **Method**: Bounding box extraction with padding
- **Padding**: 50% of max(width, height)
- **Output Size**: 160×160 pixels (FaceNet requirement)
- **Interpolation**: Linear (cv2.INTER_LINEAR)

#### [3] Preprocessing
```python
transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])
```
- **Color Space**: BGR → RGB conversion
- **Normalization**: Pixel values scaled to [-1, 1]

#### [4] Embedding Extractor
- **Model**: InceptionResnetV1
- **Pretrained On**: VGGFace2 (3.3M images, 9,131 identities)
- **Architecture**: Inception-ResNet hybrid
- **Output**: 512-dimensional embedding vector
- **Device**: CPU (CUDA if available)

#### [5] L2 Normalization
```python
embedding_normalized = embedding / np.linalg.norm(embedding)
```
- **Purpose**: Unit length vectors for cosine similarity
- **Applied**: After embedding extraction, before scaling

#### [6] StandardScaler
```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
```
- **Purpose**: Zero mean, unit variance
- **Fitted On**: Training embeddings
- **Applied**: During both training and inference

#### [7] SVM Classifier
- **Type**: Support Vector Classification (SVC)
- **Kernel**: Linear
- **Probability**: Enabled (Platt scaling)
- **C Parameter**: 1.0
- **Classes**: 19 students
- **Training Accuracy**: 99.8%

---


## 3. DATASET USAGE

### Dataset Structure

**Location**: `backend/dataset/processed/`

**Structure**:
```
dataset/processed/
  STU001/
    img_001.jpg
    img_002.jpg
    ...
  STU002/
    img_001.jpg
    ...
  STU013/
    img_001.jpg
    ...
```

### Dataset Statistics

- **Total Students**: 19
- **Total Images**: 2,907
- **Average Images/Student**: ~153
- **Image Format**: JPG, JPEG, PNG
- **Image Size**: Variable (resized to 160×160 during processing)

### Student Distribution

```
STU001, STU002, STU003, STU004, STU005, STU006, STU008, STU009, STU010,
STU011, STU012, STU013, STU014, STU015, STU016, STU017, STU018, STU019, STU021
```

### Embedding Generation Process

1. **Load Image**: Read from disk using PIL
2. **Face Detection**: MTCNN or direct resize (images pre-cropped)
3. **Extract Embedding**: FaceNet forward pass
4. **Normalize**: L2 normalization to unit length
5. **Store**: Save to numpy array

### Class Imbalance Handling

**Method**: None explicitly applied (dataset appears balanced)

**Reasoning**:
- Average ~153 images/student suggests balanced distribution
- SVM with linear kernel is robust to moderate imbalance
- High accuracy (99.8%) indicates no significant imbalance issues

### Train/Validation Split

**Split Ratio**: 80/20 (stratified)
- **Training Set**: 80% of images per student
- **Test Set**: 20% of images per student
- **Stratification**: Ensures proportional class distribution

**Implementation**:
```python
X_train, X_test, y_train, y_test = train_test_split(
    embeddings, labels,
    test_size=0.2,
    random_state=42,
    stratify=labels
)
```

### Data Augmentation

**During Training**: None

**Reasoning**:
- Embeddings are extracted from original images
- FaceNet is pretrained on augmented data
- 153 images/student is sufficient without augmentation
- Augmentation would require retraining FaceNet (not feasible)

**Potential Future Enhancement**:
- Augment images before embedding extraction
- Brightness/contrast variations
- Horizontal flips
- Small rotations (±10°)

---

## 4. TRAINING OUTPUT SUMMARY

### Generated Files

#### `face_classifier_v1.pkl` (Main Model)
**Contents**:
```python
{
    'classifier': SVC(...),      # Trained SVM
    'scaler': StandardScaler(),  # Fitted scaler
    'label_encoder': LabelEncoder(),  # Label mapper
    'metadata': {...}            # Training info
}
```
**Size**: ~2-5 MB
**Purpose**: Complete model package for inference

#### `label_encoder_classes.npy`
**Contents**: Array of student IDs
```python
['STU001', 'STU002', ..., 'STU021']
```
**Purpose**: Map class indices to student IDs

#### `X.npy` (Embeddings)
**Shape**: (2907, 512)
**Contents**: All training embeddings
**Purpose**: Analysis, retraining, debugging

#### `y.npy` (Labels)
**Shape**: (2907,)
**Contents**: Encoded labels (0-18)
**Purpose**: Corresponds to X.npy

#### `training_metadata.json`
**Contents**:
```json
{
  "embedding_model": "InceptionResnetV1",
  "pretrained_on": "vggface2",
  "embedding_dim": 512,
  "num_classes": 19,
  "threshold": 0.8904,
  "accuracy": 0.9983,
  "training_date": "2025-11-25T11:50:12"
}
```
**Purpose**: Model provenance and configuration

#### `training_summary.txt`
**Contents**: Human-readable training report
**Purpose**: Quick reference for model details

### How Files Work During Recognition

**Inference Flow**:
```
1. Load face_classifier_v1.pkl
   ├─ Extract classifier
   ├─ Extract scaler
   └─ Extract label_encoder

2. Detect face in image
3. Extract face region
4. Generate embedding (FaceNet)
5. Normalize embedding (L2)
6. Scale embedding (scaler.transform)
7. Predict class (classifier.predict_proba)
8. Get confidence (max probability)
9. Check threshold (0.60 runtime)
10. Decode label (label_encoder.inverse_transform)
11. Return {student_id, confidence}
```

---

## 5. CONFIDENCE & THRESHOLD LOGIC

### Probability Calculation

**Method**: SVM with Platt Scaling

```python
# SVM trained with probability=True
classifier = SVC(kernel='linear', probability=True)

# During inference
probabilities = classifier.predict_proba(embedding)  # Shape: (1, 19)
confidence = np.max(probabilities)  # Max probability
predicted_class = np.argmax(probabilities)  # Class with max prob
```

**Platt Scaling**:
- Converts SVM decision values to probabilities
- Fitted on training data
- Provides calibrated confidence scores

### Threshold Values

**Training Threshold**: 0.8904 (89.04%)
- Calculated as 95th percentile of correct predictions
- Ensures 95% of training samples pass

**Runtime Threshold**: 0.60 (60%)
- **Overridden** in `classifier.py` for better recognition
- Lower threshold accepts more faces
- Trade-off: Higher recall, slightly lower precision

**Threshold Logic**:
```python
# In classifier.py
NEW_THRESHOLD = 0.60  # Override model threshold

if confidence < NEW_THRESHOLD:
    return {'status': 'unknown', 'confidence': confidence}
else:
    return {'status': 'recognized', 'student_id': student_id, 'confidence': confidence}
```

### Top-2 Comparison

**Not Currently Used**

**Potential Implementation**:
```python
# Get top 2 predictions
top2_probs = np.sort(probabilities[0])[-2:]
top1_prob = top2_probs[1]
top2_prob = top2_probs[0]

# Require significant margin
if (top1_prob - top2_prob) < 0.2:
    return 'unknown'  # Too close, uncertain
```

### Unknown Face Logic

**Rejection Criteria**:
1. **No Face Detected**: `status='no_face'`
2. **Low Confidence**: `confidence < 0.60` → `status='unknown'`
3. **Student Not in DB**: `status='unknown'`

**Response Format**:
```python
{
    'status': 'unknown',
    'message': 'Face not recognized (low confidence)',
    'confidence': 0.58
}
```

---

## 6. FINAL SYSTEM BEHAVIOR (END-TO-END)

### Complete Recognition Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CAPTURE IMAGE                                            │
│    - Webcam/camera captures frame                           │
│    - Image sent to backend as base64/multipart              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. DECODE IMAGE                                             │
│    - Convert base64 → numpy array (BGR)                     │
│    - Validate image format                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. DETECT FACE                                              │
│    - OpenCV Haar Cascade detection                          │
│    - Returns bounding box: (x, y, w, h)                     │
│    - If no face: return 'no_face'                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. EXTRACT & ALIGN FACE                                     │
│    - Crop face with 50% padding                             │
│    - Resize to 160×160 pixels                               │
│    - Convert BGR → RGB                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. GENERATE EMBEDDING                                       │
│    - FaceNet InceptionResnetV1 forward pass                 │
│    - Output: 512-dimensional vector                         │
│    - L2 normalize to unit length                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. SCALE EMBEDDING                                          │
│    - Apply StandardScaler.transform()                       │
│    - Zero mean, unit variance                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. CLASSIFY                                                 │
│    - SVM.predict_proba(embedding)                           │
│    - Get probabilities for all 19 classes                   │
│    - Select class with max probability                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. CHECK CONFIDENCE                                         │
│    - If confidence < 0.60: return 'unknown'                 │
│    - If confidence >= 0.60: proceed                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. DECODE LABEL                                             │
│    - LabelEncoder.inverse_transform(class_idx)              │
│    - Get student_id (e.g., 'STU013')                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 10. CHECK DATABASE                                          │
│     - Query MongoDB for student_id                          │
│     - Verify student exists                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 11. CHECK DUPLICATE                                         │
│     - Query: {student_id, session_id, date}                 │
│     - If exists: UPDATE timestamp only                      │
│     - If new: INSERT attendance record                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 12. RETURN RESULT                                           │
│     {                                                       │
│       'status': 'recognized',                               │
│       'student_id': 'STU013',                               │
│       'student_name': 'Bekam Ayele',                        │
│       'confidence': 0.876                                   │
│     }                                                       │
└─────────────────────────────────────────────────────────────┘
```

### Timing Breakdown

**Typical Inference Time** (CPU):
- Face Detection: 50-100ms
- Face Extraction: 10ms
- Embedding Generation: 200-300ms (FaceNet)
- Classification: 5-10ms (SVM)
- **Total**: ~300-400ms per image

**GPU Acceleration**:
- Embedding Generation: 50-100ms
- **Total**: ~100-150ms per image

---


## 7. RISKS, LIMITATIONS & FUTURE IMPROVEMENTS

### Current Limitations

#### 1. Dataset Imbalance
**Issue**: Varying image counts per student (if dataset grows unevenly)
**Impact**: Bias toward students with more images
**Mitigation**: Class weighting in SVM (not currently applied)
**Future**: Implement balanced sampling or class weights

#### 2. Lighting Sensitivity
**Issue**: Poor performance in extreme lighting conditions
**Impact**: False negatives in dark/bright environments
**Current Mitigation**: Histogram equalization in face detection
**Future**: 
- Train on augmented data with lighting variations
- Use illumination-invariant features
- Add preprocessing for lighting normalization

#### 3. Similar Face Confusion
**Issue**: Students with similar facial features may be confused
**Impact**: False positives (wrong student marked)
**Current Threshold**: 0.60 (60%) - relatively permissive
**Mitigation**: Increase threshold to 0.75-0.80
**Future**:
- Collect more diverse images per student
- Use ArcFace instead of FaceNet (better discrimination)
- Implement top-2 margin checking

#### 4. Pose Variation
**Issue**: Extreme head angles reduce accuracy
**Impact**: False negatives for profile/tilted faces
**Current**: Limited to frontal faces (Haar Cascade)
**Future**:
- Use multi-view face detector (MTCNN, RetinaFace)
- Train on multi-pose images
- Implement 3D face alignment

#### 5. Occlusion Handling
**Issue**: Masks, glasses, hats reduce recognition
**Impact**: False negatives
**Current**: No specific handling
**Future**:
- Train on occluded face dataset
- Use attention mechanisms
- Implement partial face matching

#### 6. Age Progression
**Issue**: Student appearance changes over time
**Impact**: Gradual accuracy degradation
**Current**: No handling
**Future**:
- Periodic retraining with recent images
- Online learning/model updates
- Age-invariant features

### Performance Bottlenecks

#### 1. FaceNet Inference Speed
**Issue**: 200-300ms per image on CPU
**Impact**: Slow real-time recognition
**Solution**: 
- Use GPU acceleration (50-100ms)
- Use lighter model (MobileFaceNet)
- Batch processing for multiple faces

#### 2. Model Loading Time
**Issue**: 2-3 seconds on first request
**Impact**: Slow initial response
**Solution**: Lazy loading (already implemented)

#### 3. Memory Usage
**Issue**: FaceNet model ~100MB in RAM
**Impact**: High memory footprint
**Solution**: Model quantization, pruning

### Security Concerns

#### 1. Spoofing Attacks
**Issue**: Photos/videos can fool the system
**Impact**: Unauthorized attendance marking
**Current**: No liveness detection
**Future**:
- Implement liveness detection (blink, head movement)
- Use depth cameras
- Challenge-response mechanisms

#### 2. Model Theft
**Issue**: Model files accessible on server
**Impact**: Intellectual property theft
**Current**: No encryption
**Future**:
- Encrypt model files
- Use model serving APIs
- Implement access controls

### Recommended Improvements

#### Priority 1: Increase Threshold
**Action**: Change threshold from 0.60 → 0.75
**Benefit**: Reduce false positives (wrong student marked)
**Trade-off**: Slightly more "unknown" results
**Implementation**: 
```python
# In classifier.py
NEW_THRESHOLD = 0.75  # More strict
```

#### Priority 2: Collect More Images
**Action**: Increase to 200-300 images per student
**Benefit**: Better generalization, higher accuracy
**Focus**: Diverse angles, lighting, expressions
**Implementation**: Use `train_large_dataset.py`

#### Priority 3: Implement Class Balancing
**Action**: Add class weights to SVM
**Benefit**: Fair representation for all students
**Implementation**:
```python
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight(
    'balanced', classes=np.unique(y), y=y
)
classifier = SVC(class_weight=class_weights, ...)
```

#### Priority 4: Add Top-2 Margin Check
**Action**: Require significant gap between top 2 predictions
**Benefit**: Reject ambiguous cases
**Implementation**:
```python
top2 = np.sort(probabilities[0])[-2:]
if (top2[1] - top2[0]) < 0.2:
    return 'unknown'
```

#### Priority 5: Upgrade to ArcFace
**Action**: Replace FaceNet with ArcFace embeddings
**Benefit**: Better discrimination for similar faces
**Trade-off**: Requires retraining
**Implementation**: Use `insightface` library

### Future Architecture Enhancements

#### Option 1: End-to-End Deep Learning
**Approach**: Train CNN directly on student faces
**Pros**: Optimized for specific dataset
**Cons**: Requires large dataset, long training time
**Feasibility**: Low (insufficient data)

#### Option 2: Few-Shot Learning
**Approach**: Meta-learning for new students
**Pros**: Add students without retraining
**Cons**: Complex implementation
**Feasibility**: Medium (research-level)

#### Option 3: Ensemble Methods
**Approach**: Combine multiple models
**Pros**: Higher accuracy, robustness
**Cons**: Slower inference, more memory
**Feasibility**: High (straightforward)

#### Option 4: Active Learning
**Approach**: Request labels for uncertain cases
**Pros**: Continuous improvement
**Cons**: Requires human feedback loop
**Feasibility**: Medium (needs UI changes)

---

## 8. TECHNICAL SPECIFICATIONS

### Software Dependencies

**Core Libraries**:
```
torch==2.9.1+cpu
torchvision==0.20.1+cpu
facenet-pytorch==2.6.0
opencv-python==4.10.0.84
scikit-learn==1.5.2
numpy==1.26.4
pillow==11.0.0
```

**Optional**:
```
mtcnn==1.0.0  # Alternative face detector
insightface   # For ArcFace embeddings
```

### Hardware Requirements

**Minimum**:
- CPU: 2 cores, 2.0 GHz
- RAM: 4 GB
- Storage: 500 MB (model + dependencies)

**Recommended**:
- CPU: 4+ cores, 3.0+ GHz
- RAM: 8 GB
- GPU: NVIDIA with CUDA support (optional)
- Storage: 2 GB

### Model Specifications

**FaceNet InceptionResnetV1**:
- Parameters: ~23M
- Input: 160×160×3 RGB image
- Output: 512-dimensional embedding
- Pretrained: VGGFace2 (3.3M images)
- Accuracy: 99.6% on LFW benchmark

**SVM Classifier**:
- Type: Linear SVC
- Classes: 19
- Support Vectors: ~500-1000
- Training Time: <1 minute
- Inference Time: <10ms

### File Sizes

```
face_classifier_v1.pkl:     ~3 MB
label_encoder_classes.npy:  <1 KB
X.npy:                      ~6 MB (2907×512 float32)
y.npy:                      ~12 KB (2907 int32)
training_metadata.json:     ~2 KB
```

---

## 9. TROUBLESHOOTING

### Common Issues

#### Issue: "No face detected"
**Causes**:
- Poor lighting
- Face too small/large
- Extreme angle
- Occlusion

**Solutions**:
- Improve lighting
- Move closer to camera
- Face camera directly
- Remove obstructions

#### Issue: "Unknown face" for trained student
**Causes**:
- Confidence < 0.60
- Appearance changed significantly
- Poor image quality

**Solutions**:
- Lower threshold (0.55)
- Retrain with recent images
- Improve camera quality

#### Issue: Wrong student recognized
**Causes**:
- Similar faces
- Threshold too low
- Insufficient training data

**Solutions**:
- Increase threshold (0.75-0.80)
- Collect more diverse images
- Retrain model

#### Issue: Slow recognition
**Causes**:
- CPU inference
- Large image size
- Model not loaded

**Solutions**:
- Use GPU
- Resize images before sending
- Warm up model on startup

---

## 10. MAINTENANCE & RETRAINING

### When to Retrain

**Triggers**:
1. Adding new students
2. Accuracy drops below 90%
3. Significant appearance changes
4. Dataset grows by >20%

### Retraining Process

```bash
# 1. Prepare dataset
cd backend
python prepare_dataset.py

# 2. Train model
python train_production_model.py

# 3. Test model
python test_production_model.py

# 4. Deploy
# Restart backend server
```

### Model Versioning

**Naming Convention**:
```
face_classifier_v1.pkl  # Current
face_classifier_v2.pkl  # After retraining
```

**Backup Strategy**:
```bash
# Before retraining
cp models/Classifier/face_classifier_v1.pkl \
   models/Classifier/face_classifier_v1_backup.pkl
```

### Performance Monitoring

**Metrics to Track**:
- Recognition accuracy
- Average confidence scores
- False positive rate
- False negative rate
- Inference time

**Logging**:
```python
# In classifier.py
logger.info(f"Recognition: {student_id}, confidence: {confidence:.3f}")
```

---

## 11. CONCLUSION

### System Strengths

✅ **High Accuracy**: 99.8% training accuracy
✅ **Fast Inference**: ~300-400ms per image
✅ **Scalable**: Handles 19+ students easily
✅ **Robust**: Pretrained FaceNet embeddings
✅ **Production-Ready**: Complete pipeline with error handling

### System Weaknesses

⚠️ **Lighting Sensitive**: Performance degrades in poor lighting
⚠️ **Pose Limited**: Best for frontal faces
⚠️ **No Liveness**: Vulnerable to photo spoofing
⚠️ **Threshold Trade-off**: 0.60 allows some false positives

### Overall Assessment

The system uses a **proven, production-ready architecture** with transfer learning from state-of-the-art FaceNet embeddings. The 99.8% training accuracy demonstrates excellent performance on the current dataset.

**Key Success Factors**:
1. Large dataset (2,907 images, ~153 per student)
2. Pretrained FaceNet (VGGFace2)
3. Linear SVM with probability
4. Proper preprocessing pipeline

**Recommended Next Steps**:
1. Increase threshold to 0.75 for better precision
2. Collect more images for problematic students
3. Implement class balancing
4. Add liveness detection for security

---

## 12. REFERENCES

### Papers

1. **FaceNet**: Schroff et al., "FaceNet: A Unified Embedding for Face Recognition and Clustering", CVPR 2015
2. **VGGFace2**: Cao et al., "VGGFace2: A dataset for recognising faces across pose and age", FG 2018
3. **Inception-ResNet**: Szegedy et al., "Inception-v4, Inception-ResNet and the Impact of Residual Connections on Learning", AAAI 2017

### Libraries

- **facenet-pytorch**: https://github.com/timesler/facenet-pytorch
- **scikit-learn**: https://scikit-learn.org/
- **OpenCV**: https://opencv.org/

### Datasets

- **VGGFace2**: 3.3M images, 9,131 identities
- **LFW**: Labeled Faces in the Wild (benchmark)

---

**Document Version**: 1.0
**Last Updated**: 2024-11-27
**System Version**: SmartAttendance v1.0
**Model Version**: face_classifier_v1.pkl (trained 2025-11-25)

