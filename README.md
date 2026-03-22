# gRPC Practice Repo

## What this repository is about

This repository is a beginner-friendly Python gRPC project.

It contains:
- A simple Greeting gRPC service definition in `protos/greeting.proto`
- Generated gRPC Python files in `generated/`
- A server app in `server.py`
- A client app in `client.py`
- A detailed learning guide in `GRPC_COMPLETE_GUIDE.md`

The goal is to help you understand gRPC from first principles and run a minimal working example locally.

## Full guide

For the complete beginner walkthrough, read:

[Open the complete gRPC guide](GRPC_COMPLETE_GUIDE.md)

## Setup

### 1. Activate your virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
venv\Scripts\activate.bat
```

macOS/Linux:

```bash
source venv/bin/activate
```

### 2. Install dependencies from requirements.txt

```bash
pip install -r requirements.txt
```

This installs everything needed so running the server and client will not fail because of missing packages.

## Run the project

Open two terminals (activate the virtual environment in both).

Terminal 1 (start server):

```bash
python server.py
```

Terminal 2 (run client):

```bash
python client.py
```

If everything is correct, the client prints a greeting response and the server logs the request.

## Optional: regenerate gRPC files after editing .proto

If you change `protos/greeting.proto`, regenerate code with:

```bash
python -m grpc_tools.protoc -I./protos --python_out=./generated --grpc_python_out=./generated ./protos/greeting.proto
```
