# Password Reset - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Configure Email (Optional)

Edit `backend/.env` and add:

```env
# For Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@smartattendance.com
FROM_NAME=SmartAttendance
FRONTEND_URL=http://localhost:5173
```

**Note:** Without email config, tokens will print to console for testing.

### Step 2: Restart Backend

```bash
# Stop current backend (Ctrl+C)
# Then restart:
cd backend
python app.py
```

### Step 3: Test the Feature

1. Go to http://localhost:5173/login
2. Click "Forgot password?"
3. Enter email: `admin@smartattendance.com`
4. Check email OR console for reset token
5. Click reset link or go to: `http://localhost:5173/reset-password?token=YOUR_TOKEN`
6. Enter new password (min 6 chars)
7. Login with new password

## 📧 Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password

3. **Update .env**
   ```env
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   ```

## 🧪 Testing Without Email

If you skip email configuration:

1. Request password reset
2. Check backend console for token:
   ```
   🔗 Reset token (for testing): abc123xyz...
   ```
3. Manually visit:
   ```
   http://localhost:5173/reset-password?token=abc123xyz...
   ```

## ✅ What's Included

- ✅ Forgot password page with email input
- ✅ Professional HTML email template
- ✅ Secure token generation (expires in 1 hour)
- ✅ Reset password page with validation
- ✅ Password confirmation
- ✅ Success/error handling
- ✅ Automatic redirect to login

## 🔒 Security Features

- Tokens expire after 1 hour
- Single-use tokens (deleted after reset)
- Email enumeration protection
- Password strength validation
- Secure bcrypt hashing

## 📝 Test Accounts

Use these emails to test:

- `admin@smartattendance.com` (Admin)
- `instructor@smartattendance.com` (Instructor)
- `student@smartattendance.com` (Student)

## 🐛 Troubleshooting

**Email not sending?**
- Check SMTP credentials in `.env`
- Use app password for Gmail (not account password)
- Check backend console for errors

**Token invalid?**
- Tokens expire after 1 hour
- Request a new reset link

**Can't find email?**
- Check spam/junk folder
- Verify email address is correct
- Use console token for testing

## 🎯 Quick Test Command

```bash
test_password_reset.bat
```

Or manually:

```bash
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"admin@smartattendance.com\"}"
```

## 📚 Full Documentation

See `PASSWORD_RESET_SETUP.md` for:
- Detailed configuration options
- Production deployment guide
- API documentation
- Email provider options
- Security best practices

---

**Ready to use!** The feature works immediately with console logging. Add email config when ready for production.
