import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests
import uuid
from dotenv import load_dotenv

# 🔥 .env 파일 로드
load_dotenv()

# FastAPI 라우터 생성
feedback_router = APIRouter()

# ========================== 기본 문장 평가 API ==========================

class FeedbackInput(BaseModel):
    user_id: int
    sentence: str

class FeedbackResult(BaseModel):
    score: float
    suggestion: str

@feedback_router.post("/evaluate", response_model=FeedbackResult)
def evaluate_sentence(input_data: FeedbackInput):
    sentence = input_data.sentence.strip()
    score = min(1.0, max(0.1, len(sentence) / 50))
    suggestion = sentence.replace("진취적인", "적극적인") if "진취적인" in sentence else "문장이 자연스럽습니다."

    return FeedbackResult(
        score=round(score, 2),
        suggestion=suggestion
    )


# ========================== Clova X - 1차 질문 API ==========================

class ChatInput(BaseModel):
    category: str

@feedback_router.post("/start_chat")
def start_chat(input_data: ChatInput):
    api_key = os.getenv("CLOVA_X_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="CLOVA_X_API_KEY가 설정되지 않았습니다.")

    url = "https://clovastudio.stream.ntruss.com/testapp/v3/chat-completions/HCX-005"

    headers = {
        "Authorization": api_key,
        "X-NCP-CLOVASTUDIO-REQUEST-ID": str(uuid.uuid4()),
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "text/event-stream"
    }

    messages = [
        {
            "role": "system",
            "content": (
                "너는 초등학생과 대화하는 친절한 AI야. "
                "학생이 자연스럽게 자신의 생각을 말할 수 있도록 "
                "어렵지 않고 부드럽게 질문을 만들어줘. "
                "카테고리(일상, 사회, 자연, 과학, 인문)에 맞춰 질문을 해. "
                "문장은 한 문장으로 끝내줘."
            )
        },
        {
            "role": "user",
            "content": f"{input_data.category}에 대해 초등학생에게 질문 하나 만들어줘."
        }
    ]

    request_data = {
        "messages": messages,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.5,
        "repetitionPenalty": 1.1,
        "stop": [],
        "includeAiFilters": True,
        "seed": 0
    }

    try:
        response = requests.post(url, headers=headers, json=request_data, stream=True)
        response.raise_for_status()

        final_question = ""
        current_event = ""

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8").strip()
                #print(f"🔵 받은 라인: {decoded_line}")

                if decoded_line.startswith("event:"):
                    current_event = decoded_line[len("event:"):].strip()

                elif decoded_line.startswith("data:"):
                    data_json = decoded_line[len("data:"):].strip()
                    try:
                        parsed = json.loads(data_json)

                        if current_event == "result":
                            if "message" in parsed and "content" in parsed["message"]:
                                final_question = parsed["message"]["content"].strip()
                                print(f"✅ 최종 질문 (stop 시점): {final_question}")
                                break

                    except json.JSONDecodeError:
                        continue

        if not final_question:
            raise HTTPException(status_code=500, detail="최종 질문을 가져오지 못했습니다.")

        return {"question": final_question}

    except Exception as e:
        return {"error": str(e)}


# ========================== Clova X - 꼬리 질문 API ==========================

class FollowUpInput(BaseModel):
    answer: str

@feedback_router.post("/followup_chat")
def followup_chat(input_data: FollowUpInput):
    api_key = os.getenv("CLOVA_X_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="CLOVA_X_API_KEY가 설정되지 않았습니다.")

    url = "https://clovastudio.stream.ntruss.com/testapp/v3/chat-completions/HCX-005"

    headers = {
        "Authorization": api_key,
        "X-NCP-CLOVASTUDIO-REQUEST-ID": str(uuid.uuid4()),
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "text/event-stream"
    }

    followup_prompt = [
        {
            "role": "system",
            "content": (
                "너는 초등학생과 대화하는 친절한 AI야. "
                "학생의 답변을 듣고 자연스럽게 이어지는 부드러운 다음 질문을 만들어줘. "
                "문장은 한 문장으로 끝내고, 어렵지 않고 따뜻하게 해줘."
            )
        },
        {
            "role": "user",
            "content": f"학생이 이렇게 대답했어: \"{input_data.answer}\"\n"
                       "이 대답에 자연스럽게 이어질 수 있는 질문을 하나 만들어줘."
        }
    ]

    request_data = {
        "messages": followup_prompt,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.5,
        "repetitionPenalty": 1.1,
        "stop": [],
        "includeAiFilters": True,
        "seed": 0
    }

    try:
        response = requests.post(url, headers=headers, json=request_data, stream=True)
        response.raise_for_status()

        followup_question = ""
        current_event = ""

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8").strip()
                #print(f"🔵 받은 라인: {decoded_line}")

                if decoded_line.startswith("event:"):
                    current_event = decoded_line[len("event:"):].strip()

                elif decoded_line.startswith("data:"):
                    data_json = decoded_line[len("data:"):].strip()
                    try:
                        parsed = json.loads(data_json)

                        if current_event == "result":
                            if "message" in parsed and "content" in parsed["message"]:
                                followup_question = parsed["message"]["content"].strip()
                                print(f"✅ 최종 꼬리질문 (stop 시점): {followup_question}")
                                break

                    except json.JSONDecodeError:
                        continue

        if not followup_question:
            raise HTTPException(status_code=500, detail="최종 꼬리질문을 가져오지 못했습니다.")

        return {"followup_question": followup_question}

    except Exception as e:
        return {"error": str(e)}

@feedback_router.post("/end_chat")
def end_chat():
    api_key = os.getenv("CLOVA_X_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="CLOVA_X_API_KEY가 설정되지 않았습니다.")

    url = "https://clovastudio.stream.ntruss.com/testapp/v3/chat-completions/HCX-005"

    headers = {
        "Authorization": api_key,
        "X-NCP-CLOVASTUDIO-REQUEST-ID": str(uuid.uuid4()),
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "text/event-stream"
    }

    messages = [
        {
            "role": "system",
            "content": (
                "너는 초등학생과 대화하는 따뜻한 AI야. "
                "사전 테스트를 잘 끝낸 학생에게 부드럽고 다정하게 마무리 인사를 한 문장으로 해줘. "
                "예를 들어 '수고했어! 이제 학습하러 가볼까?' 같은 느낌으로 짧고 따뜻하게 말해줘."
            )
        },
        {
            "role": "user",
            "content": "사전 테스트를 마쳤어. 따뜻하게 마무리 멘트를 해줘."
        }
    ]

    request_data = {
        "messages": messages,
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 100,
        "temperature": 0.5,
        "repetitionPenalty": 1.1,
        "stop": [],
        "includeAiFilters": True,
        "seed": 0
    }

    try:
        response = requests.post(url, headers=headers, json=request_data, stream=True)
        response.raise_for_status()

        final_ending = ""
        current_event = ""

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8").strip()
                #print(f"🔵 받은 라인: {decoded_line}")

                if decoded_line.startswith("event:"):
                    current_event = decoded_line[len("event:"):].strip()

                elif decoded_line.startswith("data:"):
                    data_json = decoded_line[len("data:"):].strip()
                    try:
                        parsed = json.loads(data_json)

                        if current_event == "result":
                            if "message" in parsed and "content" in parsed["message"]:
                                final_ending = parsed["message"]["content"].strip()
                                #print(f"✅ 최종 마무리 멘트: {final_ending}")
                                break

                    except json.JSONDecodeError:
                        continue

        if not final_ending:
            raise HTTPException(status_code=500, detail="마무리 멘트를 가져오지 못했습니다.")

        return {
            "ending_message": final_ending,
            "next_action": "학습하기"
        }

    except Exception as e:
        return {"error": str(e)}

