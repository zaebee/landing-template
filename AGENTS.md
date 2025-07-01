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

If you modify the `greeter.proto` file, you will need to regenerate the Python gRPC code. Use the following command:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. greeter.proto
```
