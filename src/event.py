import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline

# global constants
EVENT_Q = "What type of event happened?"  # trigger questions
# source: https://huggingface.co/veronica320/QA-for-Event-Extraction
MODEL_PATH = 'veronica320/QA-for-Event-Extraction'
EVENT_Q = "What type of event happened?"  # trigger questions


class QAEvent:

    def __init__(self, model_path, device=0):
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        model.to(torch.device("cuda"))  # model to GPU
        self.pipeline = pipeline(
            "question-answering", model=model, tokenizer=tokenizer, device=device)

    def predict(self, question, context):
        try:
            ans = self.pipeline(question=question, context=context)
            return ans  # answer, score

        except Exception as e:
            print(e)
            ans = None


def run_event_extraction(df):
    events = []
    rows = df.title.tolist()
    # NB: make sure there's enough space in HDD
    qa_event = QAEvent(model_path=MODEL_PATH)
    for row_title in tqdm(rows):
        row_event = []
        try:
            answer = qa_event.predict(question=EVENT_Q, context=row_title)
            if answer:
                events.append(dict(event=answer.get('answer'),
                              confidence=answer.get('score')))

            else:
                events.append(dict(event=None, score=None))

        except Exception as e:
            print(e)
            events.append(dict(event=None, score=None))

    return events
