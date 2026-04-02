"""HTTP client implementations for Wikipedia-API requests.

Provides both synchronous and asynchronous HTTP clients with retry logic,
rate limiting handling, and proper error handling.
"""

from .async_http_client import AsyncHTTPClient
from .base_http_client import USER_AGENT, BaseHTTPClient
from .sync_http_client import SyncHTTPClient

__all__ = [
    "BaseHTTPClient",
    "SyncHTTPClient",
    "AsyncHTTPClient",
    "USER_AGENT",
]
