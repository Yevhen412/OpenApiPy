from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {"ok": True, "hint": "use /oauth/callback?code=123 to test"}

@app.get("/oauth/callback")
def oauth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return PlainTextResponse("Missing ?code=...", status_code=400)
    # Показываем ровно то, что пришло
    return PlainTextResponse(f"Authorization code: {code}", status_code=200)
