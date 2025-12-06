# Email Setup Instructions

To receive feedback emails at anantkapoor320@gmail.com, follow these steps:

## 1. Enable 2-Step Verification
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled

## 2. Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Click "Generate"
4. Copy the 16-character password

## 3. Update .env File
Edit `backend/.env` and add:

```
GMAIL_USER=anantkapoor320@gmail.com
GMAIL_PASSWORD=your_16_character_app_password
```

## 4. Restart Backend
```bash
cd backend
python -m uvicorn main:app --reload
```

Now all feedback will be emailed to anantkapoor320@gmail.com!
