import sys
print("Python executable:", sys.executable)
try:
    import fastapi
    print("fastapi ok")
except ImportError as e:
    print("fastapi missing:", e)

try:
    import httpx
    print("httpx ok")
except ImportError as e:
    print("httpx missing:", e)

try:
    from fastapi.testclient import TestClient
    print("TestClient ok")
except ImportError as e:
    print("TestClient missing (likely starlette/httpx issue):", e)

try:
    import transformers
    print("transformers ok")
except ImportError as e:
    print("transformers missing:", e)

try:
    import torch
    print("torch ok")
except ImportError as e:
    print("torch missing:", e)
