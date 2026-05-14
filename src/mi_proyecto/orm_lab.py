from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column,
                            relationship)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product: Mapped[str]
    quantity: Mapped[int]
    unit_price: Mapped[float]

    order: Mapped["Order"] = relationship(back_populates="items")

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


def crear_base_de_datos():
    engine = create_engine("sqlite+pysqlite:///orm_lab.db", echo=False)
    Base.metadata.create_all(engine)
    return engine


def crear_usuario(session: Session, name: str, email: str) -> User:
    user = User(name=name, email=email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def crear_orden(session: Session, user: User) -> Order:
    order = Order(user=user)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def agregar_item(
    session: Session,
    order: Order,
    product: str,
    quantity: int,
    unit_price: float,
) -> OrderItem:
    item = OrderItem(
        order=order,
        product=product,
        quantity=quantity,
        unit_price=unit_price,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def listar_usuarios(session: Session) -> list[User]:
    query = select(User)
    return list(session.scalars(query))


def calcular_total_orden(order: Order) -> float:
    return sum(item.subtotal for item in order.items)


def actualizar_email(session: Session, user: User, nuevo_email: str) -> None:
    user.email = nuevo_email
    session.commit()


def eliminar_usuario(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()


def main() -> None:
    engine = crear_base_de_datos()

    with Session(engine) as session:
        user = crear_usuario(session, "Ana López", "ana@example.com")
        order = crear_orden(session, user)

        agregar_item(session, order, "Laptop", 1, 12500.50)
        agregar_item(session, order, "Mouse", 2, 350.00)

        usuarios = listar_usuarios(session)

        print("Usuarios registrados:")
        for usuario in usuarios:
            print(f"{usuario.id} - {usuario.name} - {usuario.email}")

        print("\nÓrdenes del usuario:")
        for orden in user.orders:
            total = calcular_total_orden(orden)
            print(f"Orden #{orden.id} | Total: ${total:.2f}")

            for item in orden.items:
                print(
                    f"- {item.product} | Cantidad: {item.quantity} | "
                    f"Subtotal: ${item.subtotal:.2f}"
                )

        actualizar_email(session, user, "ana.lopez@example.com")
        print(f"\nEmail actualizado: {user.email}")

        eliminar_usuario(session, user)
        print("\nUsuario eliminado correctamente")


if __name__ == "__main__":
    main()
