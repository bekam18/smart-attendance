# 🎯 Password Reset - Quick Reference Card

## 🚀 Instant Start (No Email Setup)

```bash
# 1. Start backend
cd backend
python app.py

# 2. Start frontend  
cd frontend
npm run dev

# 3. Test at: http://localhost:5173/login
# Click "Forgot password?" → Enter email → Check console for token
```

## 📧 Gmail Setup (2 Minutes)

```env
# In backend/.env add:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=noreply@smartattendance.com
FROM_NAME=SmartAttendance
FRONTEND_URL=http://localhost:5173
```

**Get App Password:** https://myaccount.google.com/apppasswords

## 🔗 URLs

| Page | URL |
|------|-----|
| Login | `http://localhost:5173/login` |
| Forgot Password | `http://localhost:5173/forgot-password` |
| Reset Password | `http://localhost:5173/reset-password?token=XXX` |

## 🎯 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/forgot-password` | Request reset |
| POST | `/api/auth/verify-reset-token` | Verify token |
| POST | `/api/auth/reset-password` | Reset password |

## 🧪 Test Commands

```bash
# Quick test
test_password_reset.bat

# Manual test
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"admin@smartattendance.com\"}"
```

## 👥 Test Accounts

- `admin@smartattendance.com`
- `instructor@smartattendance.com`
- `student@smartattendance.com`

## ✅ Features

- ✅ Forgot password link on login
- ✅ Email validation
- ✅ Secure token generation
- ✅ 1-hour token expiration
- ✅ Professional HTML email
- ✅ Password confirmation
- ✅ Success/error handling
- ✅ Auto-redirect to login
- ✅ Mobile responsive
- ✅ Console fallback (no email needed)

## 🔒 Security

- 32-byte cryptographic tokens
- 1-hour expiration
- Single-use tokens
- Email enumeration protection
- Password strength validation
- Bcrypt hashing

## 🐛 Quick Fixes

**Email not sending?**
→ Check `.env` credentials, use app password for Gmail

**Token invalid?**
→ Tokens expire in 1 hour, request new one

**Can't find email?**
→ Check spam folder, use console token for testing

**Password too short?**
→ Minimum 6 characters required

## 📁 Files Changed

### Frontend
- `pages/Login.tsx` - Added link
- `pages/ForgotPassword.tsx` - New
- `pages/ResetPassword.tsx` - New
- `lib/api.ts` - Added APIs
- `App.tsx` - Added routes

### Backend
- `blueprints/auth.py` - Added endpoints
- `utils/email_service.py` - New
- `.env.sample` - Added config

## 📚 Documentation

- `PASSWORD_RESET_COMPLETE.md` - Full implementation details
- `PASSWORD_RESET_SETUP.md` - Complete setup guide
- `PASSWORD_RESET_QUICK_START.md` - 5-minute setup
- `PASSWORD_RESET_VISUAL_GUIDE.md` - UI/UX guide
- `PASSWORD_RESET_REFERENCE_CARD.md` - This file

## 🎨 UI Flow

```
Login → Forgot Password → Email Sent → 
Check Email → Reset Password → Success → Login
```

## ⚡ Quick Test Flow

1. Go to login page
2. Click "Forgot password?"
3. Enter: `admin@smartattendance.com`
4. Check console for token (if no email)
5. Visit: `http://localhost:5173/reset-password?token=TOKEN`
6. Enter new password (min 6 chars)
7. Confirm password
8. Click "Reset Password"
9. Login with new password

## 🎊 Status

✅ **FULLY IMPLEMENTED AND READY TO USE!**

No additional setup required - works immediately with console logging. Add email config when ready for production.

---

**Need help?** Check the full documentation files or troubleshooting sections.
