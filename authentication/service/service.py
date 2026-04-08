from fastapi import Header, HTTPException
import os
import smtplib
import base64
import json
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from database.database import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from authentication.model.model import User
from fastapi import Depends
import firebase_admin
from firebase_admin import auth, credentials
from dotenv import load_dotenv
load_dotenv()

security = HTTPBearer()

# service_account_path = "../../living-the-adventure-firebase-adminsdk-fbsvc-1eb54110fb.json"

# if not firebase_admin._apps:
#     cred = credentials.Certificate(service_account_path)
#     firebase_admin.initialize_app(cred)

if not firebase_admin._apps:
    firebase_base64 = os.getenv("FIREBASE_CREDENTIALS_BASE64")

    if not firebase_base64:
        raise ValueError("FIREBASE_CREDENTIALS_BASE64 not set")

    # Decode Base64 → JSON string
    decoded_json = base64.b64decode(firebase_base64).decode("utf-8")

    # Convert string → dict
    firebase_config = json.loads(decoded_json)

    cred = credentials.Certificate(firebase_config)

    firebase_admin.initialize_app(cred)

def firebase_auth_dep(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

def get_current_user(
    decoded=Depends(firebase_auth_dep),
    db: Session = Depends(get_db),
):

    phone = decoded.get("phone_number")

    if not phone:
        raise HTTPException(status_code=400, detail="Phone number not found in token")

    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def _send_otp_email(to_email: str, otp: str):
    """Send OTP via SMTP. Configure via env vars."""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    from_email = os.getenv("SMTP_FROM", smtp_user)

    if not smtp_user or not smtp_pass:
        # Dev mode: just print the OTP
        print(f"[DEV] OTP for {to_email}: {otp}")
        return

    msg = MIMEText(
        f"Your LivingTheAdventure email verification code is:\n\n"
        f"  {otp}\n\n"
        f"This code expires in 10 minutes. Do not share it.",
        "plain"
    )
    msg["Subject"] = "Your Email Verification Code"
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, to_email, msg.as_string())
