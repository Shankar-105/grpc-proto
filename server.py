"""
server.py — The gRPC Server for our Greeting Service
=====================================================

This script does 3 things:
  1. Implements the actual business logic for the Greeter service (the SayHello method).
  2. Registers that implementation with a gRPC server.
  3. Starts the server and listens on a port for incoming RPC calls.

Analogy: Think of this as setting up a restaurant kitchen.
  - The "servicer" class is the chef who knows HOW to cook each dish (implement each RPC).
  - The "server" is the restaurant building itself — it has an address, opens its doors, and
    routes customer orders (requests) to the kitchen (servicer).
"""

# ──────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────

# 'grpc' — The core gRPC library for Python. Provides the server infrastructure.
import grpc

# 'futures' — Part of Python's standard library (concurrent.futures).
# gRPC's Python server uses a ThreadPoolExecutor to handle multiple requests concurrently.
# Each incoming RPC call is handled by a thread from this pool.
from concurrent import futures

# 'sys' and 'os' — We use these to add the 'generated' folder to Python's import path,
# because the generated code (greeting_pb2_grpc.py) imports greeting_pb2 directly
# (not as 'generated.greeting_pb2'). So Python needs to know where to find it.
import sys
import os

# Add the 'generated' directory to sys.path so Python can find greeting_pb2
# when greeting_pb2_grpc.py does `import greeting_pb2`.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

# 'greeting_pb2' — The generated file containing our message classes:
#   - HelloRequest  (what the client sends)
#   - HelloReply    (what the server responds with)
# These are like Python dataclasses but with protobuf superpowers (binary serialization).
from generated import greeting_pb2

# 'greeting_pb2_grpc' — The generated file containing:
#   - GreeterServicer: A base class we inherit from to implement our service logic.
#   - add_GreeterServicer_to_server(): A function to register our implementation with the server.
#   - GreeterStub: (Used on the client side, not here.)
from generated import greeting_pb2_grpc

# 'grpc_reflection' — This enables gRPC Server Reflection, which lets tools like
# Postman or grpcurl discover what services and methods your server offers WITHOUT
# needing the .proto file. Think of it like Swagger/OpenAPI docs, but for gRPC.
from grpc_reflection.v1alpha import reflection

# ──────────────────────────────────────────────────────
# SERVICE IMPLEMENTATION
# ──────────────────────────────────────────────────────

class GreeterServicer(greeting_pb2_grpc.GreeterServicer):
    """
    This is where the magic happens — YOUR business logic.
    We inherit from the auto-generated 'GreeterServicer' base class.
    The base class has stub methods that raise 'NotImplementedError' by default.
    Our job is to OVERRIDE those methods with real logic.

    Analogy: The generated base class is like a job description that says
    "this chef must know how to make SayHello". Our class is the actual chef
    who implements the recipe.
    """
    def SayHello(self, request, context):
        """
        Handle the SayHello RPC call.

        Parameters:
        -----------
        request : greeting_pb2.HelloRequest
            The incoming message from the client. It has a 'name' field.
            This object was automatically deserialized from binary protobuf bytes
            into a Python object by gRPC. You didn't have to parse JSON manually!

        context : grpc.ServicerContext
            Metadata about the RPC call. You can use it to:
            - Set response headers/trailers (like HTTP headers)
            - Set error status codes (like HTTP 404, 500, etc.)
            - Check if the client cancelled the request
            - Get the client's IP address, auth info, etc.
            For our simple example, we won't use it, but it's always there.

        Returns:
        --------
        greeting_pb2.HelloReply
            The response message. gRPC will automatically serialize this to binary
            protobuf and send it back to the client over HTTP/2.
        """
        # Extract the 'name' from the request (e.g., "Alice")
        client_name = request.name
        print(f"📨 Received request: name = '{client_name}'")

        # Create and return the response message.
        # greeting_pb2.HelloReply(message=...) creates a protobuf message instance
        # with the 'message' field set to our greeting string.
        reply = greeting_pb2.HelloReply(message=f"Hello, {client_name}! Welcome to gRPC!")
        print(f"📤 Sending response: '{reply.message}'")

        return reply
    
    def SayBye(self,request,context):
        reply = greeting_pb2.ByeReply(message=f"Hello, Man i Dont Hekcin even know how you are but Bye")
        print(f"📤 Sending response: '{reply.message}'")
        return reply
# ──────────────────────────────────────────────────────
# SERVER SETUP & STARTUP
# ──────────────────────────────────────────────────────

def serve():
    """
    Create, configure, and start the gRPC server.
    """

    # Step 1: Create the server with a thread pool.
    # ──────────────────────────────────────────────
    # ThreadPoolExecutor(max_workers=10) means the server can handle up to 10
    # simultaneous RPC calls. Each call gets its own thread.
    #
    # Why threads? Because your RPC method (SayHello) might do slow things like
    # database queries, file I/O, or calling other services. Threads let the server
    # handle other requests while waiting for slow operations.
    #
    # In production, you'd tune 'max_workers' based on your workload.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Step 2: Register our service implementation with the server.
    # ──────────────────────────────────────────────────────────────
    # This tells the server: "When someone calls a method on the 'Greeter' service,
    # use this GreeterServicer instance to handle it."
    #
    # You can register MULTIPLE services on the same server.
    greeting_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)

    # Step 3: Enable Server Reflection (for Postman / grpcurl testing).
    # ──────────────────────────────────────────────────────────────────
    # Reflection lets clients discover your services at runtime without .proto files.
    # We list all the service names we want to expose, plus the reflection service itself.
    SERVICE_NAMES = (
        greeting_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,  # 'greeting.Greeter'
        reflection.SERVICE_NAME,  # The reflection service itself
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    # Step 4: Tell the server which address/port to listen on.
    # ─────────────────────────────────────────────────────────
    # '[::]:50051' means:
    #   - '[::]' = Listen on ALL network interfaces (IPv4 and IPv6). Like '0.0.0.0' in REST.
    #   - ':50051' = Port 50051 (the conventional default port for gRPC, like 8080 for HTTP).
    #
    # 'add_insecure_port' means NO TLS/SSL encryption. Fine for learning and local dev.
    # In production, you'd use 'add_secure_port' with TLS certificates.
    port = "50051"
    server.add_insecure_port(f"[::]:{port}")

    # Step 5: Start the server!
    # ─────────────────────────
    # After this call, the server is running and accepting connections.
    server.start()
    print(f"✅ gRPC server started on port {port}")
    print(f"🔍 Server reflection enabled (Postman/grpcurl can auto-discover services)")
    print("⏳ Waiting for requests... (Press Ctrl+C to stop)\n")

    # Step 6: Keep the server running until interrupted.
    # ───────────────────────────────────────────────────
    # server.start() is non-blocking — it starts the server in background threads.
    # server.wait_for_termination() blocks the main thread so the program doesn't exit.
    # Without this line, the script would start the server and immediately exit!
    server.wait_for_termination()


# ──────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    # This guard ensures 'serve()' only runs when you execute this file directly
    # (python server.py), NOT when it's imported as a module.
    serve()
