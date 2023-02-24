import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline

# global constants
EVENT_Q = "What type of event happened?"  # trigger questions
# source: https://huggingface.co/veronica320/QA-for-Event-Extraction
MODEL_PATH = 'veronica320/QA-for-Event-Extraction'
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DEVICE_ID = 0 if torch.cuda.is_available() else -1


class QAEvent:

    def __init__(self, model_path, device, device_id):
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        model.to(device)  # model to CPU/GPU depending on availability
        self.pipeline = pipeline(
            "question-answering", model=model, tokenizer=tokenizer, device=device_id)

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
    qa_event = QAEvent(model_path=MODEL_PATH,
                       device=DEVICE, device_id=DEVICE_ID)
    for row_title in tqdm(rows):
        try:
            answer = qa_event.predict(question=EVENT_Q, context=row_title)
            if answer:
                events.append(dict(event=answer.get('answer'),
                              confidence=answer.get('score')))

            else:
                events.append(dict(event=None, confidence=None))

        except Exception as e:
            print(e)
            events.append(dict(event=None, confidence=None))

    return events
