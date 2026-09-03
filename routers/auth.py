from fastapi import APIRouter

router = APIRouter(prefix='/auth',tags=['auth'])


@router.post('/register')
def create_user():
    pass

@router.post('/login')
def login_user():
    pass

@router.get('/logout')
def logout_user():
    pass
