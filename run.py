import uvicorn

# Although the web_server module doesn't exist yet,
# we are creating the entry point as per the new architecture.
# We will create the web_server.py file in a later step.
from src.paddock_parser.frontend.web_server import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
