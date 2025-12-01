# Dataset Directory

This directory contains training images for the face recognition model.

## Structure

Organize your images like this:

```
dataset/
├── STU001/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   ├── photo3.jpg
│   └── photo4.jpg
├── STU002/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── image3.jpg
├── STU003/
│   ├── face1.png
│   ├── face2.png
│   └── face3.png
└── ...
```

## Requirements

### Folder Names
- Use **student IDs** as folder names
- Must match the student IDs in MongoDB
- Examples: `STU001`, `STU002`, `2024001`, etc.

### Images
- **Format**: JPG, JPEG, or PNG
- **Quantity**: 3-5 minimum per student, 10+ recommended
- **Quality**: Clear, well-lit faces
- **Resolution**: At least 160x160 pixels
- **Content**: One face per image (frontal or near-frontal)

### Image Guidelines

✅ **Good Images:**
- Clear, sharp focus
- Good lighting (not too dark or bright)
- Frontal face view
- Neutral or natural expression
- No obstructions (glasses OK, sunglasses not OK)
- Plain or simple background

❌ **Avoid:**
- Blurry or out-of-focus images
- Very dark or overexposed images
- Side profiles or extreme angles
- Sunglasses, masks, or face coverings
- Multiple faces in one image
- Very low resolution (<160x160)

## Example Dataset

For 3 students with 5 images each:

```
dataset/
├── STU001/
│   ├── front_1.jpg
│   ├── front_2.jpg
│   ├── slight_left.jpg
│   ├── slight_right.jpg
│   └── smiling.jpg
├── STU002/
│   ├── neutral_1.jpg
│   ├── neutral_2.jpg
│   ├── indoor.jpg
│   ├── outdoor.jpg
│   └── different_lighting.jpg
└── STU003/
    ├── photo_1.jpg
    ├── photo_2.jpg
    ├── photo_3.jpg
    ├── photo_4.jpg
    └── photo_5.jpg
```

## Validation

Before training, validate your dataset:

```bash
cd backend
venv\Scripts\activate
python prepare_dataset.py --validate
```

This will check:
- Directory structure
- Image formats
- Image quality
- Number of images per student
- Any issues or warnings

## Tips for Best Results

1. **Diversity**: Include images with:
   - Different lighting conditions
   - Various facial expressions
   - Slight pose variations
   - Different times/days

2. **Consistency**: Ensure:
   - Similar image quality across students
   - Comparable number of images per student
   - Consistent naming convention

3. **Quality over Quantity**:
   - 5 high-quality images > 20 poor-quality images
   - Remove blurry or problematic images
   - Retake photos if needed

4. **Testing**:
   - Keep some images aside for testing
   - Test with real-world conditions
   - Verify recognition accuracy

## Getting Started

1. Create student folders:
   ```bash
   mkdir STU001 STU002 STU003
   ```

2. Add images to each folder

3. Validate dataset:
   ```bash
   python prepare_dataset.py --validate
   ```

4. Train model:
   ```bash
   python train_model.py
   ```

## Need Help?

See the training guides:
- Quick start: `TRAINING_QUICK_START.md`
- Full guide: `TRAINING_GUIDE.md`
- Summary: `TRAINING_SUMMARY.md`
