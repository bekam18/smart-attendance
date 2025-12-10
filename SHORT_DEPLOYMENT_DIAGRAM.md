# 5.2.2 Deployment Diagram

The deployment diagram illustrates how the Smart Attendance System is distributed across hardware and software environments. The system uses a client-server architecture that can run on local networks or be deployed to cloud infrastructure.

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT DEVICES                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Admin PC   │  │ Instructor   │  │  Student     │     │
│  │              │  │   Laptop     │  │   Device     │     │
│  │ Web Browser  │  │ Web Browser  │  │ Web Browser  │     │
│  │   + Webcam   │  │   + Webcam   │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │ HTTP/HTTPS                     │
└────────────────────────────┼────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Web Server    │
                    │  (Flask/Python) │
                    │  Port: 5000     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Database Server │
                    │     (MySQL)     │
                    │   Port: 3306    │
                    └─────────────────┘
```

## Deployment Configuration

### Current Setup (Local Network)
- **Frontend Server:** React app (Port 5173) - Development or static hosting
- **Backend Server:** Flask application (Port 5000) - Handles API requests
- **Database Server:** MySQL (Port 3306) - Data storage
- **Network:** Local network (LAN) or localhost for testing

### Hardware Requirements

**Client Devices (Instructor/Admin):**
- Laptop/Desktop with webcam (720p minimum, 1080p recommended)
- 4GB RAM minimum, 8GB recommended
- Modern web browser (Chrome 90+, Firefox 88+, Edge 90+)
- Internet connection for accessing server

**Server (Backend + Database):**
- CPU: Intel Core i5 or equivalent (i7 recommended for multiple sessions)
- RAM: 8GB minimum, 16GB recommended
- Storage: 20GB SSD for system, additional space for attendance data
- Operating System: Windows 10/11, Ubuntu 20.04+, or macOS

### Software Requirements

**Client Side:**
- Modern web browser with webcam support
- No additional software installation required

**Server Side:**
- **Backend:** Python 3.8+, Flask, OpenCV, InsightFace, MySQL connector
- **Database:** MySQL 8.0+
- **Operating System:** Windows, Linux, or macOS

## Deployment Options

### Option 1: Single Machine (Development/Testing)
- All components run on one computer
- Suitable for testing and small-scale deployment
- Frontend: localhost:5173, Backend: localhost:5000, Database: localhost:3306

### Option 2: Local Network (Production)
- Backend and database on dedicated server
- Clients access via local IP address
- Suitable for single institution deployment
- Example: Backend at 192.168.1.100:5000

### Option 3: Cloud Deployment (Future Scalability)
- Backend deployed to cloud platform (AWS, Azure, Google Cloud)
- Database hosted on cloud database service
- Clients access via public domain
- Supports multiple institutions and remote access

## Network Communication

- **Protocol:** HTTP/HTTPS for API communication
- **Data Format:** JSON for API requests/responses
- **File Transfer:** Multipart form-data for image uploads
- **Authentication:** JWT tokens in HTTP headers
- **Security:** HTTPS recommended for production deployment

## Scalability Considerations

- **Horizontal Scaling:** Add more backend servers with load balancer
- **Database Replication:** Master-slave setup for read-heavy operations
- **CDN Integration:** Serve static frontend files from CDN
- **Caching:** Redis/Memcached for session and query caching

This deployment architecture supports both small-scale local installations and future expansion to cloud-based infrastructure for larger deployments.
