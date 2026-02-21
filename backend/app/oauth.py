"""
Google OAuth2 authentication
"""
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from .config import settings
import os

# OAuth configuration
config = Config(environ={
    'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID', ''),
    'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET', ''),
})

oauth = OAuth(config)

# Register Google OAuth
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    OAUTH_ENABLED = True
else:
    OAUTH_ENABLED = False
    print("⚠️ Google OAuth not configured")
