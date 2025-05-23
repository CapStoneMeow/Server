import torch
from transformers import BertTokenizer, BertForSequenceClassification
import os

MODEL_PATH = "./model/kobert"

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
            print("📦 KoBERT 모델 로드 중...")
            print("📂 MODEL_PATH 내용:", os.listdir(MODEL_PATH))

            _tokenizer = BertTokenizer.from_pretrained(
                MODEL_PATH,
                local_files_only=True
            )

            _model = BertForSequenceClassification.from_pretrained(
                MODEL_PATH,
                local_files_only=True
            )
            _model.eval()
            print("✅ 모델 로드 완료")
        except Exception as e:
            print("❌ 모델 로드 실패:", e)
            raise RuntimeError("모델 또는 토크나이저를 불러오는 중 오류 발생")

def predict_grade(text: str) -> dict:
    load_model()

    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128
    )

    with torch.no_grad():
        outputs = _model(**inputs)
        pred = torch.argmax(outputs.logits, dim=1).item()

    return {
        "label_index": pred,
        "label": label_map.get(pred, "Unknown")
    }
