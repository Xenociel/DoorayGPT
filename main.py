import openai

import uvicorn
import os
from dotenv import load_dotenv

from fastapi import FastAPI
from routes.DoorayGPT import router as search_router

load_dotenv()

app = FastAPI(title='Dooray-GPT API',
              description='Dooray-GPT API')   # FastAPI 모듈
app.include_router(search_router)  # 다른 route파일들을 불러와 포함시킴

if __name__ == "__main__":
    API_IP = str(os.getenv("HOST_IP"))
    API_PORT = int(os.getenv("HOST_PORT"))

    uvicorn.run(app, headers=[("charset", "utf-8")], host=API_IP, port=API_PORT)