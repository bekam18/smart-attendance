export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'instructor' | 'student';
  name: string;
  student_id?: string;
}

export interface Student {
  id: string;
  student_id: string;
  name: string;
  email: string;
  department: string;
  year: string;
  face_registered: boolean;
  created_at: string;
}

export interface AttendanceRecord {
  id: string;
  student_id: string;
  student_name: string;
  session_id: string;
  session_name?: string;
  timestamp: string;
  date: string;
  confidence: number;
  status: string;
}

export interface Session {
  id: string;
  name: string;
  instructor_name: string;
  course: string;
  session_type?: 'lab' | 'theory';
  time_block?: 'morning' | 'afternoon';
  section_id?: string;
  year?: string;
  start_time: string;
  end_time: string | null;
  status: 'active' | 'completed';
  attendance_count: number;
}

export interface RecognitionResult {
  status: 'recognized' | 'unknown' | 'no_face' | 'already_marked' | 'error';
  student_id?: string;
  student_name?: string;
  confidence?: number;
  message?: string;
  error?: string;
  requires_model?: boolean;
}
