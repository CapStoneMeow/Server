import torch
from transformers import BertTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "checkpoint-3198"  # 모델 위치에 맞게 수정
tokenizer = BertTokenizer.from_pretrained("monologg/kobert")
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

label_map = {
    0: "초등_저학년",
    1: "초등_고학년"
}

def predict_grade(text: str) -> dict:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        pred = torch.argmax(outputs.logits, dim=1).item()
    return {"label_index": pred, "label": label_map[pred]}
