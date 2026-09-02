
from fastapi import FastAPI
from router_login import router as login_r
from router_leitner import router as leitner_r

app = FastAPI()
app.include_router(router=login_r)
app.include_router(router=leitner_r)