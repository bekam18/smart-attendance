# Download Reports - Quick Start Guide

## Installation

1. **Install Excel dependency**
   ```bash
   install_reports_dependency.bat
   ```
   Or manually:
   ```bash
   cd backend
   pip install openpyxl
   ```

2. **Restart backend** (if running)
   ```bash
   RESTART_BACKEND_NOW.bat
   ```

## Usage

### Step 1: Access Reports Page
1. Login as instructor
2. Click the green **"Download Reports"** button on the dashboard
3. You'll be taken to the reports page

### Step 2: Configure Report
1. **Select Report Type**:
   - Daily: Single day attendance
   - Weekly: 7-day range
   - Monthly: Current month
   - Semester: Last 4 months
   - Yearly: Academic year (Sep-Aug)

2. **Select Section** (Required):
   - Choose from your assigned sections (A, B, C, D)

3. **Select Course** (Required):
   - Choose from your assigned courses (web, AI, java)

4. **Set Date Range** (Optional):
   - Daily: Pick specific date (defaults to today)
   - Weekly: Pick week start/end (defaults to current week)
   - Others: Auto-calculated

### Step 3: Generate Report
1. Click **"Generate Report"** button
2. Wait for processing (usually 1-2 seconds)
3. View results in the table below

### Step 4: Download Report
1. Click **"Download CSV"** for spreadsheet format
2. Click **"Download Excel"** for formatted XLSX
3. File downloads automatically with timestamp

## Understanding the Report

### Summary Cards
- **Total Students**: Number of students in section
- **Total Sessions**: Number of sessions in date range
- **Section**: Selected section
- **Below Threshold**: Students not meeting requirements

### Student Table Columns
- **Student ID**: Unique student identifier
- **Name**: Student full name
- **Section**: Student section
- **Total Sessions**: Combined lab + theory sessions
- **Present**: Number of times present
- **Absent**: Number of times absent
- **Overall %**: Overall attendance percentage
- **Lab %**: Lab attendance (100% required)
- **Theory %**: Theory attendance (80% required)
- **Status**: OK or Below threshold warning

### Color Indicators
- **Red Background**: Student below threshold
- **Green Badge**: ≥80% attendance (Good)
- **Yellow Badge**: 60-79% attendance (Warning)
- **Red Badge**: <60% attendance (Critical)

## Attendance Thresholds

### Lab Sessions
- **Required**: 100% attendance
- **Reason**: Practical work cannot be made up
- **Example**: 2/2 sessions = 100% ✅, 1/2 sessions = 50% ❌

### Theory Sessions
- **Required**: 80% attendance
- **Reason**: Some absences acceptable for theory
- **Example**: 4/5 sessions = 80% ✅, 3/5 sessions = 60% ❌

### Below Threshold
A student is flagged if:
- Lab percentage < 100% OR
- Theory percentage < 80%

## Report Types Explained

### Daily Report
- Shows attendance for one specific day
- Useful for checking today's attendance
- Example: "Who was present on December 4th?"

### Weekly Report
- Shows attendance for 7-day period
- Useful for weekly summaries
- Example: "This week's attendance (Mon-Sun)"

### Monthly Report
- Shows attendance for current month
- Useful for monthly reviews
- Example: "December 2025 attendance"

### Semester Report
- Shows attendance for last 4 months
- Useful for mid-semester reviews
- Example: "Sep-Dec 2025 attendance"

### Yearly Report
- Shows attendance for academic year (Sep-Aug)
- Useful for final evaluations
- Example: "2025-2026 academic year"

## Example Workflow

### Scenario: Weekly Report for Section A, Web Course

1. **Configure**:
   - Report Type: Weekly
   - Section: A
   - Course: web
   - Week Start: 2025-12-02 (Monday)
   - Week End: 2025-12-08 (Sunday)

2. **Generate**:
   - Click "Generate Report"
   - See 30 students, 5 sessions
   - 3 students below threshold

3. **Review**:
   - Check red-highlighted students
   - Note lab vs theory percentages
   - Identify students needing attention

4. **Download**:
   - Download Excel for formatted report
   - Share with department head
   - Keep for records

## Tips

### Best Practices
- Generate reports weekly for monitoring
- Download monthly reports for records
- Check "Below Threshold" students regularly
- Use Excel format for presentations

### Common Use Cases
- **Daily**: Quick check after class
- **Weekly**: Regular monitoring
- **Monthly**: Department reports
- **Semester**: Mid-term evaluations
- **Yearly**: Final grade calculations

### Troubleshooting
- **No data**: Check section/course selection
- **Wrong dates**: Verify date range includes sessions
- **Download fails**: Install openpyxl dependency
- **Missing students**: Check student section assignments

## File Formats

### CSV Format
- Plain text, comma-separated
- Opens in Excel, Google Sheets, Numbers
- Good for data processing
- File size: Small (~10KB for 30 students)

### Excel Format (XLSX)
- Formatted with colors and borders
- Professional appearance
- Good for presentations
- File size: Medium (~20KB for 30 students)

## Quick Reference

| Action | Button | Color |
|--------|--------|-------|
| Access Reports | Download Reports | Green |
| Generate Report | Generate Report | Blue |
| Download CSV | Download CSV | Green |
| Download Excel | Download Excel | Blue |
| Back to Dashboard | Back | Gray |

## Need Help?

- Check `INSTRUCTOR_REPORTS_COMPLETE.md` for detailed documentation
- Run `test_reports.bat` to test API endpoints
- Contact admin if you don't see your sections/courses
- Verify attendance data exists for selected date range

## Summary

The Download Reports feature provides:
- ✅ 5 report types (daily to yearly)
- ✅ Section and course filtering
- ✅ Comprehensive statistics
- ✅ Threshold warnings
- ✅ CSV and Excel exports
- ✅ Professional formatting
- ✅ Easy-to-use interface

Generate your first report in 3 clicks:
1. Select section
2. Select course
3. Click "Generate Report"

Then download in your preferred format!
