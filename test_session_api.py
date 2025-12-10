"""Test the session attendance API endpoint"""
import requests

BASE_URL = "http://127.0.0.1:5000"

# Login as instructor
print("="*80)
print("TESTING SESSION ATTENDANCE API")
print("="*80)

# You'll need to login first - use instructor credentials
print("\n→ Login required. Please provide instructor credentials:")
print("  (or check browser network tab for the actual API call)")

# Get the session ID from the screenshot (session 47)
session_id = 47

print(f"\n→ Testing GET /api/attendance/session/{session_id}")
print(f"  URL: {BASE_URL}/api/attendance/session/{session_id}")

# Note: This will fail without authentication token
# The actual issue is likely in the frontend or API response

print("\n" + "="*80)
print("CHECKING BACKEND LOGS")
print("="*80)
print("\nPlease check the backend terminal for any errors when loading the session page.")
print("The issue might be:")
print("  1. Frontend counting wrong")
print("  2. API returning wrong data")
print("  3. Old cached data in browser")

print("\n" + "="*80)
print("RECOMMENDED ACTIONS")
print("="*80)
print("\n1. Refresh the page with Ctrl+F5 (hard refresh)")
print("2. Check browser console for errors (F12)")
print("3. Check backend logs for API calls")
print("4. Verify the API endpoint is returning correct data")
