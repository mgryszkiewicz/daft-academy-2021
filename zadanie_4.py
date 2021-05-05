from fastapi import FastAPI, Response, Request, Depends, status, HTTPException, Cookie
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from datetime import datetime
# import hashlib

app = FastAPI()
app.access_token_1 = []
app.access_token_2 = []

security = HTTPBasic()



