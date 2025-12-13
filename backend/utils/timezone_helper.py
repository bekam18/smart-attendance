#!/usr/bin/env python3
"""
Timezone Helper for Ethiopian Time (GMT+3)
Handles proper timezone conversion for attendance timestamps
"""

from datetime import datetime, timezone, timedelta
import pytz

# Ethiopian timezone (GMT+3)
ETHIOPIAN_TZ = pytz.timezone('Africa/Addis_Ababa')
UTC_TZ = pytz.UTC

def get_ethiopian_time():
    """Get current time in Ethiopian timezone"""
    return datetime.now(ETHIOPIAN_TZ)

def get_utc_time():
    """Get current UTC time"""
    return datetime.now(UTC_TZ)

def convert_utc_to_ethiopian(utc_datetime):
    """Convert UTC datetime to Ethiopian time"""
    if utc_datetime is None:
        return None
    
    # If datetime is naive (no timezone), assume it's UTC
    if utc_datetime.tzinfo is None:
        utc_datetime = UTC_TZ.localize(utc_datetime)
    
    # Convert to Ethiopian time
    ethiopian_time = utc_datetime.astimezone(ETHIOPIAN_TZ)
    return ethiopian_time

def convert_ethiopian_to_utc(ethiopian_datetime):
    """Convert Ethiopian datetime to UTC"""
    if ethiopian_datetime is None:
        return None
    
    # If datetime is naive, assume it's Ethiopian time
    if ethiopian_datetime.tzinfo is None:
        ethiopian_datetime = ETHIOPIAN_TZ.localize(ethiopian_datetime)
    
    # Convert to UTC
    utc_time = ethiopian_datetime.astimezone(UTC_TZ)
    return utc_time

def format_ethiopian_time(utc_datetime, format_string="%Y-%m-%d %H:%M:%S"):
    """Format UTC datetime as Ethiopian time string"""
    if utc_datetime is None:
        return ""
    
    ethiopian_time = convert_utc_to_ethiopian(utc_datetime)
    return ethiopian_time.strftime(format_string)

def format_time_for_display(utc_datetime):
    """Format time for display in attendance list (Ethiopian time)"""
    if utc_datetime is None:
        return ""
    
    ethiopian_time = convert_utc_to_ethiopian(utc_datetime)
    return ethiopian_time.strftime("%I:%M:%S %p")  # 12-hour format with AM/PM

def get_current_ethiopian_timestamp():
    """Get current timestamp in Ethiopian time for database storage"""
    # Store as UTC but return Ethiopian time for display
    return get_utc_time()

def test_timezone_conversion():
    """Test timezone conversion functions"""
    print("Timezone Conversion Test")
    print("=" * 40)
    
    # Current times
    utc_now = get_utc_time()
    ethiopian_now = get_ethiopian_time()
    
    print(f"Current UTC time: {utc_now}")
    print(f"Current Ethiopian time: {ethiopian_now}")
    print(f"Time difference: {(ethiopian_now.utcoffset().total_seconds() / 3600):.1f} hours")
    
    # Test conversion
    converted_ethiopian = convert_utc_to_ethiopian(utc_now)
    print(f"UTC converted to Ethiopian: {converted_ethiopian}")
    
    # Test formatting
    formatted_time = format_time_for_display(utc_now)
    print(f"Formatted for display: {formatted_time}")
    
    return True

if __name__ == "__main__":
    test_timezone_conversion()