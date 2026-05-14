from sqlalchemy import Float, ForeignKey, String, create_engine, select
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column,
                            relationship)

from mi_proyecto.hexagonal.domain.order import Order, OrderItem


class Base(DeclarativeBase):
    pass


class OrderModel(Base):
    __tablename__ = "hex_orders"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer: Mapped[str] = mapped_column(String)

    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItemModel(Base):
    __tablename__ = "hex_order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("hex_orders.id"))
    product: Mapped[str] = mapped_column(String)
    quantity: Mapped[int]
    unit_price: Mapped[float] = mapped_column(Float)

    order: Mapped["OrderModel"] = relationship(back_populates="items")


class SQLAlchemyOrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, order: Order) -> None:
        model = OrderModel(
            id=order.id,
            customer=order.customer,
            items=[
                OrderItemModel(
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in order.items
            ],
        )

        self.session.add(model)
        self.session.commit()

    def get_by_id(self, order_id: str) -> Order | None:
        result = self.session.scalars(
            select(OrderModel).where(OrderModel.id == order_id)
        ).first()

        if result is None:
            return None

        return Order(
            id=result.id,
            customer=result.customer,
            items=[
                OrderItem(
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in result.items
            ],
        )


def create_sqlite_memory_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)
