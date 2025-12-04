# Instructor Reports Feature - Complete Implementation

## Overview
A comprehensive attendance reporting system that allows instructors to generate, view, and download detailed attendance reports with multiple filtering options and export formats.

## Features Implemented

### 1. Report Types
- **Daily Report**: Attendance for a specific date
- **Weekly Report**: Attendance for a week range (Monday-Sunday)
- **Monthly Report**: Attendance for the current month
- **Semester Report**: Attendance for the last 4 months
- **Yearly Report**: Attendance for the academic year (September-August)

### 2. Filtering Options
- **Section**: Filter by Section A, B, C, or D
- **Course**: Filter by specific course (web, AI, java, etc.)
- **Date Range**: Custom date ranges for daily and weekly reports
- **Auto-calculation**: Automatic date range calculation for monthly, semester, and yearly reports

### 3. Report Statistics
Each report includes:
- **Student Information**: ID, Name, Section
- **Overall Statistics**: Total sessions, present count, absent count, overall percentage
- **Lab Statistics**: Lab sessions, lab present count, lab percentage (100% threshold)
- **Theory Statistics**: Theory sessions, theory present count, theory percentage (80% threshold)
- **Threshold Warnings**: Highlights students below required attendance thresholds

### 4. Export Formats

#### CSV Export
- Plain text format compatible with Excel, Google Sheets
- Includes report metadata (type, section, course, date range)
- Complete student statistics with percentages
- Threshold indicators

#### Excel Export (XLSX)
- Professional formatting with colors and borders
- Blue header with white text
- Red highlighting for students below threshold
- Auto-adjusted column widths
- Report metadata at the top

### 5. Visual Indicators
- **Red Background**: Students below attendance threshold
- **Color-coded Percentages**:
  - Green: ≥80% (Good)
  - Yellow: 60-79% (Warning)
  - Red: <60% (Critical)
- **Alert Icons**: Warning triangle for below-threshold students

## Backend Implementation

### New API Endpoints

#### 1. Generate Report
```
POST /api/instructor/reports/generate
```

**Request Body:**
```json
{
  "report_type": "daily|weekly|monthly|semester|yearly",
  "section_id": "A",
  "course_name": "web",
  "start_date": "2025-12-01",
  "end_date": "2025-12-07"
}
```

**Response:**
```json
{
  "report_type": "weekly",
  "section_id": "A",
  "course_name": "web",
  "start_date": "2025-12-01",
  "end_date": "2025-12-07",
  "total_sessions": 5,
  "total_students": 30,
  "data": [
    {
      "student_id": "UGR/1234/15",
      "name": "John Doe",
      "section": "A",
      "total_sessions": 5,
      "present_count": 4,
      "absent_count": 1,
      "percentage": 80.0,
      "lab_sessions": 2,
      "lab_present": 2,
      "lab_percentage": 100.0,
      "theory_sessions": 3,
      "theory_present": 2,
      "theory_percentage": 66.7,
      "below_threshold": true
    }
  ]
}
```

#### 2. Download CSV Report
```
POST /api/instructor/reports/download/csv
```

**Request Body:** Same as generate report

**Response:** CSV file download

#### 3. Download Excel Report
```
POST /api/instructor/reports/download/excel
```

**Request Body:** Same as generate report

**Response:** XLSX file download

### Security
- JWT authentication required
- Role-based access control (instructor, admin)
- Instructors only see their own students' data
- Admins can see all data

## Frontend Implementation

### New Page: InstructorReports.tsx
Location: `frontend/src/pages/InstructorReports.tsx`

**Features:**
- Report configuration form
- Real-time report generation
- Interactive data table
- Download buttons for CSV and Excel
- Summary statistics cards
- Visual threshold indicators

### Updated Components

#### InstructorDashboard.tsx
- Added "Download Reports" button (green)
- Positioned between "View Records" and "Settings"
- Routes to `/instructor/reports`

#### App.tsx
- Added route: `/instructor/reports`
- Protected with instructor role requirement

#### api.ts
- Added `generateReport()` function
- Added `downloadReportCSV()` function
- Added `downloadReportExcel()` function

## File Structure

```
backend/
├── blueprints/
│   └── instructor.py          # Added 3 new endpoints
frontend/
├── src/
│   ├── pages/
│   │   ├── InstructorReports.tsx    # NEW: Reports page
│   │   └── InstructorDashboard.tsx  # Updated: Added button
│   ├── lib/
│   │   └── api.ts                   # Updated: Added report APIs
│   └── App.tsx                      # Updated: Added route
```

## Usage Guide

### For Instructors

1. **Access Reports**
   - Login as instructor
   - Click "Download Reports" button on dashboard
   - Or navigate to `/instructor/reports`

2. **Generate Report**
   - Select report type (daily, weekly, monthly, semester, yearly)
   - Select section (required)
   - Select course (required)
   - For daily: Choose specific date (optional, defaults to today)
   - For weekly: Choose week start and end dates (optional, defaults to current week)
   - Click "Generate Report"

3. **View Results**
   - See summary statistics (total students, sessions, below threshold count)
   - Review detailed student table
   - Red-highlighted rows indicate students below threshold
   - Color-coded percentages for quick assessment

4. **Download Reports**
   - Click "Download CSV" for spreadsheet-compatible format
   - Click "Download Excel" for formatted XLSX with colors
   - Files are automatically named with report type and date

### Attendance Thresholds

- **Lab Sessions**: 100% attendance required
- **Theory Sessions**: 80% attendance required
- Students below either threshold are flagged

## Testing

### Manual Testing

1. **Start Backend**
   ```bash
   cd backend
   python app.py
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Flow**
   - Login as instructor (bekam/bekam123)
   - Click "Download Reports"
   - Generate a daily report for Section A
   - Verify statistics are correct
   - Download CSV and Excel files
   - Open files and verify formatting

### API Testing

Use the provided test script:
```bash
test_reports.bat
```

**Note:** Replace `YOUR_TOKEN_HERE` with actual JWT token from login.

To get token:
1. Login through frontend
2. Open browser DevTools (F12)
3. Go to Application > Local Storage
4. Copy the `token` value

## Database Requirements

The feature uses existing tables:
- `attendance`: Attendance records with session_type, section_id, course_name
- `students`: Student information
- `sessions`: Session details
- `users`: Instructor information

No new tables or migrations required.

## Dependencies

### Backend
- `openpyxl`: For Excel file generation
  ```bash
  pip install openpyxl
  ```

### Frontend
- `lucide-react`: Icons (already installed)
- `react-hot-toast`: Notifications (already installed)

## Error Handling

### Backend
- Missing filters: Returns 400 with error message
- No data found: Returns empty report with 0 sessions
- Database errors: Returns 500 with error details
- Authentication errors: Returns 401 unauthorized

### Frontend
- Missing required fields: Shows toast error
- API failures: Shows toast error with message
- Loading states: Shows spinner during generation
- Empty states: Shows helpful message when no report generated

## Performance Considerations

- Reports limited to 1000 records per query
- Efficient SQL queries with proper indexing
- In-memory file generation (no disk I/O)
- Automatic cleanup of temporary objects

## Future Enhancements

Possible improvements:
1. **Email Reports**: Send reports via email
2. **Scheduled Reports**: Automatic weekly/monthly reports
3. **Charts**: Visual graphs of attendance trends
4. **Comparison**: Compare sections or time periods
5. **PDF Export**: Generate PDF reports with charts
6. **Custom Thresholds**: Allow instructors to set custom thresholds
7. **Attendance Trends**: Show improvement/decline over time
8. **Student Notifications**: Auto-notify students below threshold

## Troubleshooting

### Report shows no data
- Verify section and course are correct
- Check date range includes actual sessions
- Ensure instructor has attendance records for selected filters

### Download fails
- Check `openpyxl` is installed for Excel downloads
- Verify browser allows file downloads
- Check backend logs for errors

### Students missing from report
- Verify students are in the selected section
- Check students table has correct section values
- Ensure attendance records exist for the date range

### Threshold calculations incorrect
- Lab threshold: 100% (all sessions must be attended)
- Theory threshold: 80% (4 out of 5 sessions minimum)
- Mixed sessions: Both thresholds must be met

## Summary

The Instructor Reports feature provides a complete solution for generating, viewing, and downloading attendance reports with:
- ✅ Multiple report types (daily, weekly, monthly, semester, yearly)
- ✅ Flexible filtering (section, course, date range)
- ✅ Comprehensive statistics (overall, lab, theory percentages)
- ✅ Threshold warnings (100% lab, 80% theory)
- ✅ Multiple export formats (CSV, Excel)
- ✅ Professional formatting and visual indicators
- ✅ Secure, role-based access control
- ✅ User-friendly interface with real-time generation

The feature is production-ready and fully integrated into the SmartAttendance system.
