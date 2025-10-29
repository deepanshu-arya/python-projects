# =============================================================
# ✅ Secure Authentication API - Developed by Deepanshu
# =============================================================

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict


# =============================================================
# ▶️ Application Metadata
# =============================================================
app = FastAPI(
    title="SecureAuth Login API",
    description="A simple authentication system for user signup, login, and profile access using FastAPI.",
    version="1.0.0"
)


# =============================================================
# ▶️ Temporary User Storage (Storage will be upgraded later)
# =============================================================
local_user_store: Dict[str, str] = {}  # key=username, value=password


# =============================================================
# ▶️ Request Body Model
# =============================================================
class User(BaseModel):
    username: str
    password: str


# =============================================================
# ▶️ Root Endpoint - Server Status Check
# =============================================================
@app.get("/", status_code=status.HTTP_200_OK)
def root_status():
    """
    Returns a confirmation message indicating API is running properly.
    """
    return {
        "status": "success",
        "message": "SecureAuth API is running correctly"
    }


# =============================================================
# ▶️ User Registration Endpoint
# =============================================================
@app.post("/user-signup", status_code=status.HTTP_201_CREATED)
def user_signup(user: User):
    """
    Registers a new user into the system.
    Returns an error if the username already exists.
    """
    if user.username in local_user_store:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered. Please try a different username."
        )

    # Storing plain text password temporarily (will improve in future updates)
    local_user_store[user.username] = user.password

    return {
        "status": "success",
        "message": "User registered successfully"
    }


# =============================================================
# ▶️ User Login Endpoint
# =============================================================
@app.post("/authenticate", status_code=status.HTTP_200_OK)
def authenticate(user: User):
    """
    Authenticates the user based on the provided credentials.
    Validates both username and password.
    """
    if user.username not in local_user_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first."
        )

    if local_user_store[user.username] != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password does not match our verified records"
        )

    return {
        "status": "success",
        "message": f"Login successful for user: {user.username}"
    }


# =============================================================
# ▶️ User Profile Endpoint
# =============================================================
@app.get("/account-detail/{username}", status_code=status.HTTP_200_OK)
def account_detail(username: str):
    """
    Returns user profile information after validation.
    """
    if username not in local_user_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist in the system"
        )

    return {
        "status": "success",
        "username": username,
        "profile": "Authorized access to secure profile data"
    }
