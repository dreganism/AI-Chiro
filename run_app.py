#!/usr/bin/env python3
import sys
import os

# Triple-force the path
sys.path.insert(0, "/opt/sjwg-ai-reporter")
sys.path.insert(0, "/opt/sjwg-ai-reporter/backend")
os.environ["PYTHONPATH"] = "/opt/sjwg-ai-reporter:" + os.environ.get("PYTHONPATH", "")

print("PYTHONPATH:", os.environ["PYTHONPATH"])
print("sys.path:", sys.path[:5])

try:
    from backend.main import app
    print("SUCCESS: Imported app from backend.main")
except Exception as e:
    print("FATAL IMPORT ERROR:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Run with uvicorn directly
import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
