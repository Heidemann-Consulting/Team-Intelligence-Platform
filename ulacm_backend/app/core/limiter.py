# File: ulacm_backend/app/core/limiter.py
# Purpose: Initializes and configures the rate limiter instance.

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize limiter instance
# Key function gets the client's remote address (IP)
# Using in-memory storage, suitable for single instance docker-compose deployment.
# For multi-instance deployments, a shared backend like Redis would be needed.
# Set a reasonable default limit for general API usage.
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
