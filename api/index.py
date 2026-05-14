import sys
import os

# Add the project root to the path so it can find the backend module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

# Export the app for Vercel
# This allows Vercel to treat this as a serverless function
# that handles all /api/* requests
