import torch
from transformers import BertTokenizer, AutoModelForSequenceClassification

# ✅ 모델 저장 경로 (Render 또는 로컬 서버 내부 경로)
MODEL_PATH = "./saved_models/fine_tuned_kobert_book_all/checkpoint-3198"

# ✅ 로컬에서 tokenizer 및 model 불러오기 (Hugging Face Hub 접근 X)
tokenizer = BertTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True,
    trust_remote_code=True
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH,
    local_files_only=True,
    trust_remote_code=True
)

model.eval()

# ✅ 라벨 매핑
label_map = {
    0: "초등_저학년",
    1: "초등_고학년"
}

# ✅ 예측 함수
def predict_grade(text: str) -> dict:
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)
        pred = torch.argmax(outputs.logits, dim=1).item()

    return {
        "label_index": pred,
        "label": label_map[pred]
    }
