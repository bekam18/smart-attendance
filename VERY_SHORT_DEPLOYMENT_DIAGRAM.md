# 5.2.2 Deployment Diagram

The deployment diagram shows how the Smart Attendance System is distributed across hardware and software components. The system uses a client-server architecture suitable for local network or cloud deployment.

## Deployment Architecture

**Client Devices:** Web browsers with webcam access (Admin, Instructor, Student)  
**Web Server:** Flask application (Port 5000) - Handles API requests and face recognition  
**Database Server:** MySQL (Port 3306) - Stores users, sessions, and attendance records  
**Network:** HTTP/HTTPS communication between client and server

## System Requirements

### Client Side (Instructor/Admin)
- Laptop/Desktop with webcam (720p minimum)
- 4GB RAM, modern web browser
- No software installation required

### Server Side
- **CPU:** Intel Core i5 or equivalent
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 20GB SSD
- **OS:** Windows 10+, Ubuntu 20.04+, or macOS

### Software Stack
- **Frontend:** React with TypeScript
- **Backend:** Python 3.8+, Flask, OpenCV, InsightFace
- **Database:** MySQL 8.0+

## Deployment Options

**Local Network:** Backend and database on dedicated server, clients access via local IP  
**Cloud Deployment:** Backend on cloud platform (AWS/Azure), supports remote access and scalability

This architecture supports both small-scale local installations and future cloud expansion.
