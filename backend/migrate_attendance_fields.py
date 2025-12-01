"""
Migration script to update existing attendance records with session data
Run this once to fill in missing year, course, and session_type fields
"""

from db.mongo import get_db, init_db
from bson import ObjectId

def migrate_attendance_records():
    """Update existing attendance records with data from their sessions"""
    print("Starting attendance records migration...")
    print("="*60)
    
    init_db()
    db = get_db()
    
    # Get all attendance records
    records = list(db.attendance.find({}))
    total_records = len(records)
    
    print(f"Found {total_records} attendance records to check")
    print()
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, record in enumerate(records, 1):
        try:
            # Get the session for this attendance record
            session_id = record.get('session_id')
            
            if not session_id:
                print(f"[{i}/{total_records}] ⚠️  Record {record['_id']} has no session_id - skipping")
                skipped_count += 1
                continue
            
            session = db.sessions.find_one({'_id': ObjectId(session_id)})
            
            if not session:
                print(f"[{i}/{total_records}] ⚠️  Session {session_id} not found - skipping")
                skipped_count += 1
                continue
            
            # Build update fields
            update_fields = {}
            
            # Check and update section_id
            if not record.get('section_id'):
                update_fields['section_id'] = session.get('section_id', '')
            
            # Check and update year
            if not record.get('year'):
                update_fields['year'] = session.get('year', '')
            
            # Check and update course_name
            if not record.get('course_name'):
                update_fields['course_name'] = session.get('course_name', '')
            
            # Check and update session_type
            if not record.get('session_type'):
                update_fields['session_type'] = session.get('session_type', '')
            
            # Check and update time_block
            if not record.get('time_block'):
                update_fields['time_block'] = session.get('time_block', '')
            
            # Check and update class_year
            if not record.get('class_year'):
                update_fields['class_year'] = session.get('class_year', '')
            
            # Update if there are fields to update
            if update_fields:
                db.attendance.update_one(
                    {'_id': record['_id']},
                    {'$set': update_fields}
                )
                updated_count += 1
                
                # Show what was updated
                fields_updated = ', '.join(update_fields.keys())
                print(f"[{i}/{total_records}] ✅ Updated record {record['_id']}: {fields_updated}")
            else:
                print(f"[{i}/{total_records}] ℹ️  Record {record['_id']} already has all fields")
        
        except Exception as e:
            error_count += 1
            print(f"[{i}/{total_records}] ❌ Error updating record {record.get('_id')}: {e}")
    
    print()
    print("="*60)
    print("Migration Summary:")
    print(f"  Total records: {total_records}")
    print(f"  ✅ Updated: {updated_count}")
    print(f"  ℹ️  Skipped: {skipped_count}")
    print(f"  ❌ Errors: {error_count}")
    print("="*60)
    print()
    
    if updated_count > 0:
        print(f"✅ Migration complete! Updated {updated_count} attendance records")
    else:
        print("ℹ️  No records needed updating")

if __name__ == '__main__':
    try:
        migrate_attendance_records()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
