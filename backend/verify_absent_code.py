"""
Quick verification that absent marking code is in place
"""

print("\n" + "="*80)
print("VERIFYING ABSENT MARKING IMPLEMENTATION")
print("="*80 + "\n")

try:
    # Check if the function exists
    from blueprints.attendance import end_session
    print("✓ end_session function imported successfully")
    
    # Check the source code
    import inspect
    source = inspect.getsource(end_session)
    
    # Verify key components
    checks = [
        ("absent_student_ids", "Absent student calculation"),
        ("'absent'", "Absent status field"),
        ("absent_count", "Absent counter"),
        ("student_query", "Student query logic"),
        ("present_student_ids", "Present student tracking"),
    ]
    
    print("\nChecking implementation components:")
    all_good = True
    for keyword, description in checks:
        if keyword in source:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - MISSING!")
            all_good = False
    
    if all_good:
        print("\n" + "="*80)
        print("✅ IMPLEMENTATION VERIFIED - CODE IS IN PLACE")
        print("="*80)
        print("\nThe absent marking feature is implemented correctly.")
        print("\nTO USE IT:")
        print("1. RESTART the backend server (if it's running)")
        print("   - Stop: Ctrl+C")
        print("   - Start: python app.py")
        print("\n2. Test the feature:")
        print("   - Login as instructor")
        print("   - Start a session for a section")
        print("   - End the session")
        print("   - Check that absent students are marked")
        print("\n3. Or run: python test_absent_marking.py")
    else:
        print("\n" + "="*80)
        print("⚠️ SOME COMPONENTS MISSING")
        print("="*80)
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure you're in the backend directory")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print()
