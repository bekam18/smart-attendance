import sys
sys.path.insert(0, 'backend')

from db.mysql import get_db

db = get_db()

# Update Bekam Ayele's section
# Change these values to the correct section and year
NEW_SECTION = 'B'  # Change to correct section (A, B, C, or D)
NEW_YEAR = '4th Year'  # Change to correct year if needed

print("Current data for Bekam Ayele:")
student = db.execute_query("SELECT * FROM students WHERE student_id = 'STU013'")[0]
print(f"Name: {student['name']}")
print(f"Current Year: {student['year']}")
print(f"Current Section: {student['section']}")

# Uncomment the lines below to update
# db.execute_query(
#     "UPDATE students SET section = %s, year = %s WHERE student_id = 'STU013'",
#     (NEW_SECTION, NEW_YEAR),
#     fetch=False
# )
# print(f"\n✅ Updated Bekam Ayele to Section {NEW_SECTION}, {NEW_YEAR}")

print("\n⚠️  To apply the update, uncomment the update lines in this script")
print(f"   and set NEW_SECTION and NEW_YEAR to the correct values")
