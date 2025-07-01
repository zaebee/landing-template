import unittest
import grpc
from concurrent import futures
import time

import greeter_pb2
import greeter_pb2_grpc
from main import Greeter  # Import the Greeter servicer from main.py

_TEST_PORT = 50052  # Use a different port for testing


class TestGreeterService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Start a test server
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        greeter_pb2_grpc.add_GreeterServicer_to_server(Greeter(), cls.server)
        cls.server.add_insecure_port(f'[::]:{_TEST_PORT}')
        cls.server.start()
        # Give the server a moment to start
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.stop(0)

    def test_say_hello(self):
        # Create a channel to the server
        with grpc.insecure_channel(f'localhost:{_TEST_PORT}') as channel:
            stub = greeter_pb2_grpc.GreeterStub(channel)
            name = "TestUser"
            request = greeter_pb2.HelloRequest(name=name)
            response = stub.SayHello(request)
            self.assertEqual(response.message, f"Hello, {name}!")

    def test_say_hello_empty_name(self):
        # Create a channel to the server
        with grpc.insecure_channel(f'localhost:{_TEST_PORT}') as channel:
            stub = greeter_pb2_grpc.GreeterStub(channel)
            name = ""
            request = greeter_pb2.HelloRequest(name=name)
            response = stub.SayHello(request)
            self.assertEqual(response.message, f"Hello, {name}!")

    def test_say_hello_special_chars(self):
        # Create a channel to the server
        with grpc.insecure_channel(f'localhost:{_TEST_PORT}') as channel:
            stub = greeter_pb2_grpc.GreeterStub(channel)
            name = "!@#$%^&*()"
            request = greeter_pb2.HelloRequest(name=name)
            response = stub.SayHello(request)
            self.assertEqual(response.message, f"Hello, {name}!")


if __name__ == '__main__':
    unittest.main()
