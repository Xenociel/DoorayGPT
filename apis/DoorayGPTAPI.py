import json
import os
import requests
import openai
from dotenv import load_dotenv
from threading import Thread
import redis

load_dotenv()

# Redis 서버에 연결
redis_db1 = redis.Redis(host='localhost', port=6379, db=0)
redis_db2 = redis.Redis(host='localhost', port=6379, db=1)
MEMBERSEARCHING = 'https://api.dooray.com/common/v1/members/'
INCOMING_HEADER = {'Content-Type':'application/json;charset = utf-8'}
OPEN_API_KEY = str(os.getenv("OPEN_API_KEY"))
DOORAY_API_KEY = str(os.getenv("DOORAY_API_KEY"))
openai.api_key = OPEN_API_KEY
# 모델 - GPT 3.5 Turbo 선택
model = "gpt-3.5-turbo"


def chatbot_response(user_id: str, messages: str):
    # 이전 대화 기록을 불러와서 CHATGPT 모델에 전달하여 응답 반환
    history = redis_db1.lrange(user_id, 0, -1)
    if len(history) != 0:
        history = [json.loads(msg.decode("utf-8")) for msg in history]
        history.append({"role": "user", "content": messages})
    else:
        history = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": messages}]
        redis_db1.rpush(user_id, json.dumps({"role": "system", "content": "You are a helpful assistant."}))

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=history
    )
    redis_db1.rpush(user_id, json.dumps({"role": "user", "content": messages}))
    redis_db1.rpush(user_id, json.dumps({"role": "assistant", "content": response.choices[0]["message"]["content"]}))

    return response.choices[0]["message"]["content"]


def DoorayGPTResponse(query):
    # 이전 대화 기록을 불러와서 CHATGPT 모델에 전달하여 응답 생성
    session_id = "session:" + query["userId"]
    # 생성한 응답과 사용자의 메시지를 대화 기록에 저장

    userresponse = requests.get(url=MEMBERSEARCHING+query["userId"], headers={"Authorization":DOORAY_API_KEY})
    response = chatbot_response(session_id, query["text"])

    resp_data = {
        "botName": "DoorayGPT",
        "botIconImage": "",
        "attachments": [
            {
                "text": json.loads(userresponse.content)["result"]["name"]+'님의 요청에 대한 답변입니다. \n\n\nQ: '
                        + query['text'] + "\n\nA: " + response +
                        '\n\n\n ===*대화 주제를 바꾸시려면 \'/resetgpt\'를 사용 후 \'/gpt\'로 새로운 대화를 시작해 주세요\n '
                        '해당 명령어로 새 주제 시작시 이전 주제의 대화는 사라집니다.*=== ',
                "color": "blue"
            }
        ]
    }

    INCOMING_URL = json.loads(redis_db2.get(session_id))
    response = requests.post(url=INCOMING_URL["hook-url"], headers=INCOMING_HEADER, data=json.dumps(resp_data))


def DoorayGPTHelp(query):
    session_id = "session:" + query["userId"]
    userresponse = requests.get(url=MEMBERSEARCHING+query["userId"], headers={"Authorization":DOORAY_API_KEY})

    resp_data = {
        "botName": "DoorayGPT",
        "botIconImage": "",
        "attachments": [
            {
                "text": json.loads(userresponse.content)["result"]["name"]+'님의 요청에 대한 답변입니다. \n\n\n'
                        '1. 우측상단의 채널별 멤버/설정 버튼을 누르고 설정 탭으로 이동하여 서비스 연동을 클릭합니다.\n\n'
                        '2. (연동 중인 서비스에 \'incoming\'이 있는 경우 3번을 수행합니다.)서비스 추가 탭으로 이동하여 스크롤을 내린 '
                                                                           '후 \'incoming\' 서비스를 추가해 줍니다.\n\n'
                        '3. 연동 중인 서비스 탭으로 이동하여 우측의 \'연동 URL\'을 클릭하여 URL을 클립보드에 복사합니다.\n\n'
                        '4. 채팅 창으로 돌아가 입력창에 \'/gptset [복사한 연동 URL]\' 을 입력하고 엔터를 누릅니다.\n\n'
                        '5. \'Chat Answer URL successfully set\' 메세지가 출력되었다면 세팅이 완료되었습니다.\n\n'
                        '6. GPT와 대화를 시작하려면 \'/gpt [대화 내용]\'으로 시작하십시오\n\n',
                "color": "blue"
            }
        ]
    }

    INCOMING_URL = json.loads(redis_db2.get(session_id))
    response = requests.post(url=INCOMING_URL["hook-url"], headers=INCOMING_HEADER, data=json.dumps(resp_data))


def DoorayGPTAPI(query):
    session_id = "session:" + query["userId"]

    if redis_db2.exists(session_id) == False:
        return u'Please set incoming URL First....'

    thr = Thread(target=DoorayGPTResponse, args=[query])
    thr.start()

    return u'Please waiting for Answer....'


def DoorayGPTSet(query):
    session_id = "session:" + query["userId"]
    redis_db2.set(session_id, json.dumps({"hook-url": query["text"]}))

    return u'Chat Answer URL successfully set'


def DoorayGPTEnd(query):
    session_id = "session:" + query["userId"]
    redis_db1.delete(session_id)

    return u'Chat session successfully deleted'


def DoorayGPTHistAPI(query):
    session_id = "session:" + query["userId"]

    if redis_db2.exists(session_id) == False:
        return u'Please set incoming URL First....'

    thr = Thread(target=DoorayGPTGet, args=[query])
    thr.start()

    return 'Please waiting for Answer....'

def DoorayGPTHelpAPI(query):
    session_id = "session:" + query["userId"]

    if redis_db2.exists(session_id) == False:
        return u'Please set incoming URL First....'

    thr = Thread(target=DoorayGPTHelp)
    thr.start()


def DoorayGPTGet(query):
    session_id = "session:" + query["userId"]
    answerHist = '[진행한 대화 내역]\n\n'
    history = redis_db1.lrange(session_id, 0, -1)
    if len(history) != 0:
        history = [json.loads(msg.decode("utf-8")) for msg in history]
        for msg in history :
            if msg["role"] == 'user':
                answerHist = answerHist + 'Q: ' + msg["content"] + '\n'
            elif msg["role"] == 'assistant':
                answerHist = answerHist + 'A: ' + msg["content"] + '\n\n'

        resp_data = {
            "botName": "DoorayGPT",
            "botIconImage": "",
            "attachments": [
                {
                    "text": answerHist,
                    "color": "blue"
                }
            ]
        }

    else:
        resp_data = {
            "botName": "DoorayGPT",
            "botIconImage": "",
            "attachments": [
                {
                    "text": u'there\'s no history',
                    "color": "blue"
                }
            ]
        }
    INCOMING_URL = json.loads(redis_db2.get(session_id))
    response = requests.post(url=INCOMING_URL["hook-url"], headers=INCOMING_HEADER, data=json.dumps(resp_data))




