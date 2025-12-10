# 3.3 Functional Requirements

The system must meet the following functional requirements to perform attendance tracking accurately and efficiently. These requirements are organized by user role and system functionality.

## Core Attendance Functions

### 1. Real-Time Image Capture
The system captures live facial images using a webcam or camera during class sessions.

**Implementation Details:**
- **Capture Method:** Browser-based webcam access using MediaStream API
- **Capture Frequency:** Automatic capture every 2 seconds during active sessions
- **Image Format:** JPEG/PNG, transmitted as base64 or multipart form data
- **Resolution:** Minimum 640x480, recommended 1280x720
- **Preview Display:** Live camera feed shown to instructor during session

**User Actions:**
- Instructor clicks "Start Camera" to begin capture
- Students position themselves in front of camera
- System automatically captures and processes frames

### 2. Face Detection and Recognition
The system detects faces in the captured image and matches them with stored data using pre-trained AI models.

**Implementation Details:**
- **Detection Method:** InsightFace detector with OpenCV fallback
- **Recognition Model:** Pre-trained face recognition model with embeddings
- **Processing Time:** 1-3 seconds per face
- **Confidence Threshold:** 0.6 (60%) minimum for positive match
- **Multi-Face Support:** Can detect multiple faces but processes one at a time

**Recognition Process:**
1. Detect face in captured image
2. Extract facial features (embeddings)
3. Compare with stored embeddings in database
4. Calculate similarity score (confidence)
5. Return match if confidence > threshold

**Error Handling:**
- "No face detected" - No face found in image
- "Unknown face" - Face detected but confidence < threshold
- "Wrong section" - Student recognized but not in current class section

### 3. Attendance Marking
Once a face is recognized, the system logs attendance immediately with a timestamp.

**Implementation Details:**
- **Automatic Logging:** Attendance recorded upon successful recognition
- **Timestamp:** UTC timestamp with local time display
- **Status Values:** "present" or "absent"
- **Duplicate Prevention:** 5-minute window prevents rapid re-marking
- **Session Validation:** Verifies student belongs to session's section/year

**Attendance Record Fields:**
- Student ID
- Session ID
- Instructor ID
- Section ID and Year
- Session Type (lab/theory)
- Time Block (morning/afternoon)
- Course Name
- Timestamp
- Date
- Confidence Score
- Status (present/absent)

**Business Rules:**
- Student can only be marked present if face recognized with confidence ≥ 60%
- Student must belong to the session's section and year
- Duplicate marking within 5 minutes updates timestamp only
- Multiple markings allowed when session reopened (12-hour retake feature)

### 4. Confidence Score Display
The system provides a confidence level with each recognition to help verify accuracy.

**Implementation Details:**
- **Score Range:** 0.0 to 1.0 (0% to 100%)
- **Display Format:** Percentage with one decimal place (e.g., "85.3%")
- **Color Coding:**
  - Green (≥80%): High confidence
  - Yellow (60-79%): Medium confidence
  - Red (<60%): Low confidence (rejected)

**Visibility:**
- Real-time display during recognition
- Stored in attendance records
- Visible in attendance list
- Included in exported reports

**Use Cases:**
- Instructors can verify recognition accuracy
- Low confidence scores may indicate need for model retraining
- Helps identify students who need better training images

## User Management Functions

### 5. User Login and Access Control
Different users (e.g., admin, instructor, student) can log in securely with role-based permissions.

**Implementation Details:**
- **Authentication:** JWT (JSON Web Token) based authentication
- **Password Security:** bcrypt hashing with salt
- **Session Duration:** 24-hour token expiration
- **Login Endpoint:** POST /api/auth/login

**User Roles and Permissions:**

#### Admin Role:
- Add/edit/delete instructors and students
- View all attendance records across all sessions
- Export attendance data (CSV/Excel)
- Manage system settings
- View system statistics and dashboards
- Enable/disable user accounts
- Access all courses and sections

#### Instructor Role:
- Start/stop/reopen attendance sessions
- View own sessions and attendance records
- Mark students as present/absent
- Generate attendance reports for own classes
- Export attendance data for own courses
- Change own password
- View student lists for assigned sections
- Access only assigned courses and sections

#### Student Role:
- View own attendance history
- Filter attendance by course and instructor
- View attendance statistics (present/absent counts)
- View enrolled courses
- Change own password
- Cannot modify attendance records

**Security Features:**
- Password reset via email with secure tokens
- SQL injection protection on all endpoints
- Role-based route protection
- Automatic logout on token expiration
- Failed login attempt logging

### 6. Student Registration
New students can be added by uploading facial images and basic personal information.

**Implementation Details:**
- **Registration Method:** Admin-only function
- **Required Information:**
  - Student ID (unique)
  - Full Name
  - Email Address
  - Department
  - Year (1, 2, 3, or 4)
  - Section (A, B, C, D, etc.)
  - Password (auto-generated or manual)

**Face Registration Process:**
1. Admin creates student account with basic info
2. System generates user credentials
3. Student credentials provided to student
4. Facial images collected separately for model training
5. Model retrained with new student data

**Validation Rules:**
- Student ID must be unique
- Email must be valid format and unique
- Year must be numeric (1-4)
- Section must be single letter
- All required fields must be filled

**Bulk Registration:**
- Admin can import multiple students via CSV
- Batch processing for large enrollments
- Validation errors reported per student

## Session Management Functions

### 7. Session Creation and Control
Instructors can create, start, stop, and manage attendance sessions.

**Session Creation:**
- **Required Fields:**
  - Session Type (lab/theory)
  - Time Block (morning/afternoon)
  - Section (A, B, C, D)
  - Year (automatically from instructor profile)
  - Course (optional, from instructor's assigned courses)

**Session Statuses:**
- **Active:** Session is running, camera is on
- **Stopped Daily:** Session stopped for the day, can reopen after 12 hours
- **Ended Semester:** Session permanently ended, cannot reopen
- **Completed:** Legacy status for old sessions

**Session Actions:**

#### Start Session:
- Creates new session with active status
- Initializes attendance list
- Enables camera for face recognition
- Displays live attendance tracking

#### Stop Camera (Daily End):
- Marks all absent students automatically
- Sets status to "stopped_daily"
- Records end time
- Can be reopened after 12 hours

#### End Session (Semester End):
- Permanently closes session
- Sets status to "ended_semester"
- Cannot be reopened
- Use only at semester completion

#### Reopen Session (12-Hour Retake):
- Available after 12 hours from stop time
- Reactivates session (status → active)
- Preserves all previous attendance records
- Allows new attendance to be taken
- Shows countdown timer until eligible

**Session Display:**
- List of all instructor's sessions
- Status badges with color coding
- Attendance count per session
- Start/end timestamps
- Reopen eligibility indicator

### 8. Manual Attendance Update
Instructors can override or correct attendance manually if recognition fails.

**Implementation Details:**
- **Current Limitation:** Manual update not yet implemented in UI
- **Workaround:** Admin can update via database or future admin panel
- **Planned Feature:** Instructor dashboard with manual attendance controls

**Use Cases:**
- Student face not recognized due to technical issues
- Camera malfunction during class
- Student arrived late after camera stopped
- Correction of false absences
- Emergency attendance recording

**Audit Trail:**
- All manual updates logged with timestamp
- Instructor ID recorded for accountability
- Original vs. updated status tracked
- Reason for change (optional field)

### 9. Automatic Absent Marking
System automatically marks students as absent when camera is stopped.

**Implementation Details:**
- **Trigger:** Instructor clicks "Stop Camera" button
- **Process:**
  1. Retrieves all students in session's section/year
  2. Identifies students not marked present
  3. Creates attendance records with status "absent"
  4. Records timestamp and session details

**Business Rules:**
- Only marks students not already present
- Uses same session metadata (course, section, year)
- Confidence score set to 0.0 for absent records
- Cannot be automatically reversed (requires manual correction)

## Reporting and Data Export Functions

### 10. Attendance Reporting
The system can generate reports based on date, student, or class and export them in formats like CSV or Excel.

**Report Types:**

#### Instructor Reports:
- **Date Range Report:** Attendance for specific date range
- **Course Report:** All attendance for a specific course
- **Section Report:** Attendance by section and year
- **Student Report:** Individual student attendance history
- **Session Report:** Detailed report for single session

**Report Filters:**
- Start Date and End Date
- Course Name
- Section ID
- Year
- Session Type (lab/theory)
- Time Block (morning/afternoon)

**Report Metrics:**
- Total Sessions
- Total Present Count
- Total Absent Count
- Attendance Percentage
- Student-wise breakdown
- Date-wise breakdown

**Export Formats:**
- **CSV:** Comma-separated values for Excel/spreadsheet import
- **Excel (.xlsx):** Formatted spreadsheet with headers and styling
- **Download:** Direct browser download with auto-generated filename

#### Admin Reports:
- **All Attendance Records:** Complete system-wide attendance data
- **Instructor Performance:** Sessions and attendance by instructor
- **Daily Statistics:** System usage and attendance metrics
- **Active Sessions:** Currently running sessions
- **Recent Sessions:** Last 10 sessions across all instructors

**Report Generation Process:**
1. User selects report type and filters
2. System queries database with filters
3. Aggregates data and calculates metrics
4. Formats data for display or export
5. Generates downloadable file or displays in UI

### 11. Student Attendance History
Students can view their own attendance records with filtering options.

**Implementation Details:**
- **Access:** Student dashboard
- **Display:** Table with all attendance records
- **Sorting:** By date (newest first)

**Filters Available:**
- **By Course:** Filter by specific course name
- **By Instructor:** Filter by instructor who recorded attendance
- **Clear Filters:** Reset to show all records

**Information Displayed:**
- Date and Time
- Course Name
- Instructor Name
- Session Type (lab/theory)
- Time Block (morning/afternoon)
- Status (present/absent)
- Confidence Score (if present)

**Statistics:**
- Total Courses Enrolled
- Total Attendance Records
- Present Count
- Absent Count
- Attendance Percentage

## Database Management Functions

### 12. Database Management
The system stores and retrieves student data, facial embeddings, and attendance logs securely.

**Database Technology:**
- **DBMS:** MySQL 8.0+
- **Connection:** mysql-connector-python
- **Connection Pooling:** Enabled for performance
- **Character Set:** utf8mb4 for international character support

**Database Tables:**

#### Users Table:
- Stores login credentials for all users
- Fields: id, username, password (hashed), email, role, name
- Indexes: username (unique), email (unique)

#### Students Table:
- Stores student profile information
- Fields: id, user_id, student_id, name, email, department, year, section, face_registered
- Indexes: student_id (unique), user_id (foreign key)
- Links to users table via user_id

#### Instructors Table (via Users):
- Instructors stored in users table with role='instructor'
- Additional fields: course_name, class_year, session_types (JSON)
- Courses stored as JSON array for multi-course support

#### Sessions Table:
- Stores attendance session information
- Fields: id, instructor_id, instructor_name, section_id, year, session_type, time_block, course_name, name, start_time, end_time, status, attendance_count
- Indexes: instructor_id, start_time, status
- Foreign key: instructor_id → users.id

#### Attendance Table:
- Stores all attendance records
- Fields: id, student_id, session_id, instructor_id, section_id, year, session_type, time_block, course_name, class_year, timestamp, date, confidence, status
- Indexes: student_id, session_id, date, timestamp
- Foreign keys: session_id → sessions.id, instructor_id → users.id
- **No unique constraint** - allows multiple records per day (12-hour retake feature)

**Data Security:**
- Passwords hashed with bcrypt (12 rounds)
- Facial embeddings stored as binary data
- Parameterized queries prevent SQL injection
- Foreign key constraints maintain referential integrity
- Cascade delete for related records

**Backup and Recovery:**
- Regular database backups recommended
- Transaction support for data consistency
- Error logging for troubleshooting
- Audit trail for critical operations

**Performance Optimization:**
- Indexes on frequently queried columns
- Connection pooling for concurrent requests
- Query optimization for large datasets
- Pagination for large result sets

## Additional Functional Requirements

### 13. Password Reset Functionality
Users can reset forgotten passwords via email verification.

**Implementation Details:**
- **Trigger:** "Forgot Password" link on login page
- **Process:**
  1. User enters email address
  2. System generates secure reset token (32 bytes)
  3. Token stored with 1-hour expiration
  4. Email sent with reset link
  5. User clicks link and enters new password
  6. Token validated and password updated

**Security Features:**
- Tokens are single-use only
- 1-hour expiration for security
- Secure token generation (cryptographically random)
- Email verification required
- Password strength validation

**Email Configuration:**
- Supports multiple providers (Gmail, Outlook, SendGrid)
- Professional HTML email template
- Fallback: Prints token to console if email not configured

### 14. Multi-Course Support for Instructors
Instructors can be assigned to multiple courses and manage them independently.

**Implementation Details:**
- **Storage:** Courses stored as JSON array in users table
- **Display:** All courses shown on instructor dashboard
- **Session Creation:** Dropdown to select course when starting session
- **Filtering:** Reports can be filtered by specific course

**Benefits:**
- Single instructor can teach multiple subjects
- Separate attendance tracking per course
- Flexible course assignment
- Easy course addition/removal by admin

### 15. Section and Year Validation
System validates that students belong to the correct section and year for each session.

**Implementation Details:**
- **Validation Point:** During face recognition
- **Check:** Student's section/year must match session's section/year
- **Result:** "Wrong section" error if mismatch
- **Display:** Clear error message with student and session details

**Business Rules:**
- Student in Section A cannot be marked in Section B session
- Student in Year 3 cannot be marked in Year 4 session
- Validation prevents cross-section attendance errors
- Ensures data accuracy and integrity

### 16. Real-Time Attendance Display
Live attendance list updates as students are recognized.

**Implementation Details:**
- **Display:** Side panel showing all attendance records
- **Updates:** Automatic refresh after each recognition
- **Information Shown:**
  - Student name and ID
  - Status (present/absent)
  - Timestamp (for present)
  - Confidence score (for present)
  - Color coding (green for present, red for absent)

**Sorting:**
- Present students shown first
- Sorted by timestamp (most recent first)
- Absent students shown at bottom

**Statistics:**
- Present count (green badge)
- Absent count (red badge)
- Total students in section

## Summary of Functional Requirements

| Category | Requirements | Status |
|----------|-------------|--------|
| **Core Attendance** | Image capture, face detection, recognition, marking | ✅ Implemented |
| **User Management** | Login, access control, registration | ✅ Implemented |
| **Session Management** | Create, start, stop, reopen sessions | ✅ Implemented |
| **Reporting** | Generate reports, export CSV/Excel | ✅ Implemented |
| **Database** | Secure storage, retrieval, management | ✅ Implemented |
| **Security** | Password reset, SQL injection protection | ✅ Implemented |
| **Advanced Features** | Multi-course, 12-hour retake, validation | ✅ Implemented |
| **Manual Updates** | Manual attendance correction | ⏳ Planned |

## Non-Functional Requirements Met

- **Performance:** 1-3 second recognition time
- **Scalability:** Supports 100+ students per section
- **Security:** JWT auth, bcrypt hashing, SQL injection protection
- **Usability:** Intuitive UI with clear status indicators
- **Reliability:** Error handling and recovery mechanisms
- **Maintainability:** Modular code structure, comprehensive documentation

## Conclusion

The smart attendance system successfully implements all core functional requirements for automated attendance tracking using facial recognition. The system provides role-based access control, real-time attendance marking, comprehensive reporting, and secure database management. Advanced features like 12-hour session reopening, multi-course support, and automatic absent marking enhance the system's flexibility and usability for academic institutions.
