# Deployment Guide

## Local Development

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.sample .env
```

5. Update `.env` with your MongoDB connection string

6. Place model files in `models/Classifier/`:
   - face_classifier_v1.pkl
   - label_encoder.pkl
   - label_encoder_classes.npy

7. Run the backend:
```bash
python app.py
```

Backend will run on http://localhost:5000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.sample .env
```

4. Run the frontend:
```bash
npm run dev
```

Frontend will run on http://localhost:5173

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Steps

1. Ensure model files are in `backend/models/Classifier/`

2. Update environment variables in `docker-compose.yml`

3. Build and run:
```bash
docker-compose up --build
```

4. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:5000

5. Stop the application:
```bash
docker-compose down
```

## Production Deployment

### Backend (Flask)

#### Option 1: Using Gunicorn

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Option 2: Using uWSGI

1. Install uWSGI:
```bash
pip install uwsgi
```

2. Create `uwsgi.ini`:
```ini
[uwsgi]
module = app:app
master = true
processes = 4
socket = 0.0.0.0:5000
protocol = http
```

3. Run:
```bash
uwsgi uwsgi.ini
```

### Frontend (React)

1. Build for production:
```bash
cd frontend
npm run build
```

2. Serve with Nginx:

Create `/etc/nginx/sites-available/smartattendance`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/smartattendance/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

3. Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/smartattendance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Cloud Deployment

### AWS

#### Backend (EC2 + Elastic Beanstalk)

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
cd backend
eb init
```

3. Create environment:
```bash
eb create smartattendance-env
```

4. Deploy:
```bash
eb deploy
```

#### Frontend (S3 + CloudFront)

1. Build:
```bash
cd frontend
npm run build
```

2. Upload to S3:
```bash
aws s3 sync dist/ s3://your-bucket-name
```

3. Configure CloudFront distribution

### Heroku

#### Backend

1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Deploy:
```bash
cd backend
heroku create smartattendance-api
git push heroku main
```

#### Frontend

1. Create `static.json`:
```json
{
  "root": "dist",
  "routes": {
    "/**": "index.html"
  }
}
```

2. Deploy:
```bash
cd frontend
heroku create smartattendance-web
heroku buildpacks:add heroku/nodejs
git push heroku main
```

### DigitalOcean

1. Create Droplet (Ubuntu 22.04)

2. SSH into droplet:
```bash
ssh root@your-droplet-ip
```

3. Install dependencies:
```bash
apt update
apt install python3-pip nodejs npm nginx
```

4. Clone repository:
```bash
git clone your-repo-url
cd SmartAttendance
```

5. Setup backend:
```bash
cd backend
pip3 install -r requirements.txt
```

6. Setup frontend:
```bash
cd frontend
npm install
npm run build
```

7. Configure Nginx (see above)

8. Setup systemd service for backend:

Create `/etc/systemd/system/smartattendance.service`:
```ini
[Unit]
Description=SmartAttendance Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/root/SmartAttendance/backend
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

9. Start service:
```bash
systemctl enable smartattendance
systemctl start smartattendance
```

## Environment Variables

### Backend
- `SECRET_KEY`: Flask secret key
- `MONGODB_URI`: MongoDB connection string
- `JWT_SECRET_KEY`: JWT secret key
- `RECOGNITION_THRESHOLD`: Confidence threshold (0.0-1.0)
- `FLASK_PORT`: Port number (default: 5000)

### Frontend
- `VITE_API_URL`: Backend API URL

## SSL/HTTPS Setup

### Using Let's Encrypt (Certbot)

1. Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. Obtain certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

3. Auto-renewal:
```bash
sudo certbot renew --dry-run
```

## Monitoring

### Backend Logs

```bash
# Docker
docker-compose logs -f backend

# Systemd
journalctl -u smartattendance -f
```

### Frontend Logs

```bash
# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log
```

## Backup

### MongoDB Backup

```bash
mongodump --uri="your-mongodb-uri" --out=/backup/$(date +%Y%m%d)
```

### Model Files Backup

```bash
tar -czf models-backup-$(date +%Y%m%d).tar.gz backend/models/
```

## Troubleshooting

### Backend not starting
- Check MongoDB connection
- Verify model files exist
- Check port availability

### Frontend not connecting to backend
- Verify VITE_API_URL in .env
- Check CORS settings
- Verify backend is running

### Camera not working
- Use HTTPS in production
- Check browser permissions
- Verify getUserMedia support

### Recognition not working
- Verify model files are loaded
- Check model file permissions
- Review recognition threshold
