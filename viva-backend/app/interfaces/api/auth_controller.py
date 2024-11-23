import os
from fastapi import APIRouter, Depends, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from pydantic import BaseModel
from infrastructure.repositories.user_repository import UserRepository
from domain.entities.entities import User as UserEntity
from interfaces.service.jwt_service import generate_jwt


router = APIRouter()

# 替换为您的 Google Client ID
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class GoogleLoginRequest(BaseModel):
    token: str

class User(BaseModel):
    id: str
    email: str
    name: str
    picture: str

@router.post("/auth/google-login")
async def google_login(
    request: GoogleLoginRequest,
    user_repo: UserRepository = Depends(UserRepository)
):
    try:
        idinfo = id_token.verify_oauth2_token(request.token, google_requests.Request(), GOOGLE_CLIENT_ID)
        google_id = idinfo['sub']
        email = idinfo.get('email')
        name = idinfo.get('name')
        picture = idinfo.get('picture')

        # 检查用户是否存在
        user = user_repo.get_user_by_google_id(google_id)

        if user:
            # 更新现有用户信息
            user = user_repo.update_user(
                google_id,
                email=email,
                username=name,
                profile_picture=picture
            )
        else:
            # 创建新用户
            user = user_repo.create_user(
                google_id=google_id,
                email=email,
                username=name,
                profile_picture=picture
            )

        # 创建用户对象用于生成 JWT
        user_entity = User(
            id=user['google_id'],
            email=user['email'],
            name=user['username'],
            picture=user['profile_picture']
        )
        
        # 生成 JWT
        token = generate_jwt(user_entity.dict())

        return {
            'message': '登录成功',
            'token': token,
            'user': user_entity.dict()
        }
    except ValueError as e:
        print('Google token 验证失败或用户操作失败', e)
        raise HTTPException(status_code=400, detail="Invalid Google token or user operation failed")
    except Exception as e:
        print('登录过程中发生错误', e)
        raise HTTPException(status_code=500, detail="Internal server error during login process")