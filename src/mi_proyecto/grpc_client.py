import grpc

from mi_proyecto import orders_pb2, orders_pb2_grpc


def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = orders_pb2_grpc.OrderServiceStub(channel)

    response = stub.CreateOrder(
        orders_pb2.OrderRequest(
            customer="Ana López",
            product="Laptop",
            quantity=2,
            unit_price=12500.5,
        )
    )

    print("Order creada:")
    print(response)


if __name__ == "__main__":
    run()
