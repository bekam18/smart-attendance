#!/usr/bin/env python3
"""
Time-based restrictions for the attendance system
"""
from datetime import datetime, time
from typing import Tuple, Dict, Any

def is_within_working_hours(current_time: datetime = None) -> Dict[str, Any]:
    """
    Check if current time is within official working hours
    
    Working Hours:
    - Morning: 8:30 AM - 12:30 PM
    - Lunch Break: 12:30 PM - 1:30 PM (BLOCKED)
    - Afternoon: 1:30 PM - 5:30 PM
    
    Args:
        current_time: datetime object (defaults to now)
    
    Returns:
        Dict with validation result and details
    """
    if current_time is None:
        current_time = datetime.now()
    
    current_time_only = current_time.time()
    
    # Define working hours
    morning_start = time(8, 30)   # 8:30 AM
    morning_end = time(12, 30)    # 12:30 PM
    afternoon_start = time(13, 30)  # 1:30 PM
    afternoon_end = time(17, 30)    # 5:30 PM
    
    # Check if within morning hours
    if morning_start <= current_time_only < morning_end:
        return {
            'allowed': True,
            'period': 'morning',
            'message': 'Within morning working hours (8:30 AM - 12:30 PM)',
            'current_time': current_time_only.strftime('%I:%M %p'),
            'next_period': 'afternoon (1:30 PM - 5:30 PM)'
        }
    
    # Check if within afternoon hours
    elif afternoon_start <= current_time_only <= afternoon_end:
        return {
            'allowed': True,
            'period': 'afternoon',
            'message': 'Within afternoon working hours (1:30 PM - 5:30 PM)',
            'current_time': current_time_only.strftime('%I:%M %p'),
            'next_period': 'morning (8:30 AM - 12:30 PM tomorrow)'
        }
    
    # Check specific blocked periods
    elif morning_end <= current_time_only < afternoon_start:
        # Lunch break
        return {
            'allowed': False,
            'period': 'lunch_break',
            'message': 'System is blocked during lunch break (12:30 PM - 1:30 PM)',
            'current_time': current_time_only.strftime('%I:%M %p'),
            'next_period': 'afternoon (1:30 PM - 5:30 PM)',
            'minutes_until_next': _minutes_until_time(current_time, afternoon_start)
        }
    
    elif current_time_only > afternoon_end:
        # After work hours
        return {
            'allowed': False,
            'period': 'after_hours',
            'message': 'System is blocked after working hours (after 5:30 PM)',
            'current_time': current_time_only.strftime('%I:%M %p'),
            'next_period': 'morning (8:30 AM tomorrow)',
            'minutes_until_next': _minutes_until_tomorrow_morning(current_time)
        }
    
    else:
        # Before work hours
        return {
            'allowed': False,
            'period': 'before_hours',
            'message': 'System is blocked before working hours (before 8:30 AM)',
            'current_time': current_time_only.strftime('%I:%M %p'),
            'next_period': 'morning (8:30 AM - 12:30 PM)',
            'minutes_until_next': _minutes_until_time(current_time, morning_start)
        }

def _minutes_until_time(current_dt: datetime, target_time: time) -> int:
    """Calculate minutes until target time today"""
    target_dt = current_dt.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=0,
        microsecond=0
    )
    
    if target_dt <= current_dt:
        # Target time has passed today, calculate for tomorrow
        target_dt = target_dt.replace(day=target_dt.day + 1)
    
    diff = target_dt - current_dt
    return int(diff.total_seconds() / 60)

def _minutes_until_tomorrow_morning(current_dt: datetime) -> int:
    """Calculate minutes until 8:30 AM tomorrow"""
    tomorrow = current_dt.replace(
        day=current_dt.day + 1,
        hour=8,
        minute=30,
        second=0,
        microsecond=0
    )
    
    diff = tomorrow - current_dt
    return int(diff.total_seconds() / 60)

def check_semester_end_eligibility(session_start_date: datetime, session_count: int) -> Dict[str, Any]:
    """
    Check if instructor can end semester session
    
    Rules:
    - Must complete at least 4 months (120 days)
    - Must conduct minimum 8 sessions
    
    Args:
        session_start_date: When the first session started
        session_count: Number of sessions conducted
    
    Returns:
        Dict with eligibility result and details
    """
    current_date = datetime.now()
    
    # Calculate days since start
    days_elapsed = (current_date - session_start_date).days
    months_elapsed = days_elapsed / 30.44  # Average days per month
    
    # Check 4-month requirement (120 days)
    min_days_required = 120  # 4 months
    days_remaining = max(0, min_days_required - days_elapsed)
    
    # Check 8-session requirement
    min_sessions_required = 8
    sessions_remaining = max(0, min_sessions_required - session_count)
    
    # Determine eligibility
    time_requirement_met = days_elapsed >= min_days_required
    session_requirement_met = session_count >= min_sessions_required
    
    can_end_semester = time_requirement_met and session_requirement_met
    
    return {
        'can_end_semester': can_end_semester,
        'time_requirement_met': time_requirement_met,
        'session_requirement_met': session_requirement_met,
        'days_elapsed': days_elapsed,
        'months_elapsed': round(months_elapsed, 1),
        'days_remaining': days_remaining,
        'sessions_conducted': session_count,
        'sessions_remaining': sessions_remaining,
        'message': _get_semester_end_message(
            can_end_semester, days_remaining, sessions_remaining
        )
    }

def _get_semester_end_message(can_end: bool, days_remaining: int, sessions_remaining: int) -> str:
    """Generate appropriate message for semester end eligibility"""
    if can_end:
        return "✅ Eligible to end semester session"
    
    reasons = []
    if days_remaining > 0:
        reasons.append(f"{days_remaining} days remaining (need 4 months)")
    if sessions_remaining > 0:
        reasons.append(f"{sessions_remaining} sessions remaining (need 8 total)")
    
    return f"❌ Cannot end semester: {', '.join(reasons)}"

# Test functions for development
def test_working_hours():
    """Test working hours validation with different times"""
    test_times = [
        datetime(2025, 12, 11, 7, 0),   # 7:00 AM - before hours
        datetime(2025, 12, 11, 9, 0),   # 9:00 AM - morning hours
        datetime(2025, 12, 11, 12, 0),  # 12:00 PM - lunch break
        datetime(2025, 12, 11, 14, 0),  # 2:00 PM - afternoon hours
        datetime(2025, 12, 11, 18, 0),  # 6:00 PM - after hours
    ]
    
    print("🕐 Working Hours Test")
    print("=" * 40)
    
    for test_time in test_times:
        result = is_within_working_hours(test_time)
        status = "✅ ALLOWED" if result['allowed'] else "❌ BLOCKED"
        print(f"{test_time.strftime('%I:%M %p')}: {status}")
        print(f"   {result['message']}")
        if not result['allowed']:
            print(f"   Next: {result['next_period']}")
        print()

def test_semester_eligibility():
    """Test semester end eligibility with different scenarios"""
    test_scenarios = [
        (datetime(2025, 8, 1), 5),   # 4+ months, <8 sessions
        (datetime(2025, 11, 1), 10), # <4 months, 8+ sessions  
        (datetime(2025, 7, 1), 12),  # 4+ months, 8+ sessions
        (datetime(2025, 10, 1), 3),  # <4 months, <8 sessions
    ]
    
    print("📅 Semester End Eligibility Test")
    print("=" * 40)
    
    for start_date, session_count in test_scenarios:
        result = check_semester_end_eligibility(start_date, session_count)
        status = "✅ CAN END" if result['can_end_semester'] else "❌ CANNOT END"
        print(f"Start: {start_date.strftime('%Y-%m-%d')}, Sessions: {session_count}")
        print(f"   {status}: {result['message']}")
        print(f"   Months elapsed: {result['months_elapsed']}")
        print()

if __name__ == "__main__":
    test_working_hours()
    test_semester_eligibility()