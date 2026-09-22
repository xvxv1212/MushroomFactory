# 패스워드를 암호화하느 함수가 포함된 모듈
# 이 모듈의 함수가 계정을 등록할 때 또는 로그인 시에 패스워드를 비교할 때 사용
from passlib.context import CryptContext

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

class HashPassword:
    # 비밀번호를 해싱한 값을 반환하는 함수
    def create_hash(self, password : str) :
        return pwd_context.hash(password)

    # 비밀번호를 검증하는 함수
    def verify_hash(self, plain_password : str, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)