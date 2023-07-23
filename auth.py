from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

import os
load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
oauth = OAuth()

# Read Okta configuration from environment variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
okta_domain = os.getenv("OKTA_DOMAIN")
token_endpoint = f"https://{okta_domain}/oauth2/default/v1/token"


oauth.register(
    name="okta",
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url=f"https://{okta_domain}/oauth2/default/.well-known/oauth-authorization-server",
    client_kwargs={
        "scope": "openid profile",
    },
)
