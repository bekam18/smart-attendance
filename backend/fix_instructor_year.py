"""
Fix instructor's class_year to match student year format
"""

from db.mysql import get_db

def fix_instructor_year():
    print("\n" + "="*70)
    print("FIXING INSTRUCTOR YEAR FORMAT")
    print("="*70)
    
    db = get_db()
    
    # Get all instructors
    instructors = db.execute_query('SELECT id, name, class_year FROM users WHERE role = "instructor"')
    
    if not instructors:
        print("\n❌ No instructors found!")
        return
    
    print(f"\nFound {len(instructors)} instructors:")
    
    year_map = {
        '1': '1st Year',
        '1r': '1st Year',
        '2': '2nd Year',
        '2r': '2nd Year',
        '3': '3rd Year',
        '3r': '3rd Year',
        '4': '4th Year',
        '4r': '4th Year',
        '4th': '4th Year'
    }
    
    for instructor in instructors:
        old_year = instructor['class_year']
        
        # Check if needs fixing
        if old_year in year_map:
            new_year = year_map[old_year]
            
            print(f"\nInstructor: {instructor['name']}")
            print(f"  Old Year: '{old_year}'")
            print(f"  New Year: '{new_year}'")
            
            # Update the instructor
            db.execute_query(
                "UPDATE users SET class_year = %s WHERE id = %s",
                (new_year, instructor['id']),
                fetch=False
            )
            
            print(f"  ✅ Updated!")
        else:
            print(f"\nInstructor: {instructor['name']}")
            print(f"  Year: '{old_year}' - OK")
    
    print("\n" + "="*70)
    print("✅ DONE!")
    print("="*70)

if __name__ == '__main__':
    try:
        fix_instructor_year()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
