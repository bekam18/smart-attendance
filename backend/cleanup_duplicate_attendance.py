"""
Cleanup script to remove duplicate attendance records
Keeps only the LATEST entry for each (student_id, session_id, date) combination
"""

from db.mongo import get_db
from bson import ObjectId
from datetime import datetime

def cleanup_duplicates():
    """Remove duplicate attendance records, keeping only the latest one"""
    
    db = get_db()
    
    print("="*80)
    print("CLEANING UP DUPLICATE ATTENDANCE RECORDS")
    print("="*80)
    
    # Find all attendance records
    all_records = list(db.attendance.find())
    
    print(f"\n📊 Total attendance records: {len(all_records)}")
    
    # Group by (student_id, session_id, date)
    groups = {}
    for record in all_records:
        key = (
            record.get('student_id'),
            record.get('session_id'),
            record.get('date')
        )
        
        if key not in groups:
            groups[key] = []
        groups[key].append(record)
    
    print(f"📊 Unique combinations: {len(groups)}")
    
    # Find duplicates
    duplicates_found = 0
    records_to_delete = []
    
    for key, records in groups.items():
        if len(records) > 1:
            duplicates_found += 1
            student_id, session_id, date = key
            
            print(f"\n⚠️  DUPLICATE FOUND:")
            print(f"   Student: {student_id}")
            print(f"   Session: {session_id}")
            print(f"   Date: {date}")
            print(f"   Count: {len(records)} entries")
            
            # Sort by timestamp (newest first)
            sorted_records = sorted(
                records,
                key=lambda x: x.get('timestamp', datetime.min),
                reverse=True
            )
            
            # Keep the first (newest), delete the rest
            keep = sorted_records[0]
            delete = sorted_records[1:]
            
            print(f"   ✅ KEEPING: {keep['_id']} (timestamp: {keep.get('timestamp')})")
            
            for rec in delete:
                print(f"   ❌ DELETING: {rec['_id']} (timestamp: {rec.get('timestamp')})")
                records_to_delete.append(rec['_id'])
    
    print(f"\n📊 Summary:")
    print(f"   Duplicate groups found: {duplicates_found}")
    print(f"   Records to delete: {len(records_to_delete)}")
    
    if records_to_delete:
        print(f"\n⚠️  About to delete {len(records_to_delete)} duplicate records...")
        response = input("   Continue? (yes/no): ")
        
        if response.lower() == 'yes':
            result = db.attendance.delete_many({
                '_id': {'$in': records_to_delete}
            })
            
            print(f"\n✅ Deleted {result.deleted_count} duplicate records")
            
            # Verify
            remaining = db.attendance.count_documents({})
            print(f"✅ Remaining attendance records: {remaining}")
            
            # Update session counts
            print(f"\n🔄 Updating session attendance counts...")
            sessions = db.sessions.find()
            
            for session in sessions:
                session_id = str(session['_id'])
                count = db.attendance.count_documents({'session_id': session_id})
                
                db.sessions.update_one(
                    {'_id': session['_id']},
                    {'$set': {'attendance_count': count}}
                )
                
                print(f"   Session {session_id}: {count} attendees")
            
            print(f"\n✅ CLEANUP COMPLETE!")
        else:
            print(f"\n❌ Cleanup cancelled")
    else:
        print(f"\n✅ No duplicates found - database is clean!")
    
    print("="*80)


if __name__ == '__main__':
    cleanup_duplicates()
