"""
Fix year format in existing sessions
Changes '1', '2', '3', '4' to '1st Year', '2nd Year', '3rd Year', '4th Year'
"""

from db.mysql import get_db

def fix_session_year_format():
    print("\n" + "="*70)
    print("FIXING SESSION YEAR FORMAT")
    print("="*70)
    
    db = get_db()
    
    # Get all sessions with wrong year format
    sessions = db.execute_query(
        "SELECT id, name, section_id, year FROM sessions WHERE year IN ('1', '2', '3', '4', '1r', '2r', '3r', '4r', '4th')"
    )
    
    if not sessions:
        print("\n✅ No sessions need fixing!")
        return
    
    print(f"\nFound {len(sessions)} sessions to fix:")
    
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
    
    for session in sessions:
        old_year = session['year']
        new_year = year_map.get(old_year, old_year)
        
        print(f"\nSession ID {session['id']}: {session['name']}")
        print(f"  Section: {session['section_id']}")
        print(f"  Year: '{old_year}' → '{new_year}'")
        
        # Update the session
        db.execute_query(
            "UPDATE sessions SET year = %s WHERE id = %s",
            (new_year, session['id']),
            fetch=False
        )
        
        print(f"  ✅ Updated!")
    
    print("\n" + "="*70)
    print(f"✅ Fixed {len(sessions)} sessions!")
    print("="*70)
    print("\nNow try clicking 'Stop Camera' again.")

if __name__ == '__main__':
    try:
        fix_session_year_format()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
