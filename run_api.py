import uvicorn
import os

if __name__ == "__main__":
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run the server with explicit host and port
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Changed from 0.0.0.0 to 127.0.0.1
        port=8080,  # Changed from 8000 to 8080
        reload=True,
        log_level="info"
    ) 