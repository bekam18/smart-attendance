"""
Dataset Preparation Script
Helps organize and validate training images for face recognition
"""

import os
import sys
from pathlib import Path
from PIL import Image
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatasetPreparation:
    """Prepare and validate dataset for training"""
    
    def __init__(self, dataset_path='dataset'):
        self.dataset_path = Path(dataset_path)
        
    def create_structure(self):
        """Create dataset directory structure"""
        logger.info(f"Creating dataset directory: {self.dataset_path}")
        self.dataset_path.mkdir(parents=True, exist_ok=True)
        logger.info("✓ Dataset directory created")
        
    def validate_images(self):
        """Validate all images in dataset"""
        logger.info("Validating dataset images...")
        
        if not self.dataset_path.exists():
            logger.error(f"Dataset path not found: {self.dataset_path}")
            return False
        
        student_dirs = [d for d in self.dataset_path.iterdir() if d.is_dir()]
        
        if len(student_dirs) == 0:
            logger.warning("No student directories found")
            logger.info(f"Please create student folders in: {self.dataset_path}")
            logger.info("Example: dataset/STU001/, dataset/STU002/, etc.")
            return False
        
        total_images = 0
        total_students = 0
        issues = []
        
        for student_dir in sorted(student_dirs):
            student_id = student_dir.name
            image_files = list(student_dir.glob('*.jpg')) + \
                         list(student_dir.glob('*.jpeg')) + \
                         list(student_dir.glob('*.png'))
            
            if len(image_files) == 0:
                issues.append(f"⚠ {student_id}: No images found")
                continue
            
            if len(image_files) < 3:
                issues.append(f"⚠ {student_id}: Only {len(image_files)} images (recommend 3-5+)")
            
            valid_images = 0
            for img_path in image_files:
                try:
                    img = Image.open(img_path)
                    width, height = img.size
                    
                    if width < 160 or height < 160:
                        issues.append(f"⚠ {student_id}/{img_path.name}: Low resolution ({width}x{height})")
                    
                    valid_images += 1
                    
                except Exception as e:
                    issues.append(f"✗ {student_id}/{img_path.name}: Invalid image - {e}")
            
            if valid_images > 0:
                logger.info(f"✓ {student_id}: {valid_images} valid images")
                total_images += valid_images
                total_students += 1
        
        logger.info("\n" + "="*60)
        logger.info("DATASET VALIDATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total students: {total_students}")
        logger.info(f"Total images: {total_images}")
        
        if issues:
            logger.info(f"\nIssues found: {len(issues)}")
            for issue in issues:
                logger.info(f"  {issue}")
        else:
            logger.info("\n✓ No issues found - dataset is ready for training!")
        
        logger.info("="*60)
        
        return total_students > 0 and total_images > 0
    
    def show_statistics(self):
        """Show detailed dataset statistics"""
        if not self.dataset_path.exists():
            logger.error(f"Dataset path not found: {self.dataset_path}")
            return
        
        student_dirs = [d for d in self.dataset_path.iterdir() if d.is_dir()]
        
        if len(student_dirs) == 0:
            logger.info("No student directories found")
            return
        
        stats = []
        for student_dir in sorted(student_dirs):
            student_id = student_dir.name
            image_files = list(student_dir.glob('*.jpg')) + \
                         list(student_dir.glob('*.jpeg')) + \
                         list(student_dir.glob('*.png'))
            
            total_size = sum(f.stat().st_size for f in image_files)
            avg_size = total_size / len(image_files) if image_files else 0
            
            stats.append({
                'student_id': student_id,
                'num_images': len(image_files),
                'total_size_mb': total_size / (1024 * 1024),
                'avg_size_kb': avg_size / 1024
            })
        
        logger.info("\n" + "="*60)
        logger.info("DATASET STATISTICS")
        logger.info("="*60)
        logger.info(f"{'Student ID':<15} {'Images':<10} {'Total Size':<15} {'Avg Size'}")
        logger.info("-"*60)
        
        for stat in stats:
            logger.info(
                f"{stat['student_id']:<15} "
                f"{stat['num_images']:<10} "
                f"{stat['total_size_mb']:.2f} MB{'':<8} "
                f"{stat['avg_size_kb']:.1f} KB"
            )
        
        total_images = sum(s['num_images'] for s in stats)
        total_size = sum(s['total_size_mb'] for s in stats)
        
        logger.info("-"*60)
        logger.info(f"{'TOTAL':<15} {total_images:<10} {total_size:.2f} MB")
        logger.info("="*60)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare and validate training dataset')
    parser.add_argument('--dataset', type=str, default='dataset',
                       help='Path to dataset directory')
    parser.add_argument('--create', action='store_true',
                       help='Create dataset directory structure')
    parser.add_argument('--validate', action='store_true',
                       help='Validate dataset images')
    parser.add_argument('--stats', action='store_true',
                       help='Show dataset statistics')
    
    args = parser.parse_args()
    
    prep = DatasetPreparation(dataset_path=args.dataset)
    
    if args.create:
        prep.create_structure()
    
    if args.validate or (not args.create and not args.stats):
        prep.validate_images()
    
    if args.stats:
        prep.show_statistics()


if __name__ == '__main__':
    main()
