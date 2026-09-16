from fastapi import  Depends, status, HTTPException

from src.db.session import get_session
from sqlalchemy.orm import Session
from src.db.models import User

from sqlalchemy import select
from src.utils.jwt import  verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession


# 验证用户是否登录
# 获取当前用户: 获取用户传递token ,验证token ,获取用户信息
async def get_current_user(
    authoriation: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    session: Session = Depends(get_session),
):

    # 获取token &
    access_token = authoriation.credentials

    # 验证token
    try:
        payload = verify_token(access_token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
    except ValueError:  # 验证失败
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    # 获取用户id
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # 查询数据库中查询用户
    result = await session.execute(select(User).where(User.id == user_id))

    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if user.is_active == False:  # 账号被禁用
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
        )

    return user

async def get_admin_user(
        current_user:User=Depends(get_current_user)):
    if current_user.role !='admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    return current_user