"""
client.py — The gRPC Client for our Greeting Service
=====================================================

This script does 3 things:
  1. Connects to the gRPC server via a "channel".
  2. Creates a "stub" (a local proxy object that represents the remote service).
  3. Calls the remote SayHello method as if it were a local function call.

Analogy: Think of this as calling a restaurant to place an order.
  - The "channel" is the phone line connecting you to the restaurant.
  - The "stub" is like the restaurant's phone menu system: "Press 1 for SayHello".
  - Making the RPC call is like saying your order into the phone and getting a response.

The beauty of gRPC: The client code looks like a normal function call.
You don't deal with URLs, HTTP methods, headers, or JSON parsing.
gRPC handles all of that under the hood.
"""

# ──────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────

# 'grpc' — The core gRPC library. On the client side, we use it to create channels.
import grpc

# Same path setup as server.py — the generated code needs to find greeting_pb2.
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

# 'greeting_pb2' — Contains the message classes (HelloRequest, HelloReply).
# We need HelloRequest to create our request, and we'll receive HelloReply back.
from generated import greeting_pb2

# 'greeting_pb2_grpc' — Contains the GreeterStub class.
# The "stub" is a client-side proxy that knows how to serialize your request,
# send it over the network, and deserialize the response — all automatically.
from generated import greeting_pb2_grpc


# ──────────────────────────────────────────────────────
# MAIN CLIENT LOGIC
# ──────────────────────────────────────────────────────

def run():
    """
    Connect to the gRPC server and make a SayHello call.
    """

    # Step 1: Create a Channel
    # ─────────────────────────
    # A channel is a connection to the gRPC server. Think of it as a phone line.
    #
    # 'localhost:50051' — Connect to the server running on our own machine, port 50051.
    #
    # 'insecure_channel' — No TLS encryption (matches our server's add_insecure_port).
    # In production, you'd use grpc.secure_channel() with TLS certificates.
    #
    # We use a 'with' statement (context manager) so the channel is automatically
    # closed when we're done — like hanging up the phone after the call.
    #
    # Important: A single channel can be reused for MANY RPC calls. You don't need
    # to create a new channel for each call. Under the hood, gRPC uses HTTP/2
    # multiplexing, so many calls can share one TCP connection simultaneously.
    print("📞 Connecting to gRPC server at localhost:50051...")

    with grpc.insecure_channel('localhost:50051') as channel:

        # Step 2: Create a Stub
        # ──────────────────────
        # The "stub" is a Python object that acts as a proxy for the remote service.
        # It has the same methods as the service defined in the .proto file.
        #
        # When you call stub.SayHello(...), the stub:
        #   1. Serializes your HelloRequest to compact binary (protobuf).
        #   2. Sends it over HTTP/2 to the server.
        #   3. Waits for the server's response.
        #   4. Deserializes the binary response into a HelloReply Python object.
        #   5. Returns it to you.
        #
        # You interact with it like a normal Python object — all the network
        # complexity is hidden. This is the "Remote Procedure Call" magic.
        stub = greeting_pb2_grpc.GreeterStub(channel)

        # Step 3: Create the Request Message
        # ────────────────────────────────────
        # Create a HelloRequest protobuf message with the 'name' field set.
        # This is like filling out a form before sending it.
        name_to_send = "Alice"
        request = greeting_pb2.HelloRequest(name=name_to_send)
        print(f"📤 Sending request: name = '{name_to_send}'")

        # Step 4: Make the RPC Call
        # ──────────────────────────
        # This is where the remote call happens!
        #
        # stub.SayHello(request) does ALL of this behind the scenes:
        #   1. Serializes 'request' → binary bytes using protobuf
        #   2. Opens an HTTP/2 stream to the server
        #   3. Sends HTTP/2 headers: POST /greeting.Greeter/SayHello
        #      (Yes, gRPC uses POST internally! The "URL" is /package.Service/Method)
        #   4. Sends the binary request body in an HTTP/2 DATA frame
        #   5. Server processes it and sends back binary response
        #   6. Client receives the response DATA frame
        #   7. Deserializes binary → HelloReply Python object
        #   8. Returns the HelloReply to you
        #
        # To you, it looks like a simple function call. That's the beauty of gRPC.
        try:
            response = stub.SayHello(request)
            # Step 5: Use the Response
            # ─────────────────────────
            # 'response' is a HelloReply object. Access fields like any Python object.
            print(f"📨 Received response: '{response.message}'")

        except grpc.RpcError as e:
            # gRPC errors are like HTTP errors but more structured.
            # e.code() gives you a status code (like HTTP 404, 500, etc.)
            # e.details() gives you a human-readable error message.
            #
            # Common gRPC status codes (compare to HTTP):
            #   OK (0)              → HTTP 200
            #   INVALID_ARGUMENT (3) → HTTP 400
            #   NOT_FOUND (5)       → HTTP 404
            #   INTERNAL (13)       → HTTP 500
            #   UNAVAILABLE (14)    → HTTP 503 (server is down)
            print(f"❌ RPC failed!")
            print(f"   Status code: {e.code()}")
            print(f"   Details: {e.details()}")

# ──────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    run()
