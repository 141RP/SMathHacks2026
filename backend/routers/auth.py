from fastapi import APIRouter, HTTPException, status
from ..schemas.auth import LoginRequest, Token
from ..auth.jwt import create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    # This should verify against DB in real implementation
    # For now, using mock logic
    if request.username == "admin" and request.password == "password":
        access_token = create_access_token(
            data={"sub": "1", "role": "org_admin", "org_id": 1}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    elif request.username == "diver" and request.password == "password":
         access_token = create_access_token(
            data={"sub": "2", "role": "volunteer_diver", "org_id": 1}
        )
         return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )
