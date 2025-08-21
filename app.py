from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/oauth/callback", response_class=PlainTextResponse)
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    if error:
        return f"OAuth error: {error}"
    if code:
        return f"Authorization code: {code}"
    return "No code received"
