import grpc
import time
from concurrent import futures

from . import discover_pb2
from . import discover_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Discover(discover_pb2_grpc.DiscoverServicer):

  def SayHello(self, request, context):
    return discover_pb2.HelloReply(message='Hello, %s!' % request.name)


def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  discover_pb2_grpc.add_DiscoverServicer_to_server(Discover(), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  print("Server started. Listening on port 50051.")
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)


if __name__ == '__main__':
  serve()
