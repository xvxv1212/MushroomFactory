# jwt_handler.py
# JWT 문자열을 인코딩,디코딩 하는 함수가 포함된다.

# 사용 라이브러리
from jose import jwt, JWTError
from fastapi import HTTPException, status
import time
from datetime import datetime

# 모듈의 클래스 임포트
from database.connection import Settings

settings = Settings()

def create_access_token(user : str):
    payload = {
        "user" : user,
        "expires" : time.time() + 3600 # 현재 시간 기준 만료시간을 1시간으로 설정
    }

    # 토큰
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm = "HS256")
    return token

# 토큰 검증하는 함수
def verify_acess_token(token : str):
    try :
        data = jwt.decode(token, settings.SECRET_KEY, algorithms = ["HS256"])
        expire = data.get("expires")

        if expire is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail = "No access token supplied"
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail = "Token expired"
            )
        return data
    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid token"
        )
