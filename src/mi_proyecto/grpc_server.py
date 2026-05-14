import json
import uuid
from concurrent import futures

import grpc
import redis

from mi_proyecto import orders_pb2, orders_pb2_grpc

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


class OrderService(orders_pb2_grpc.OrderServiceServicer):
    def CreateOrder(self, request, context):
        order_id = str(uuid.uuid4())
        total = request.quantity * request.unit_price

        event = {
            "event": "OrderCreated",
            "order_id": order_id,
            "customer": request.customer,
            "total": total,
        }

        r.publish("orders", json.dumps(event))

        return orders_pb2.OrderResponse(
            id=order_id,
            total=total,
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)

    server.add_insecure_port("[::]:50051")
    server.start()

    print("gRPC server running on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
