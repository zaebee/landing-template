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

If you modify the `discover_service/proto/discover.proto` file, you will need to regenerate the Python gRPC code. Use the following command from the project root directory:

```bash
python -m grpc_tools.protoc -I. --python_out=discover_service --grpc_python_out=discover_service discover_service/proto/discover.proto
```
This will generate `discover_service/discover_pb2.py` and `discover_service/discover_pb2_grpc.py`.

**Important:** After generating the code, you will need to manually update the import statement in `discover_service/discover_pb2_grpc.py`.
Change:
`import discover_pb2 as discover__pb2` (or similar, depending on how protoc structures it based on the new paths)
To:
`from . import discover_pb2 as discover__pb2`
