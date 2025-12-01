"""
Migrate existing instructors to support multiple courses
Converts single course_name field to courses array
"""
from db.mongo import init_db

def migrate_instructors():
    """Migrate instructors from single course to multiple courses"""
    db = init_db()
    
    print("🔄 Starting instructor migration to multi-course format...")
    
    # Find all instructors
    instructors = db.users.find({'role': 'instructor'})
    
    updated_count = 0
    skipped_count = 0
    
    for instructor in instructors:
        # Check if already has courses array
        if 'courses' in instructor and isinstance(instructor['courses'], list):
            print(f"⏭️  Skipping {instructor['name']} - already has courses array")
            skipped_count += 1
            continue
        
        # Get existing course_name
        course_name = instructor.get('course_name', '')
        
        # Create courses array
        courses = [course_name] if course_name else []
        
        # Update instructor
        db.users.update_one(
            {'_id': instructor['_id']},
            {
                '$set': {
                    'courses': courses
                }
            }
        )
        
        print(f"✅ Updated {instructor['name']}: course_name='{course_name}' -> courses={courses}")
        updated_count += 1
    
    print(f"\n📊 Migration complete!")
    print(f"   Updated: {updated_count} instructors")
    print(f"   Skipped: {skipped_count} instructors (already migrated)")
    print(f"   Total: {updated_count + skipped_count} instructors")

if __name__ == '__main__':
    migrate_instructors()
