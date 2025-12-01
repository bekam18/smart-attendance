"""
Simple retraining script using existing backend infrastructure
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, 'backend')

# Now run the existing training script
from train_production_model import main

if __name__ == '__main__':
    print("=" * 70)
    print("RUNNING PRODUCTION MODEL TRAINING")
    print("=" * 70)
    print()
    main()
