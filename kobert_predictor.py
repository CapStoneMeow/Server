from fastapi import HTTPException
from transformers import AutoModelForSequenceClassification, AutoConfig
import torch
import os
from tokenization_kobert import KoBertTokenizer

MODEL_DIR = "./model/kobert"

label_map = {
    0: "초등_저학년",
    1: "초등_고학년",
    2: "초등_중학년"
}

_tokenizer = None
_model = None

def load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        try:
            print("📦 KoBERT .bin 모델 로드 중...")
            print("📂 MODEL_DIR 내용:", os.listdir(MODEL_DIR))

            # ✅ KoBertTokenizer는 custom 초기화 (from_pretrained X)
            vocab_file = os.path.join(MODEL_DIR, "tokenizer_78b3253a26.model")
            vocab_txt = os.path.join(MODEL_DIR, "vocab.txt")
            _tokenizer = KoBertTokenizer(vocab_file=vocab_file, vocab_txt=vocab_txt)

            # ✅ config 강제 세팅 (num_labels=3)
            config = AutoConfig.from_pretrained(MODEL_DIR)
            config.num_labels = 3

            # ✅ 모델 로드
            _model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR, config=config, local_files_only=True)
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
