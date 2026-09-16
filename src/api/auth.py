
from fastapi import APIRouter, Depends, status, UploadFile,HTTPException
from src.schemas.auth import RegisterRequest,UserResponse,LoginRequest,TokenResponse,RefreshRequest
from src.db.session import get_session
from sqlalchemy.orm import Session
from src.utils.password import get_password_hash, verify_password
from src.db.models import User
# from src.config import Setting
from sqlalchemy import select
from src.utils.jwt import create_access_token,create_refresh_token,verify_token
from src.deps import get_current_user

router = APIRouter(
    # prefix="",
    tags=["auth"]
)


@router.post("/register",response_model=UserResponse)
async def register(reqeust:RegisterRequest,session:Session=Depends(get_session)):
    email = reqeust.email
    password = reqeust.password

    # 检查邮箱是否已存在
    result = await session.execute(
                select(User).where(User.email == email)
            ) # type: ignore
    if result.scalar_one_or_none():
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

 

    # 密码强度校验
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    # 注册用户
    # 创建用户对象
    user = User(
        email=email,
        password_hash = get_password_hash(password)
        )
    print("注册用户--之前", user)
    session.add(user) # 添加用户实例信息到会话
    await session.commit() # type: ignore # 数据库提交 数据持久化
    await session.refresh(user) # type: ignore
    print("注册用户--之前", user)

    # 响应返回
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role
    )

@router.post('/login',response_model=TokenResponse)
async def login(request:LoginRequest,session:Session=Depends(get_session)):
    email=request.email
    password=request.password

    result=await session.execute(select(User).where(User.email==email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="the email is not registered ",
        )
    if not verify_password(password,user.password_hash):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="password error ",
            )
    if not user.is_active:
         raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="the user is not active ",
            )
    access_token=create_access_token({"sub":str(user.id)})
    refresh_token = create_refresh_token(data={"sub":str(user.id)})

    return TokenResponse(
         access_token=access_token,
         refresh_token=refresh_token,
         token_type="bearer" # header 传值开头 形式
     )

@router.post("/refresh",response_model=TokenResponse)
async def refresh(request: RefreshRequest):
    try:
        payload=verify_token(request.refresh_token)
        if payload.get('type') !='refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    except ValueError: # 验证失败
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    uer_id = payload.get("sub")
    access_token = create_access_token(data={"sub":uer_id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,
        token_type="bearer",
    )

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):

    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
    )

