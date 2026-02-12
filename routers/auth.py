from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
from core.security import create_access_token, verify_password, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from services.user_service import get_member
from database import get_db_connection

router = APIRouter(prefix="/auth", tags=["authentication"])

# Token Helper
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str
    name: str # Real Name

@router.post("/register")
def register(user: UserCreate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # Check existing
        cursor.execute("SELECT * FROM members WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = get_password_hash(user.password)
        
        # Insert
        sql = "INSERT INTO members (username, password_hash, name, role, gold) VALUES (%s, %s, %s, 'USER', 0)"
        cursor.execute(sql, (user.username, hashed_password, user.name))
        conn.commit()
        
        return {"msg": "User created successfully"}
    finally:
        conn.close()

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm has username, password
    member = get_member(form_data.username)
    if not member or not member['password_hash']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(form_data.password, member['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": member['username'], "role": member.get('role', 'USER')},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, "token_type": "bearer",
        "username": member['username'], "name": member['name'],
        "role": member.get('role', 'USER')
    }

# ─── 의존성 함수 ───

def get_current_user(token: str = Depends(oauth2_scheme)):
    """로그인된 사용자 정보를 반환합니다."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = get_member(username)
    if user is None:
        raise credentials_exception
    return user

def get_admin_user(user = Depends(get_current_user)):
    """관리자 권한이 있는 사용자만 허용합니다."""
    if user.get('role') != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    return user

