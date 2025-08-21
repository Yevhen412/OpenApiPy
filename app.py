from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/oauth/callback", response_class=HTMLResponse)
async def callback(request: Request, code: str = None, error: str = None):
    if error:
        return f"<h2>OAuth error: {error}</h2>"
    if code:
        return f"<h2>Authorization code: {code}</h2>"
    return "<h2>No code received</h2>"
