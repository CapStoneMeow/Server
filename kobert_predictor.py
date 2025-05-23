from fastapi import HTTPException
from transformers import AutoConfig, AutoTokenizer, AutoModelForSequenceClassification
from safetensors.torch import load_file
import torch
import os

MODEL_DIR = "./model/kobert"  # 필요시 절대경로로 수정
SAFETENSORS_PATH = os.path.join(MODEL_DIR, "model.safetensors")

label_map = {
    0: "초등_저학년",
    1: "초등_고학년"
}

_tokenizer = None
_model = None

def load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        try:
            print("📦 KoBERT safetensors 모델 로드 중...")
            print("📂 MODEL_DIR 내용:", os.listdir(MODEL_DIR))

            # ✅ config 및 tokenizer 로드
            config = AutoConfig.from_pretrained(MODEL_DIR, local_files_only=True)
            _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)

            # ✅ 빈 모델 생성 후 safetensors 적용
            _model = AutoModelForSequenceClassification.from_config(config)
            state_dict = load_file(SAFETENSORS_PATH)
            _model.load_state_dict(state_dict)
            _model.eval()

            print("✅ 모델 로드 완료")
        except Exception as e:
            print("❌ 모델 로드 실패:", e)
            raise RuntimeError("모델 또는 토크나이저 로드 실패")

def predict_grade(text: str) -> dict:
    try:
        load_model()
        inputs = _tokenizer(text, return_tensors="pt", padding="max_length", truncation=True, max_length=128)
        with torch.no_grad():
            outputs = _model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()

        return {
            "label_index": pred,
            "label": label_map.get(pred, "Unknown")
        }

    except Exception as e:
        print("❌ 예측 실패:", e)
        raise HTTPException(status_code=500, detail=f"예측 중 오류 발생: {str(e)}")
