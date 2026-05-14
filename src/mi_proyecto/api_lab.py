from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy import Float, Integer, String, create_engine, select
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column,
                            sessionmaker)

from mi_proyecto.settings import settings

SECRET_KEY = settings.secret_key
DATABASE_URL = settings.database_url
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

app = FastAPI(
    title="Orders API Lab",
    version="1.0.0",
    description="API para gestión de órdenes con JWT, validación y CRUD.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer: Mapped[str] = mapped_column(String, index=True)
    product: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)


class OrderCreate(BaseModel):
    customer: str = Field(min_length=2)
    product: str = Field(min_length=2)
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class OrderUpdate(BaseModel):
    customer: str = Field(min_length=2)
    product: str = Field(min_length=2)
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class OrderPatch(BaseModel):
    customer: str | None = Field(default=None, min_length=2)
    product: str | None = Field(default=None, min_length=2)
    quantity: int | None = Field(default=None, gt=0)
    unit_price: float | None = Field(default=None, gt=0)


class OrderOut(BaseModel):
    id: int
    customer: str
    product: str
    quantity: int
    unit_price: float
    total: float


class Token(BaseModel):
    access_token: str
    token_type: str


class ErrorResponse(BaseModel):
    errorCode: str
    errorMessage: str
    userError: str
    info: str = ""


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username: str, password: str) -> bool:
    return username == "admin" and password == "1234"


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "errorCode": "AUTH_001",
                    "errorMessage": "Token sin usuario válido",
                    "userError": "No tienes autorización para ejecutar esta operación.",
                    "info": "",
                },
            )

        return username

    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "errorCode": "AUTH_002",
                "errorMessage": "Token inválido o expirado",
                "userError": "Tu sesión no es válida. Inicia sesión nuevamente.",
                "info": "",
            },
        ) from exc


def to_order_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        customer=order.customer,
        product=order.product,
        quantity=order.quantity,
        unit_price=order.unit_price,
        total=order.quantity * order.unit_price,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "errorCode": f"HTTP_{exc.status_code}",
            "errorMessage": str(exc.detail),
            "userError": "No fue posible procesar la solicitud.",
            "info": "",
        },
    )


@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.post(
    "/api/v1/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "errorCode": "AUTH_003",
                "errorMessage": "Credenciales incorrectas",
                "userError": "Usuario o contraseña incorrectos.",
                "info": "",
            },
        )

    token = create_access_token({"sub": form_data.username})
    return Token(access_token=token, token_type="bearer")


@app.post(
    "/api/v1/orders",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    order: OrderCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
) -> OrderOut:
    db_order = Order(**order.model_dump())

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return to_order_out(db_order)


@app.get(
    "/api/v1/orders",
    response_model=list[OrderOut],
    status_code=status.HTTP_200_OK,
)
async def list_orders(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
    limit: int = 25,
    offset: int = 0,
) -> list[OrderOut]:
    query = select(Order).offset(offset).limit(limit)
    orders = db.scalars(query).all()

    return [to_order_out(order) for order in orders]


@app.get(
    "/api/v1/orders/{order_id}",
    response_model=OrderOut,
    status_code=status.HTTP_200_OK,
)
async def get_order(
    order_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
) -> OrderOut:
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "errorCode": "ORD_404",
                "errorMessage": f"Order {order_id} not found",
                "userError": "La orden solicitada no existe.",
                "info": "",
            },
        )

    return to_order_out(order)


@app.put(
    "/api/v1/orders/{order_id}",
    response_model=OrderOut,
    status_code=status.HTTP_200_OK,
)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
) -> OrderOut:
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "errorCode": "ORD_404",
                "errorMessage": f"Order {order_id} not found",
                "userError": "La orden solicitada no existe.",
                "info": "",
            },
        )

    order.customer = order_data.customer
    order.product = order_data.product
    order.quantity = order_data.quantity
    order.unit_price = order_data.unit_price

    db.commit()
    db.refresh(order)

    return to_order_out(order)


@app.patch(
    "/api/v1/orders/{order_id}",
    response_model=OrderOut,
    status_code=status.HTTP_200_OK,
)
async def patch_order(
    order_id: int,
    order_data: OrderPatch,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
) -> OrderOut:
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "errorCode": "ORD_404",
                "errorMessage": f"Order {order_id} not found",
                "userError": "La orden solicitada no existe.",
                "info": "",
            },
        )

    update_data = order_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)

    return to_order_out(order)


@app.delete(
    "/api/v1/orders/{order_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_order(
    order_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[str, Depends(get_current_user)],
) -> dict[str, str]:
    order = db.get(Order, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "errorCode": "ORD_404",
                "errorMessage": f"Order {order_id} not found",
                "userError": "La orden solicitada no existe.",
                "info": "",
            },
        )

    db.delete(order)
    db.commit()

    return {"message": "Orden eliminada correctamente"}
