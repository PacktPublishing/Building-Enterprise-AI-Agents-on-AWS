import base64
import json
import os
import time
import requests

CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
CLIENT_SECRET = os.environ["COGNITO_CLIENT_SECRET"]
TOKEN_URL = os.environ["COGNITO_TOKEN_URL"]
SCOPE = os.environ["COGNITO_SCOPE"]


def fetch_access_token():
    response = requests.post(
        TOKEN_URL,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials", "scope": SCOPE},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("token_type", "").lower() != "bearer":
        raise RuntimeError("Expected a bearer access token")
    return payload["access_token"], payload.get("expires_in")


def decode_unverified_payload(token):
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Expected a JWT with three sections")
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


def safe_claim_view(token):
    claims = decode_unverified_payload(token)
    visible = ("iss", "client_id", "scope", "token_use", "iat", "exp", "sub")
    return {name: claims.get(name) for name in visible if name in claims}


def token_is_expired(token, clock_skew_seconds=30):
    claims = decode_unverified_payload(token)
    exp = claims.get("exp")
    if exp is None:
        return True
    return time.time() >= (exp - clock_skew_seconds)


if __name__ == "__main__":
    token, expires_in = fetch_access_token()
    print("Access token received successfully")
    print(f"Expires in: {expires_in} seconds")
    print(json.dumps(safe_claim_view(token), indent=2))
