from fastapi import FastAPI, Response, Request, Depends, status, HTTPException, Cookie
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from datetime import datetime
# import hashlib

app = FastAPI()
app.access_token_1 = [] #przerobić to na liste i powinno śmigać
app.access_token_2 = []

security = HTTPBasic()


@app.get("/hello", response_class=HTMLResponse)
def hello():
    return '<h1>Hello! Today date is ' + str(datetime.today().strftime('%Y-%m-%d')) + '</h1>'


@app.post("/login_session", status_code=201)
def login_session(*, response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    if not (credentials.username == '4dm1n' and credentials.password == 'NotSoSecurePa$$'):
        raise HTTPException(status_code=401)

    new_access_token_1 = hash(datetime.now())
    app.access_token_1.append(str(new_access_token_1))
    while len(app.access_token_1) > 3: app.access_token_1.pop(0)
    response.set_cookie(key="session_token", value=new_access_token_1)
    return


@app.post("/login_token", status_code=201)
def login_token(*, response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    if not (credentials.username == '4dm1n' and credentials.password == 'NotSoSecurePa$$'):
        raise HTTPException(status_code=401)

    new_access_token_2 = hash(datetime.now())
    app.access_token_2.append(str(new_access_token_2))
    while len(app.access_token_2) > 3: app.access_token_2.pop(0)
    return {"token": new_access_token_2}


@app.get("/welcome_session")
def welcome_session(*, request: Request, session_token: str = Cookie(None)):
    if not (str(session_token) in app.access_token_1):
        raise HTTPException(status_code=401)
    if str(request.query_params.get("format")) == "json":
        return JSONResponse(content={"message": "Welcome!"})
    elif str(request.query_params.get("format")) == "html":
        return HTMLResponse(content="<h1>Welcome!</h1>")
    else:
        return PlainTextResponse(content="Welcome!")


@app.get("/welcome_token")
def welcome_token(format: Optional[str] = "", token: Optional[str] = ""):
    if not (str(token) in app.access_token_2):
       raise HTTPException(status_code=401) 
    if format == "json":
        return JSONResponse(content={"message": "Welcome!"})
    elif format == "html":
        return HTMLResponse(content="<h1>Welcome!</h1>")
    else:
        return PlainTextResponse(content="Welcome!")
    

@app.delete("/logout_session")
def logout_session(format: Optional[str] = "", session_token: str = Cookie(None)):
    if not (str(session_token) in app.access_token_1):
        raise HTTPException(status_code=401)
    while session_token in app.access_token_1: app.access_token_1.remove(session_token)
    return RedirectResponse("/logged_out?format=" + format, status_code=303)


@app.delete("/logout_token")
def logout_token(token: Optional[str], format: Optional[str] = ""):
    if not (str(token) in app.access_token_2):
        raise HTTPException(status_code=401)
    while token in app.access_token_2: app.access_token_2.remove(token)
    return RedirectResponse("/logged_out?format=" + format, status_code=303)


@app.get("/logged_out")
def logged_out(format: Optional[str] = ""):
    if format == "json":
        return JSONResponse(content={"message": "Logged out!"})
    elif format == "html":
        return HTMLResponse(content="<h1>Logged out!</h1>")
    else:
        return PlainTextResponse(content="Logged out!")
