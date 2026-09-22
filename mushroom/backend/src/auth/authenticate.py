# authenticate.py
# authenticate 의존 라이브러리가 포함되며 인증 및 권한을 위해 라우트에 주입된다.

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_handler import verify_acess_token

#
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admins/signin", auto_error=False)

#
async def authenticate(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
) -> str:
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Sign in for access"
        )

    decoded_token = verify_acess_token(token.removeprefix("Bearer ").strip())
    return decoded_token["user"]


async def optional_authenticate(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
) -> str | None:
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        decoded_token = verify_acess_token(token.removeprefix("Bearer ").strip())
        return decoded_token["user"]
    except HTTPException:
        return None
