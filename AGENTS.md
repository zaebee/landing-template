## Running the gRPC Server

To run the gRPC server, execute the following command in your terminal:

```bash
python main.py
```

The server will start and listen on port 50051.

## Running Tests

To run the tests for the gRPC server, execute the following command in your terminal:

```bash
python -m unittest test_main.py
```

This will run all the test cases defined in `test_main.py`.

## Dependencies

Make sure you have the necessary dependencies installed. You can install them using pip:

```bash
pip install -r requirements.txt
```

## Generating Protobuf Code

If you modify the `proto/discover.proto` file, you will need to regenerate the Python gRPC code. Use the following command from the project root directory:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/discover.proto
```
This will generate `discover_pb2.py` and `discover_pb2_grpc.py` in the project root.

**Important:** After generating the code, you might need to manually update the import statement in `discover_pb2_grpc.py`.
Change:
`from proto import discover_pb2 as proto_dot_discover__pb2`
To:
`import discover_pb2 as proto_dot_discover__pb2`
