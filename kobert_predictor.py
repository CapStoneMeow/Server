import torch
from transformers import BertTokenizer, AutoModelForSequenceClassification

# ✅ 모델 경로
MODEL_PATH = "./model/kobert"

# ✅ 라벨 매핑
label_map = {
    0: "초등_저학년",
    1: "초등_고학년"
}

# ✅ 전역 모델/토크나이저 객체
_tokenizer = None
_model = None

# ✅ 모델 로드 함수
def load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        try:
            print("📦 KoBERT 모델 로드 중...")
            _tokenizer = BertTokenizer.from_pretrained(
                MODEL_PATH,
                local_files_only=True,
                trust_remote_code=True
            )
            _model = AutoModelForSequenceClassification.from_pretrained(
                MODEL_PATH,
                local_files_only=True,
                trust_remote_code=True
            )
            _model.eval()
            print("✅ 모델 로드 완료")
        except Exception as e:
            print("❌ 모델 로드 실패:", e)
            raise RuntimeError("모델 또는 토크나이저를 불러오는 중 오류 발생")

# ✅ 예측 함수
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
