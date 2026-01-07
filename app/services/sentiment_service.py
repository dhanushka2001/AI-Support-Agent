from transformers import pipeline

model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest"

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    # model="distilbert-base-uncased-finetuned-sst-2-english"
    model=model_path,
    tokenizer=model_path
)


def detect_emotion(text: str) -> str:
    result = sentiment_analyzer(text)[0]
    label = result["label"]
    score = result["score"]

    if label.lower() == "POSITIVE".lower() and score > 0.5:
        return "positive"
        #return score
    elif label.lower() == "NEGATIVE".lower() and score > 0.5:
        return "negative"
        #return score * -1
    else:
        return "neutral"
        #return score 

