"""Shadow Library - Server Runner"""

import uvicorn
from web_server import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
