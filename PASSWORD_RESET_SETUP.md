# Password Reset Feature - Setup Guide

## Overview
The password reset feature allows users to reset their passwords via email. Users receive a secure reset link that expires in 1 hour.

## Features Implemented

### Frontend
- **Forgot Password Page** (`/forgot-password`)
  - Email input form
  - Email validation
  - Success confirmation screen
  
- **Reset Password Page** (`/reset-password?token=xxx`)
  - Token verification
  - New password form with confirmation
  - Password strength validation (min 6 characters)
  - Success/error handling

- **Login Page Update**
  - Added "Forgot password?" link

### Backend
- **API Endpoints** (in `backend/blueprints/auth.py`)
  - `POST /api/auth/forgot-password` - Request password reset
  - `POST /api/auth/verify-reset-token` - Verify reset token
  - `POST /api/auth/reset-password` - Reset password with token

- **Email Service** (`backend/utils/email_service.py`)
  - Professional HTML email templates
  - SMTP configuration
  - Fallback to console logging for testing

## Email Configuration

### Option 1: Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Copy the 16-character password

3. **Update `.env` file**:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=noreply@smartattendance.com
FROM_NAME=SmartAttendance
FRONTEND_URL=http://localhost:5173
```

### Option 2: Custom Domain Email

If you have a domain email (e.g., `admin@yourdomain.com`):

```env
SMTP_SERVER=smtp.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=admin@yourdomain.com
SMTP_PASSWORD=your-email-password
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=SmartAttendance
FRONTEND_URL=http://localhost:5173
```

### Option 3: Other Email Providers

**Outlook/Office365:**
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

**Yahoo:**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

**SendGrid (Production):**
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

## Testing Without Email Configuration

If you don't configure email settings, the system will:
1. Print reset tokens to the console
2. Return the token in the API response (development only)
3. Allow you to manually construct reset URLs

**Example console output:**
```
⚠️  Email service not configured
📧 Email would be sent to: user@example.com
🔗 Reset token (for testing): abc123xyz...
```

**Manual reset URL:**
```
http://localhost:5173/reset-password?token=abc123xyz...
```

## User Flow

1. **User clicks "Forgot password?" on login page**
2. **User enters their email address**
3. **System sends reset email** (or prints token to console)
4. **User clicks reset link in email**
5. **System verifies token** and shows reset form
6. **User enters new password** (twice for confirmation)
7. **Password is updated** and user is redirected to login

## Security Features

- ✅ Reset tokens are cryptographically secure (32 bytes)
- ✅ Tokens expire after 1 hour
- ✅ Tokens are single-use (deleted after password reset)
- ✅ Email enumeration protection (always returns success)
- ✅ Password strength validation (minimum 6 characters)
- ✅ Secure password hashing (bcrypt)

## API Usage Examples

### Request Password Reset
```bash
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Response:**
```json
{
  "message": "If an account exists with this email, a password reset link has been sent.",
  "token": "abc123..." // Only in development without email config
}
```

### Verify Reset Token
```bash
curl -X POST http://localhost:5000/api/auth/verify-reset-token \
  -H "Content-Type: application/json" \
  -d '{"token": "abc123..."}'
```

**Response:**
```json
{
  "valid": true,
  "email": "user@example.com"
}
```

### Reset Password
```bash
curl -X POST http://localhost:5000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123...",
    "password": "newpassword123"
  }'
```

**Response:**
```json
{
  "message": "Password has been reset successfully. You can now login with your new password."
}
```

## Production Deployment

### Recommended Changes for Production:

1. **Use a dedicated email service** (SendGrid, AWS SES, Mailgun)
2. **Store tokens in Redis** instead of memory
3. **Add rate limiting** to prevent abuse
4. **Remove token from API response** (only send via email)
5. **Use HTTPS** for frontend URL
6. **Add email verification** for new accounts
7. **Log password reset attempts** for security auditing

### Example Production .env:
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxxxxxxxxxx
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=SmartAttendance
FRONTEND_URL=https://attendance.yourdomain.com
```

## Troubleshooting

### Email not sending?
1. Check SMTP credentials in `.env`
2. Verify 2FA and app password (Gmail)
3. Check firewall/port 587 access
4. Look for error messages in console

### Token invalid/expired?
1. Tokens expire after 1 hour
2. Tokens are single-use
3. Request a new reset link

### Password reset not working?
1. Check backend console for errors
2. Verify user email exists in database
3. Ensure password meets minimum requirements (6 chars)

## Email Template Preview

The reset email includes:
- Professional header with gradient
- Clear call-to-action button
- Fallback text link
- Expiration warning
- Security notice
- Branded footer

## Next Steps

1. **Update your `.env` file** with email credentials
2. **Restart the backend** server
3. **Test the flow** with a real user account
4. **Check spam folder** if email doesn't arrive
5. **Monitor console** for any errors

## Support

For issues or questions:
- Check backend console logs
- Verify email configuration
- Test with console logging first
- Review security best practices

---

**Note:** Always use app-specific passwords for Gmail, never your actual account password!
