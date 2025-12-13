#!/usr/bin/env python3
"""Update existing attendance data to have more realistic patterns"""

import sys
import random
sys.path.append('backend')

from db.mysql import get_db

def update_attendance_patterns():
    """Update existing attendance data with realistic patterns"""
    
    print("🎯 Updating Attendance Patterns for Realistic Data")
    print("=" * 50)
    
    try:
        db = get_db()
        print("✅ Database connection successful")
        
        # Check current attendance data
        current_data = db.execute_query("SELECT COUNT(*) as count FROM attendance")
        total_records = current_data[0]['count']
        print(f"📊 Found {total_records} existing attendance records")
        
        if total_records == 0:
            print("❌ No attendance data found. Please create some attendance data first.")
            return False
        
        # Get all attendance records
        all_records = db.execute_query("""
            SELECT id, time_block, section_id, course_name, status 
            FROM attendance 
            ORDER BY id
        """)
        
        print(f"📋 Processing {len(all_records)} records...")
        
        updates_made = 0
        
        for record in all_records:
            record_id = record['id']
            time_block = record['time_block']
            section_id = record['section_id']
            course_name = record['course_name']
            current_status = record['status']
            
            # Determine realistic attendance probability
            if time_block == "morning":
                if section_id == "A":
                    attendance_prob = 0.78  # Morning Section A: 78%
                else:
                    attendance_prob = 0.72  # Morning Section B: 72%
            else:  # afternoon
                if section_id == "A":
                    attendance_prob = 0.87  # Afternoon Section A: 87%
                else:
                    attendance_prob = 0.83  # Afternoon Section B: 83%
            
            # Add course-specific variations
            if course_name == "Computer Science":
                attendance_prob += 0.05
            elif course_name == "Mathematics":
                attendance_prob += 0.02
            elif course_name == "Physics":
                attendance_prob -= 0.03
            elif course_name == "Chemistry":
                attendance_prob += 0.01
            
            # Ensure probability is within bounds
            attendance_prob = max(0.55, min(0.95, attendance_prob))
            
            # Determine new status based on probability
            new_status = "present" if random.random() < attendance_prob else "absent"
            new_confidence = random.uniform(0.75, 0.95) if new_status == "present" else 0.0
            
            # Update record if status changed
            if new_status != current_status:
                update_query = """
                    UPDATE attendance 
                    SET status = %s, confidence = %s 
                    WHERE id = %s
                """
                
                db.execute_query(update_query, (new_status, new_confidence, record_id), fetch=False)
                updates_made += 1
        
        print(f"✅ Updated {updates_made} records with realistic patterns")
        
        # Generate summary statistics
        print("\n📈 Updated Attendance Summary:")
        
        # Overall statistics
        total_records = db.execute_query("SELECT COUNT(*) as count FROM attendance")[0]['count']
        present_records = db.execute_query("SELECT COUNT(*) as count FROM attendance WHERE status = 'present'")[0]['count']
        overall_rate = (present_records / total_records) * 100 if total_records > 0 else 0
        
        print(f"   📊 Total Records: {total_records}")
        print(f"   ✅ Present: {present_records}")
        print(f"   ❌ Absent: {total_records - present_records}")
        print(f"   📈 Overall Attendance: {overall_rate:.1f}%")
        
        # Time block statistics
        print(f"\n⏰ Time Block Breakdown:")
        time_stats = db.execute_query("""
            SELECT 
                time_block,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
                ROUND((SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 1) as rate
            FROM attendance 
            WHERE time_block IS NOT NULL
            GROUP BY time_block
            ORDER BY time_block
        """)
        
        for stat in time_stats:
            print(f"   {stat['time_block'].title()}: {stat['rate']}% ({stat['present']}/{stat['total']})")
        
        # Section statistics  
        print(f"\n📚 Section Breakdown:")
        section_stats = db.execute_query("""
            SELECT 
                section_id,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
                ROUND((SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 1) as rate
            FROM attendance 
            WHERE section_id IS NOT NULL
            GROUP BY section_id
            ORDER BY section_id
        """)
        
        for stat in section_stats:
            print(f"   Section {stat['section_id']}: {stat['rate']}% ({stat['present']}/{stat['total']})")
        
        # Combined time block and section statistics
        print(f"\n🎯 Time Block + Section Breakdown:")
        combined_stats = db.execute_query("""
            SELECT 
                time_block,
                section_id,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
                ROUND((SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 1) as rate
            FROM attendance 
            WHERE time_block IS NOT NULL AND section_id IS NOT NULL
            GROUP BY time_block, section_id
            ORDER BY time_block, section_id
        """)
        
        for stat in combined_stats:
            print(f"   {stat['time_block'].title()} Section {stat['section_id']}: {stat['rate']}% ({stat['present']}/{stat['total']})")
        
        # Course statistics
        print(f"\n🎓 Course Breakdown:")
        course_stats = db.execute_query("""
            SELECT 
                course_name,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
                ROUND((SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 1) as rate
            FROM attendance 
            WHERE course_name IS NOT NULL
            GROUP BY course_name
            ORDER BY rate DESC
        """)
        
        for stat in course_stats:
            print(f"   {stat['course_name']}: {stat['rate']}% ({stat['present']}/{stat['total']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating attendance patterns: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = update_attendance_patterns()
    
    if success:
        print(f"\n🎉 Attendance patterns updated successfully!")
        print(f"💡 New realistic patterns:")
        print(f"   🌅 Morning Section A: ~78% attendance")
        print(f"   🌅 Morning Section B: ~72% attendance") 
        print(f"   🌇 Afternoon Section A: ~87% attendance")
        print(f"   🌇 Afternoon Section B: ~83% attendance")
        print(f"   📚 Course variations applied")
        print(f"\n🔄 Next steps:")
        print(f"   1. Run: python generate_real_analytics_data.py")
        print(f"   2. Check the admin dashboard for updated analytics")
    else:
        print(f"\n❌ Failed to update attendance patterns")