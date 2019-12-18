from fastapi import FastAPI, Header, HTTPException
from router import file_c
from starlette.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
app.include_router(file_c.router,prefix="/file_c",tags=["file"])

