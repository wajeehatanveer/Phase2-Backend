from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, validator
from ..auth.jwt_handler import create_access_token
from datetime import timedelta
from sqlmodel import Session, select
from ..db import engine
from ..models.user import User
from passlib.context import CryptContext
import logging


logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    user_id: str


class SignupRequest(BaseModel):
    email: str
    password: str

    @validator('email')
    def validate_email(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError('email must be a string')
        v = v.strip().lower()
        # lightweight validation to avoid optional email-validator dependency
        if '@' not in v or v.startswith('@') or v.endswith('@'):
            raise ValueError('Invalid email address')
        return v


class SignupResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    message: str


router = APIRouter(prefix="/auth", tags=["auth"])


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login")
def login(request: LoginRequest):
    """Simple development login that returns a signed JWT for the provided user_id."""
    # In production, replace this with real authentication against Better Auth
    if not request.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    token = create_access_token(data={"user_id": request.user_id, "sub": request.user_id}, expires_delta=timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer", "user_id": request.user_id}


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest):
    """Create a new user with hashed password and return a JWT token."""
    try:
        with Session(engine) as session:
            # Normalize email
            email = request.email.strip().lower()

            # Check if user already exists
            existing = session.exec(select(User).where(User.email == email)).first()
            if existing:
                raise HTTPException(status_code=400, detail="User with this email already exists")

            # Hash the password
            hashed = pwd_context.hash(request.password)

            # Create user record
            user = User(email=email, hashed_password=hashed)
            session.add(user)
            session.commit()
            session.refresh(user)

            # Create JWT token using same logic as /auth/login
            token = create_access_token(data={"user_id": user.email, "sub": user.email}, expires_delta=timedelta(minutes=60))

            return SignupResponse(
                access_token=token,
                token_type="bearer",
                user_id=user.email,
                message="User created successfully"
            )
    except HTTPException:
        # Re-raise HTTPExceptions so FastAPI handles them
        raise
    except Exception as e:
        logger.exception("Error creating user: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error while creating user")