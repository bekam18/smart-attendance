/**
 * Time-based restrictions for the attendance system
 */
import { useState, useEffect } from 'react';

export interface WorkingHoursCheck {
  allowed: boolean;
  period: 'morning' | 'afternoon' | 'lunch_break' | 'before_hours' | 'after_hours';
  message: string;
  current_time: string;
  next_period: string;
  minutes_until_next?: number;
}

export interface SemesterEligibility {
  can_end_semester: boolean;
  time_requirement_met: boolean;
  session_requirement_met: boolean;
  days_elapsed: number;
  months_elapsed: number;
  days_remaining: number;
  sessions_conducted: number;
  sessions_remaining: number;
  message: string;
}

/**
 * Check if current time is within working hours (client-side)
 */
export function isWithinWorkingHours(currentTime?: Date): WorkingHoursCheck {
  const now = currentTime || new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();
  const currentMinutes = hours * 60 + minutes;
  
  // Working hours in minutes from midnight
  const morningStart = 8 * 60 + 30;   // 8:30 AM
  const morningEnd = 12 * 60 + 30;     // 12:30 PM
  const afternoonStart = 13 * 60 + 30; // 1:30 PM
  const afternoonEnd = 17 * 60 + 30;   // 5:30 PM
  
  const currentTimeStr = now.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true 
  });
  
  // Check if within morning hours
  if (currentMinutes >= morningStart && currentMinutes < morningEnd) {
    return {
      allowed: true,
      period: 'morning',
      message: 'Within morning working hours (8:30 AM - 12:30 PM)',
      current_time: currentTimeStr,
      next_period: 'afternoon (1:30 PM - 5:30 PM)'
    };
  }
  
  // Check if within afternoon hours
  if (currentMinutes >= afternoonStart && currentMinutes <= afternoonEnd) {
    return {
      allowed: true,
      period: 'afternoon',
      message: 'Within afternoon working hours (1:30 PM - 5:30 PM)',
      current_time: currentTimeStr,
      next_period: 'morning (8:30 AM - 12:30 PM tomorrow)'
    };
  }
  
  // Check specific blocked periods
  if (currentMinutes >= morningEnd && currentMinutes < afternoonStart) {
    // Lunch break
    const minutesUntilAfternoon = afternoonStart - currentMinutes;
    return {
      allowed: false,
      period: 'lunch_break',
      message: 'System is blocked during lunch break (12:30 PM - 1:30 PM)',
      current_time: currentTimeStr,
      next_period: 'afternoon (1:30 PM - 5:30 PM)',
      minutes_until_next: minutesUntilAfternoon
    };
  }
  
  if (currentMinutes > afternoonEnd) {
    // After work hours
    const minutesUntilTomorrow = (24 * 60) + morningStart - currentMinutes;
    return {
      allowed: false,
      period: 'after_hours',
      message: 'System is blocked after working hours (after 5:30 PM)',
      current_time: currentTimeStr,
      next_period: 'morning (8:30 AM tomorrow)',
      minutes_until_next: minutesUntilTomorrow
    };
  }
  
  // Before work hours
  const minutesUntilMorning = morningStart - currentMinutes;
  return {
    allowed: false,
    period: 'before_hours',
    message: 'System is blocked before working hours (before 8:30 AM)',
    current_time: currentTimeStr,
    next_period: 'morning (8:30 AM - 12:30 PM)',
    minutes_until_next: minutesUntilMorning
  };
}

/**
 * Format minutes into human-readable time
 */
export function formatTimeUntil(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  if (remainingMinutes === 0) {
    return `${hours} hour${hours !== 1 ? 's' : ''}`;
  }
  
  return `${hours}h ${remainingMinutes}m`;
}

/**
 * Get working hours status with live updates
 */
export function useWorkingHoursStatus() {
  const [status, setStatus] = useState<WorkingHoursCheck>(isWithinWorkingHours());
  
  useEffect(() => {
    const updateStatus = () => {
      setStatus(isWithinWorkingHours());
    };
    
    // Update every minute
    const interval = setInterval(updateStatus, 60000);
    
    return () => clearInterval(interval);
  }, []);
  
  return status;
}

/**
 * Get working hours status color classes
 */
export function getWorkingHoursStatusColor(allowed: boolean): string {
  if (allowed) return 'text-green-600 bg-green-50';
  return 'text-red-600 bg-red-50';
}

/**
 * Get working hours status icon
 */
export function getWorkingHoursStatusIcon(allowed: boolean): string {
  if (allowed) return '🟢';
  return '🔴';
}