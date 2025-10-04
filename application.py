# Alternative Railway deployment entry point
# This file serves as the main entry point for Railway

import os
from app import app

# Railway expects the Flask app to be named 'application'
application = app

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))