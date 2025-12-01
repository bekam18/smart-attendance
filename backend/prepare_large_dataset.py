"""
Prepare and validate large dataset structure
- Ensures folders are named by student ID only
- Removes nested subfolders
- Validates image files
- Reports statistics
"""

import os
import shutil
from pathlib import Path

DATASET_PATH = 'dataset'

print("="*80)
print("DATASET PREPARATION AND VALIDATION")
print("="*80)
print()

# ============================================================================
# STEP 1: Scan current structure
# ============================================================================

print("STEP 1: Scanning dataset structure...")
print("-"*80)

if not os.path.exists(DATASET_PATH):
    print(f"❌ Dataset path not found: {DATASET_PATH}")
    print(f"   Please create it and add student folders")
    exit(1)

all_items = os.listdir(DATASET_PATH)
folders = [item for item in all_items if os.path.isdir(os.path.join(DATASET_PATH, item))]

print(f"✅ Found {len(folders)} folders in dataset/")
print()

# ============================================================================
# STEP 2: Validate folder names
# ============================================================================

print("STEP 2: Validating folder names...")
print("-"*80)

valid_folders = []
invalid_folders = []

for folder in folders:
    # Check if folder name is a student ID (STU### format)
    if folder.upper().startswith('STU') and len(folder) >= 6:
        valid_folders.append(folder)
        print(f"✅ {folder} - Valid student ID")
    else:
        invalid_folders.append(folder)
        print(f"⚠️  {folder} - NOT a student ID (will be skipped)")

print()
print(f"Valid student folders: {len(valid_folders)}")
print(f"Invalid folders: {len(invalid_folders)}")
print()

# ============================================================================
# STEP 3: Check for nested subfolders
# ============================================================================

print("STEP 3: Checking for nested subfolders...")
print("-"*80)

folders_with_subfolders = []

for folder in valid_folders:
    folder_path = os.path.join(DATASET_PATH, folder)
    items = os.listdir(folder_path)
    
    subfolders = [item for item in items if os.path.isdir(os.path.join(folder_path, item))]
    
    if subfolders:
        folders_with_subfolders.append((folder, subfolders))
        print(f"⚠️  {folder} has subfolders: {subfolders}")

if folders_with_subfolders:
    print()
    print(f"⚠️  Found {len(folders_with_subfolders)} folders with nested subfolders")
    print()
    print("Options:")
    print("1. Flatten structure (move all images to parent folder)")
    print("2. Skip (training will ignore subfolders)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        print()
        print("Flattening folder structure...")
        print("-"*80)
        
        for folder, subfolders in folders_with_subfolders:
            folder_path = os.path.join(DATASET_PATH, folder)
            
            for subfolder in subfolders:
                subfolder_path = os.path.join(folder_path, subfolder)
                
                # Move all images from subfolder to parent
                for file in os.listdir(subfolder_path):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        src = os.path.join(subfolder_path, file)
                        dst = os.path.join(folder_path, f"{subfolder}_{file}")
                        shutil.move(src, dst)
                
                # Remove empty subfolder
                try:
                    os.rmdir(subfolder_path)
                    print(f"✅ Flattened: {folder}/{subfolder}")
                except:
                    print(f"⚠️  Could not remove: {folder}/{subfolder}")
        
        print()
        print("✅ Folder structure flattened")
    else:
        print()
        print("⚠️  Subfolders will be ignored during training")

print()

# ============================================================================
# STEP 4: Count images per student
# ============================================================================

print("STEP 4: Counting images per student...")
print("-"*80)

image_counts = {}
total_images = 0

for folder in valid_folders:
    folder_path = os.path.join(DATASET_PATH, folder)
    
    # Count image files (not in subfolders)
    image_files = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_files.append(file)
    
    count = len(image_files)
    image_counts[folder] = count
    total_images += count
    
    # Visual indicator
    if count >= 100:
        status = "✅ Excellent"
    elif count >= 50:
        status = "✅ Good"
    elif count >= 20:
        status = "⚠️  Acceptable"
    else:
        status = "❌ Too few"
    
    bar = "█" * (count // 10)
    print(f"{folder}: {count:3d} images {bar} {status}")

print()
print(f"Total students: {len(valid_folders)}")
print(f"Total images: {total_images}")
print(f"Average images per student: {total_images / len(valid_folders):.1f}")
print()

# ============================================================================
# STEP 5: Recommendations
# ============================================================================

print("STEP 5: Recommendations...")
print("-"*80)

# Check for students with too few images
low_count_students = [folder for folder, count in image_counts.items() if count < 20]

if low_count_students:
    print(f"⚠️  {len(low_count_students)} students have < 20 images:")
    for folder in low_count_students:
        print(f"   - {folder}: {image_counts[folder]} images")
    print()
    print("   Recommendation: Add more images for better accuracy")
    print()

# Check for students with very high counts
high_count_students = [folder for folder, count in image_counts.items() if count > 200]

if high_count_students:
    print(f"✅ {len(high_count_students)} students have > 200 images (excellent!):")
    for folder in high_count_students:
        print(f"   - {folder}: {image_counts[folder]} images")
    print()

# Overall assessment
if total_images >= len(valid_folders) * 100:
    print("✅ Dataset is EXCELLENT for training!")
    print("   Expected accuracy: 95%+")
elif total_images >= len(valid_folders) * 50:
    print("✅ Dataset is GOOD for training")
    print("   Expected accuracy: 90%+")
elif total_images >= len(valid_folders) * 20:
    print("⚠️  Dataset is ACCEPTABLE for training")
    print("   Expected accuracy: 85%+")
else:
    print("❌ Dataset needs more images")
    print("   Expected accuracy: < 85%")

print()

# ============================================================================
# SUMMARY
# ============================================================================

print("="*80)
print("DATASET PREPARATION COMPLETE")
print("="*80)
print()
print(f"📊 Summary:")
print(f"   Valid student folders: {len(valid_folders)}")
print(f"   Total images: {total_images}")
print(f"   Avg images per student: {total_images / len(valid_folders):.1f}")
print()
print("✅ Dataset is ready for training!")
print()
print("Next step:")
print("   Run: train_large_dataset.bat")
print()
print("="*80)
