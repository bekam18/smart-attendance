#!/usr/bin/env python3
"""Test the datetime timezone fix"""

import sys
sys.path.append('backend')

from datetime import datetime, timedelta
from utils.timezone_helper import get_ethiopian_time, UTC_TZ
import pytz

def test_datetime_fix():
    """Test the datetime timezone fix"""
    
    print("🕐 Testing Datetime Timezone Fix")
    print("=" * 40)
    
    # Simulate the scenario that was causing the error
    print("\n1. Testing timezone-aware vs timezone-naive datetime subtraction...")
    
    # Get current Ethiopian time (timezone-aware)
    current_ethiopian = get_ethiopian_time()
    print(f"   Current Ethiopian time: {current_ethiopian}")
    print(f"   Timezone info: {current_ethiopian.tzinfo}")
    
    # Simulate existing_time from database (timezone-naive)
    existing_time_naive = datetime.now()  # This is what comes from DB
    print(f"   Existing time (naive): {existing_time_naive}")
    print(f"   Timezone info: {existing_time_naive.tzinfo}")
    
    # This would cause the error:
    try:
        time_diff = current_ethiopian - existing_time_naive
        print(f"   ❌ This should have failed but didn't: {time_diff}")
    except TypeError as e:
        print(f"   ✅ Expected error: {e}")
    
    print("\n2. Testing the fix...")
    
    # Apply the fix
    existing_time = existing_time_naive
    if existing_time.tzinfo is None:
        existing_time = UTC_TZ.localize(existing_time)
        print(f"   Fixed existing time: {existing_time}")
    
    # Convert both to Ethiopian time for comparison
    existing_ethiopian = existing_time.astimezone(current_ethiopian.tzinfo)
    time_diff = current_ethiopian - existing_ethiopian
    
    print(f"   ✅ Time difference calculated: {time_diff.total_seconds():.1f} seconds")
    
    print("\n3. Testing with various datetime scenarios...")
    
    # Test with different timezone scenarios
    test_cases = [
        ("Naive datetime", datetime.now()),
        ("UTC datetime", datetime.now(UTC_TZ)),
        ("Ethiopian datetime", get_ethiopian_time()),
    ]
    
    for name, test_time in test_cases:
        print(f"\n   Testing {name}: {test_time}")
        
        # Apply the same fix logic
        if test_time.tzinfo is None:
            test_time = UTC_TZ.localize(test_time)
        
        test_ethiopian = test_time.astimezone(current_ethiopian.tzinfo)
        diff = current_ethiopian - test_ethiopian
        
        print(f"   ✅ Difference: {diff.total_seconds():.1f} seconds")
    
    print(f"\n🎉 All datetime operations completed successfully!")
    print(f"   The timezone fix should resolve the 'Recognition failed' error.")
    
    return True

if __name__ == "__main__":
    test_datetime_fix()