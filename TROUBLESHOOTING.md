# Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### 1. MongoDB Connection Failed

**Error:** `MongoDB connection failed: ...`

**Solutions:**
- Verify MongoDB connection string in `backend/.env`
- Check if MongoDB Atlas IP whitelist includes your IP
- Test connection string using MongoDB Compass
- Ensure network connectivity

```bash
# Test MongoDB connection
python -c "from pymongo import MongoClient; client = MongoClient('your-connection-string'); print(client.server_info())"
```

#### 2. Model Files Not Found

**Error:** `Recognition model missing` or `Classifier not found`

**Solutions:**
- Ensure model files are in `backend/models/Classifier/`:
  - `face_classifier_v1.pkl`
  - `label_encoder.pkl`
  - `label_encoder_classes.npy`
- Check file permissions
- Verify file paths in config

```bash
# Check if files exist
ls -la backend/models/Classifier/
```

#### 3. Import Errors

**Error:** `ModuleNotFoundError: No module named '...'`

**Solutions:**
- Activate virtual environment
- Reinstall dependencies

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 4. Port Already in Use

**Error:** `Address already in use`

**Solutions:**
- Change port in `backend/.env`
- Kill process using the port

```bash
# Find process using port 5000
lsof -i :5000  # On Linux/Mac
netstat -ano | findstr :5000  # On Windows

# Kill process
kill -9 <PID>  # On Linux/Mac
taskkill /PID <PID> /F  # On Windows
```

#### 5. CORS Errors

**Error:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solutions:**
- Add frontend URL to `CORS_ORIGINS` in `backend/.env`
- Restart backend server

```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend Issues

#### 1. Cannot Connect to Backend

**Error:** `Network Error` or `Failed to fetch`

**Solutions:**
- Verify backend is running
- Check `VITE_API_URL` in `frontend/.env`
- Ensure no firewall blocking

```bash
# Test backend connection
curl http://localhost:5000/health
```

#### 2. Camera Not Working

**Error:** `Failed to access camera` or `Permission denied`

**Solutions:**
- Grant camera permissions in browser
- Use HTTPS in production (required for camera access)
- Check if camera is being used by another application
- Try different browser

**Browser Permissions:**
- Chrome: Settings → Privacy and security → Site Settings → Camera
- Firefox: Preferences → Privacy & Security → Permissions → Camera
- Safari: Preferences → Websites → Camera

#### 3. Build Errors

**Error:** Build fails with TypeScript errors

**Solutions:**
- Clear node_modules and reinstall

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 4. Blank Page After Build

**Solutions:**
- Check browser console for errors
- Verify API URL is correct
- Clear browser cache
- Check if backend is accessible

### Recognition Issues

#### 1. Low Recognition Accuracy

**Solutions:**
- Adjust confidence threshold in `backend/.env`
- Ensure good lighting conditions
- Register more face images per student
- Use higher quality camera
- Retrain model with more diverse images

```env
RECOGNITION_THRESHOLD=0.50  # Lower for more lenient recognition
```

#### 2. "Unknown Student" for Registered Students

**Solutions:**
- Verify student is in training data
- Check if model files are up to date
- Reload models using debug endpoint

```bash
curl -X POST http://localhost:5000/api/debug/reload-models
```

#### 3. "No Face Detected"

**Solutions:**
- Ensure face is clearly visible
- Improve lighting
- Face camera directly
- Remove obstructions (glasses, mask, etc.)
- Adjust camera angle

### Docker Issues

#### 1. Docker Build Fails

**Solutions:**
- Check Docker is running
- Ensure sufficient disk space
- Clear Docker cache

```bash
docker system prune -a
docker-compose build --no-cache
```

#### 2. Container Exits Immediately

**Solutions:**
- Check container logs

```bash
docker-compose logs backend
docker-compose logs frontend
```

- Verify environment variables
- Check if ports are available

#### 3. Cannot Access Application

**Solutions:**
- Verify containers are running

```bash
docker-compose ps
```

- Check port mappings
- Ensure no firewall blocking

### Database Issues

#### 1. Duplicate Key Error

**Error:** `E11000 duplicate key error`

**Solutions:**
- Username or email already exists
- Student ID already exists
- Use different credentials

#### 2. Slow Queries

**Solutions:**
- Ensure indexes are created
- Check MongoDB Atlas cluster tier
- Optimize queries
- Consider upgrading database plan

### Performance Issues

#### 1. Slow Recognition

**Solutions:**
- Use smaller image sizes
- Reduce capture interval
- Use GPU for inference (if available)
- Optimize model
- Use faster detection method

#### 2. High Memory Usage

**Solutions:**
- Reduce image quality
- Limit concurrent requests
- Increase server resources
- Use model quantization

### Authentication Issues

#### 1. Token Expired

**Error:** `401 Unauthorized`

**Solutions:**
- Login again
- Increase token expiry time

```env
JWT_EXPIRY_HOURS=24
```

#### 2. Invalid Credentials

**Solutions:**
- Verify username and password
- Check if user exists in database
- Reset password if needed

### Development Issues

#### 1. Hot Reload Not Working

**Solutions:**
- Restart development server
- Check file watcher limits (Linux)

```bash
# Increase file watcher limit
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

#### 2. Environment Variables Not Loading

**Solutions:**
- Restart development server after changing .env
- Verify .env file location
- Check variable names (VITE_ prefix for frontend)

## Debug Tools

### Check Model Status

```bash
curl http://localhost:5000/api/debug/model-status
```

### Test Recognition

```bash
curl -X POST -F "image=@test_image.jpg" http://localhost:5000/api/debug/recognition-test
```

### Check Backend Health

```bash
curl http://localhost:5000/health
```

### View Backend Logs

```bash
# Development
python app.py

# Docker
docker-compose logs -f backend

# Production (systemd)
journalctl -u smartattendance -f
```

### View Frontend Logs

```bash
# Development
npm run dev

# Docker
docker-compose logs -f frontend

# Nginx
tail -f /var/log/nginx/error.log
```

## Getting Help

If you're still experiencing issues:

1. Check the logs for detailed error messages
2. Search existing GitHub issues
3. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version, Node version)
   - Relevant logs

## Useful Commands

```bash
# Backend
cd backend
python app.py                    # Run backend
python seed_db.py               # Seed database
pip list                        # List installed packages

# Frontend
cd frontend
npm run dev                     # Run development server
npm run build                   # Build for production
npm run preview                 # Preview production build

# Docker
docker-compose up               # Start all services
docker-compose down             # Stop all services
docker-compose logs -f          # View logs
docker-compose restart          # Restart services

# Database
mongosh "your-connection-string"  # Connect to MongoDB
```

## Performance Optimization

### Backend
- Use Gunicorn with multiple workers
- Enable caching for model predictions
- Use Redis for session storage
- Optimize database queries

### Frontend
- Enable code splitting
- Lazy load components
- Optimize images
- Use CDN for static assets

### Recognition
- Use GPU acceleration
- Batch process images
- Cache embeddings
- Use lighter models
