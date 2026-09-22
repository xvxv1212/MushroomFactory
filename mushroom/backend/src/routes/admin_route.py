import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sqlmodel import select, func
import logging
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token
from auth.authenticate import authenticate, optional_authenticate
from database.connection import get_session
from model.admin import Admin
from model.llm_role import LlmRole, WriteLlmRole

router = APIRouter(prefix="/admins", tags=["Admins"])

template = Jinja2Templates("templates/")

password_encoder = HashPassword()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    )
    logger.addHandler(console_handler)
logger.propagate = False

@router.get("/")
async def admin_index(
    request: Request,
    current_user: str | None = Depends(optional_authenticate),
):
    return template.TemplateResponse(
        request,
        "admin/admin_index.html",
        {"is_authenticated": current_user is not None},
    )

@router.get("/signup")
async def admin_join_form(request : Request):
    return template.TemplateResponse(request, "admin/admin_joinform.html")

@router.post("/signup")
async def signup(
    admin_id: str = Form(...),
    admin_pw: str = Form(...),
    teacher_num: int = Form(...),
    admin_name : str = Form(...),
    contact: str = Form(...),
    session = Depends(get_session)
):
    admin_exist = session.get(Admin, admin_id)
    if admin_exist:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail = "User with supplied username exists."
        )
    admin = Admin(
        admin_id=admin_id,
        teacher_num=teacher_num,
        admin_name=admin_name,
        contact=contact,
        admin_pw=password_encoder.create_hash(admin_pw),
    )

    session.add(admin)
    session.commit()
    session.refresh(admin)

    return RedirectResponse("/admins/", status_code = 303)

@router.get("/signin")
async def user_signin(request : Request):
    return template.TemplateResponse(request, "admin/login_form.html")

@router.post("/signin")
async def sign_user_in(
                       user: OAuth2PasswordRequestForm = Depends(),
                       session =  Depends(get_session)
                       ) -> dict:
    admin_exist = session.get(Admin, user.username)
    if not admin_exist:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Invalid username or password"
        )

    if not password_encoder.verify_hash(user.password, admin_exist.admin_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid details passed",
        )

    if admin_exist.enabled == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile update required before sign in",
            headers={"X-Account-Status": "PROFILE_UPDATE_REQUIRED"},
        )

    access_token = create_access_token(admin_exist.admin_id)
    response = RedirectResponse("/admins/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
    )
    return response
    
@router.get("/signout")
async def signout():
    response = RedirectResponse("/admins/", status_code=303)
    response.delete_cookie("access_token")
    return response

@router.get("/update")
async def update_admin(
    request: Request,
    current_user: str = Depends(authenticate),
    session = Depends(get_session),
):
    admin_exist = session.get(Admin, current_user)
    if not admin_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin account not found",
        )
    return template.TemplateResponse(request, "admin/update_form.html", {"admin" : admin_exist})

@router.post("/update")
async def update_admin(
        admin_pw: str | None = Form(None),
        contact: str | None = Form(None),
        current_user: str = Depends(authenticate),
        session = Depends(get_session)
):
    admin = session.get(Admin, current_user)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin account not found",
        )

    updated_fields: list[str] = []

    if admin_pw is not None and admin_pw.strip():
        admin.admin_pw = password_encoder.create_hash(admin_pw.strip())
        updated_fields.append("admin_pw")

    if contact is not None and contact.strip():
        admin.contact = contact.strip()
        updated_fields.append("contact")

    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    admin.enabled = 1
    session.add(admin)
    session.commit()
    print(f"[ADMIN UPDATE SUCCESS] admin_id={admin.admin_id}, fields={updated_fields}")

    return RedirectResponse("/admins/", status_code=303)

@router.post("/resign")
async def resign(
    current_user: str = Depends(authenticate),
    session = Depends(get_session),
):
    admin = session.get(Admin, current_user)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin account not found",
        )

    admin.enabled = 0
    session.add(admin)
    session.commit()
    print(f"[ADMIN RESIGN SUCCESS] admin_id={admin.admin_id}, enabled=0")

    response = RedirectResponse("/admins/", status_code=303)
    response.delete_cookie("access_token")
    return response

# 여기부터 LLM_ROLE에 추가를 하는 로직임
# 사실상 게시판에 글을 올리는 로직과도 같음
# LLM_ROLE은 ADMIN_TABLE을 참조
@router.get("/writeform")
async def write_form(
        request : Request,
        current_user: str = Depends(authenticate),
        session = Depends(get_session),
):
    if not session.get(Admin, current_user).enabled:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail="Profile update required before sign in",
            headers={"X-Account-Status": "PROFILE_UPDATE_REQUIRED"},
        )
    return template.TemplateResponse(request, "/llm_role/write_form.html")

@router.post("/write")
async def write(
    category: str = Form(...),
    content: str = Form(...),
    title : str = Form(...),
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    if not category.strip() or not content.strip() or not title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category and content are required",
        )

    llm_role = LlmRole(
        category=category.strip(),
        title=title.strip(),
        content=content.strip(),
        admin_id=current_user,
    )

    session.add(llm_role)
    session.commit()
    session.refresh(llm_role)

    print(
        f"[LLM ROLE CREATED] "
        f"lr_num={llm_role.lr_num}, admin_id={llm_role.admin_id}"
    )

    return RedirectResponse("/admins/llmRoleList", status_code=303)


@router.get("/llmRoleList")
async def llm_role_list(
        request : Request,
        session = Depends(get_session),
        current_user: str = Depends(authenticate)
):
    if not session.get(Admin, current_user).enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profile update required before sign in",
            headers={"X-Account-Status": "PROFILE_UPDATE_REQUIRED"},
        )

    # 전체보기는 select
    statement = select(LlmRole)
    llm_roles = session.exec(statement).all()

    return template.TemplateResponse(request, "/llm_role/llm_roles.html", {"llm_roles" : llm_roles})

@router.get("/llmRole/{lr_num}")
async def select_one_llm_role(
        request: Request,
        lr_num : int,
        current_user: str | None = Depends(optional_authenticate),
        session = Depends(get_session),
):
    llm_role = session.get(LlmRole, lr_num)
    if not llm_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM role not found",
        )

    return template.TemplateResponse(
        request,
        "llm_role/selectOneLlmRole.html",
        {
                "is_owner": current_user is not None and current_user == llm_role.admin_id,
                "llm_role": llm_role,
        } )
@router.get("/updateLlmRole/{lr_num}")
async def update_llm_role(
        request : Request,
        lr_num : int,
        session = Depends(get_session),
):
    llm_role = session.get(LlmRole, lr_num)

    return template.TemplateResponse(
        request,
        "/llm_role/updateLRForm.html",
        {"llm_role" : llm_role}
    )

@router.post("/updateLlmRole/{lr_num}")
async def update_llm_role(
    lr_num: int,
    category: str = Form(...),
    content: str = Form(...),
    title: str = Form(...),
    current_user: str = Depends(authenticate),
    session=Depends(get_session),
):
    # 한 번 조회한 객체
    llm_role = session.get(LlmRole, lr_num)

    if not llm_role:
        raise HTTPException(
            status_code=404,
            detail="LLM role not found",
        )

    if llm_role.admin_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="Only the author can update this role",
        )

    llm_role.category = category.strip()
    llm_role.title = title.strip()
    llm_role.content = content.strip()

    # update
    session.add(llm_role)
    session.commit()
    session.refresh(llm_role)

    return RedirectResponse(
        f"/admins/llmRole/{lr_num}",
        status_code=303,
    )

# 삭제 로직
@router.get("/deleteLlmRole/{lr_num}")
async def my_llm_roles(
    lr_num : int,
    current_user: str = Depends(authenticate),
    session = Depends(get_session)
):
    llm_role = session.get(LlmRole, lr_num)

    if not llm_role:
        raise HTTPException(
            status_code=404,
            detail="LLM role not found",
        )

    if llm_role.admin_id != current_user:
        raise HTTPException(
            status_code=403,
            detail="Only the author can update this role",
        )

    session.delete(llm_role)
    session.commit()

    return RedirectResponse(
        "/admins/llmRoleList",
        status_code=303,
    )

# 자기가 작성한 것만 조회 -> 마이페이지 격인 곳
@router.get("/myRoles")
async def myRoles(
    request : Request,
    session = Depends(get_session),
    current_user = Depends(authenticate)
):

    total_count = session.exec(
        select(func.count(LlmRole.admin_id)).where(LlmRole.admin_id == current_user)
    ).one()

    statement = (
        select(LlmRole.lr_num, LlmRole.title, LlmRole.created_at)
        .join(Admin, Admin.admin_id == LlmRole.admin_id)
        .where(Admin.admin_id == current_user)
    )
    llm_roles = session.exec(statement).all()

    response = template.TemplateResponse(
        request,
        "/admin/myRoles.html",
        {"llm_roles" : llm_roles , "total_count" : total_count, "admin_id" : current_user}
    )
    return response
