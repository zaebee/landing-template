import unittest
import grpc
from concurrent import futures
import time

import discover_pb2
import discover_pb2_grpc
from main import Discover  # Import the Discover servicer from main.py

_TEST_PORT = 50052  # Use a different port for testing


class TestDiscoverService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Start a test server
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        discover_pb2_grpc.add_DiscoverServicer_to_server(Discover(), cls.server)
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
            stub = discover_pb2_grpc.DiscoverStub(channel)
            name = "TestUser"
            request = discover_pb2.HelloRequest(name=name)
            response = stub.SayHello(request)
            self.assertEqual(response.message, f"Hello, {name}!")

    def test_say_hello_empty_name(self):
        # Create a channel to the server
        with grpc.insecure_channel(f'localhost:{_TEST_PORT}') as channel:
            stub = discover_pb2_grpc.DiscoverStub(channel)
            name = ""
            request = discover_pb2.HelloRequest(name=name)
            response = stub.SayHello(request)
            self.assertEqual(response.message, f"Hello, {name}!")

    def test_say_hello_special_chars(self):
        # Create a channel to the server
        with grpc.insecure_channel(f'localhost:{_TEST_PORT}') as channel:
            stub = discover_pb2_grpc.DiscoverStub(channel)
            name = "!@#$%^&*()"
            request = discover_pb2.HelloRequest(name=name)
            response = stub.SayHello(request)
            self.assertEqual(response.message, f"Hello, {name}!")


if __name__ == '__main__':
    unittest.main()
