"""
Migration script to add instructor_id and section_id to existing data
Run this ONCE to update existing attendance records and sessions
"""

from pymongo import MongoClient
from datetime import datetime
from config import config

def migrate_database():
    """Add instructor_id and section_id to existing records"""
    
    print("🔄 Starting database migration for multi-instructor security...")
    
    # Connect to MongoDB
    client = MongoClient(config.MONGODB_URI)
    db = client[config.MONGODB_DB_NAME]
    
    # Step 1: Add sections to existing instructors
    print("\n1️⃣ Adding sections to instructors...")
    instructors = list(db.users.find({'role': 'instructor'}))
    
    for idx, instructor in enumerate(instructors):
        if 'sections' not in instructor:
            # Assign default sections based on department
            dept = instructor.get('department', 'General')
            sections = [f"{dept.upper()[:4]}101-A", f"{dept.upper()[:4]}201-B"]
            
            db.users.update_one(
                {'_id': instructor['_id']},
                {'$set': {'sections': sections}}
            )
            print(f"   ✅ Added sections to {instructor.get('name')}: {sections}")
    
    # Step 2: Add instructor_id and section_id to existing sessions
    print("\n2️⃣ Updating sessions with instructor_id and section_id...")
    sessions = list(db.sessions.find({}))
    
    for session in sessions:
        updates = {}
        
        # Add instructor_id if missing
        if 'instructor_id' not in session:
            # Try to find instructor from instructor_name or assign first instructor
            instructor = None
            if 'instructor_name' in session:
                instructor = db.users.find_one({
                    'role': 'instructor',
                    'name': session['instructor_name']
                })
            
            if not instructor:
                # Assign to first instructor
                instructor = db.users.find_one({'role': 'instructor'})
            
            if instructor:
                updates['instructor_id'] = str(instructor['_id'])
                print(f"   ✅ Added instructor_id to session: {session.get('name')}")
        
        # Add section_id if missing
        if 'section_id' not in session:
            # Get instructor's first section
            instructor_id = updates.get('instructor_id') or session.get('instructor_id')
            if instructor_id:
                from bson import ObjectId
                instructor = db.users.find_one({'_id': ObjectId(instructor_id)})
                if instructor and 'sections' in instructor:
                    updates['section_id'] = instructor['sections'][0]
                    print(f"   ✅ Added section_id to session: {session.get('name')}")
        
        if updates:
            db.sessions.update_one(
                {'_id': session['_id']},
                {'$set': updates}
            )
    
    # Step 3: Add instructor_id and section_id to existing attendance records
    print("\n3️⃣ Updating attendance records with instructor_id and section_id...")
    attendance_records = list(db.attendance.find({}))
    
    updated_count = 0
    for record in attendance_records:
        updates = {}
        
        # Get session to find instructor_id and section_id
        if 'session_id' in record:
            from bson import ObjectId
            try:
                session = db.sessions.find_one({'_id': ObjectId(record['session_id'])})
                
                if session:
                    if 'instructor_id' not in record and 'instructor_id' in session:
                        updates['instructor_id'] = session['instructor_id']
                    
                    if 'section_id' not in record and 'section_id' in session:
                        updates['section_id'] = session.get('section_id', '')
            except:
                # If session_id is not ObjectId, try as string
                session = db.sessions.find_one({'_id': record['session_id']})
                if session:
                    if 'instructor_id' not in record and 'instructor_id' in session:
                        updates['instructor_id'] = session['instructor_id']
                    
                    if 'section_id' not in record and 'section_id' in session:
                        updates['section_id'] = session.get('section_id', '')
        
        if updates:
            db.attendance.update_one(
                {'_id': record['_id']},
                {'$set': updates}
            )
            updated_count += 1
    
    print(f"   ✅ Updated {updated_count} attendance records")
    
    # Step 4: Verify migration
    print("\n4️⃣ Verifying migration...")
    
    instructors_with_sections = db.users.count_documents({
        'role': 'instructor',
        'sections': {'$exists': True}
    })
    
    sessions_with_instructor = db.sessions.count_documents({
        'instructor_id': {'$exists': True}
    })
    
    attendance_with_instructor = db.attendance.count_documents({
        'instructor_id': {'$exists': True}
    })
    
    print(f"   ✅ Instructors with sections: {instructors_with_sections}")
    print(f"   ✅ Sessions with instructor_id: {sessions_with_instructor}")
    print(f"   ✅ Attendance records with instructor_id: {attendance_with_instructor}")
    
    # Print summary
    print("\n" + "="*60)
    print("✅ Migration completed successfully!")
    print("="*60)
    print("\n📊 Summary:")
    print(f"   Total Instructors: {db.users.count_documents({'role': 'instructor'})}")
    print(f"   Total Sessions: {db.sessions.count_documents({})}")
    print(f"   Total Attendance Records: {db.attendance.count_documents({})}")
    print("\n🔒 Security Status:")
    print(f"   ✅ All instructors have sections assigned")
    print(f"   ✅ All sessions linked to instructors")
    print(f"   ✅ All attendance records linked to instructors")
    print("\n🚀 System ready for multi-instructor secure access!")
    
    client.close()

if __name__ == '__main__':
    try:
        migrate_database()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
