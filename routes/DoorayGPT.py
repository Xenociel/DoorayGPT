from fastapi import APIRouter,HTTPException
from apis import DoorayGPTAPI
from db.classes import Dooray
import chardet


router = APIRouter(
    prefix="/DoorayGPT"  # url 앞에 고정적으로 붙는 경로추가
)  # Route 분리


@router.post("/gpt", tags=["DoorayGPT"])
async def DoorayGPT(dooray:Dooray):
    dooray = dooray.dict()
    if dooray["text"] == "":
        raise HTTPException(status_code=404, detail="Error: 질문이 없습니다.")

    responsetext = DoorayGPTAPI.DoorayGPTAPI(dooray)

    return {
        "text": responsetext,
        "responseType": "inChannel"
    }


@router.post("/setting", tags=["DoorayGPT"])
async def setting(dooray:Dooray):
    # 사용자의 세션 ID 삭제
    dooray = dooray.dict()
    responsetext = DoorayGPTAPI.DoorayGPTSet(dooray)

    return {
        "text": responsetext,
        "responseType": "ephemeral"
    }


@router.post("/end_session", tags=["DoorayGPT"])
async def end_session(dooray:Dooray):
    # 사용자의 세션 ID 삭제
    dooray = dooray.dict()
    responsetext = DoorayGPTAPI.DoorayGPTEnd(dooray)

    return {
        "text": responsetext,
        "responseType": "ephemeral"
    }


@router.post("/get_messages", tags=["DoorayGPT"])
async def get_messages(dooray:Dooray):
    # 사용자의 세션 ID를 기반으로 대화 기록 조회
    dooray = dooray.dict()
    responsetext = DoorayGPTAPI.DoorayGPTHistAPI(dooray)

    return {
        "text": responsetext,
        "responseType": "ephemeral"
    }


@router.post("/help", tags=["DoorayGPT"])
async def gpt_help(dooray:Dooray):
    # 사용자의 세션 ID를 기반으로 대화 기록 조회
    dooray = dooray.dict()
    responsetext = DoorayGPTAPI.DoorayGPTHelp(dooray)

    return {
        "text": responsetext,
        "responseType": "ephemeral"
    }