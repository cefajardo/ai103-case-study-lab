import os
import textwrap
import time
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()  # load variables from .env into os.environ

SYSTEM_INSTRUCTIONS = (
    "You are an AI assistant that assesses written English proficiency. "
    "Evaluate the user's text based on grammar, vocabulary, coherence, and tone, "
    "then assign an estimated CEFR level (A1–C2) with brief, constructive feedback. "
    'Respond only with a JSON object with keys "cefr_level", "grammar", '
    '"vocabulary", "coherence", "tone", and "feedback".'
)

def choose_model() -> str:
    """Ask the user for a model size and return the matching deployment name."""
    models = {
        "small": os.environ["SMALL_MODEL_DEPLOYMENT_NAME"],
        "large": os.environ["LARGE_MODEL_DEPLOYMENT_NAME"],
    }
    while True:
        choice = input("Select model size (small/large) [small]: ").strip().lower() or "small"
        if choice in ("s", "l"):
            choice = "small" if choice == "s" else "large"
        if choice in models:
            return models[choice]
        print("Please enter 'small' or 'large'.")


def get_text() -> str:
    """Ask the user for the text to send to the model (cannot be empty)."""
    while True:
        text = input("Text to evaluate: ").strip()
        if text:
            return text
        print("Please enter some text.")

class Scores(BaseModel):
    grammar: int
    vocabulary: int
    coherence: int
    tone_and_style: int


class Correction(BaseModel):
    original: str
    corrected: str
    explanation: str


class EnglishWritingAssessment(BaseModel):
    cefr_level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    confidence_score: float
    scores: Scores
    strengths: list[str]
    corrections: list[Correction]
    improved_version: str


def print_assessment(a: EnglishWritingAssessment) -> None:
    """Print the assessment as a readable report."""
    width = 60
    line = "─" * width

    def section(title: str) -> None:
        print(f"\n{title}\n{line}")

    print(f"\n{'═' * width}")
    print(f"  CEFR level: {a.cefr_level}   (confidence {a.confidence_score:.0%})")
    print("═" * width)

    section("Scores")
    for name, value in a.scores.model_dump().items():
        label = name.replace("_", " ").capitalize()
        print(f"  {label:<16} {value}")

    section("Strengths")
    for s in a.strengths or ["(none)"]:
        print(f"  • {s}")

    section("Corrections")
    if not a.corrections:
        print("  (none)")
    for i, c in enumerate(a.corrections, 1):
        print(f"  {i}. ✗ {c.original}")
        print(f"     ✓ {c.corrected}")
        print(f"     → {c.explanation}")

    section("Improved version")
    print(textwrap.fill(a.improved_version, width, initial_indent="  ", subsequent_indent="  "))
    print()

try:
    model = choose_model()
    print(f"Using deployment: {model}")
    text = get_text()
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )
    openai_client = project.get_openai_client()  # OpenAI-compatible client
    start = time.perf_counter()
    resp = openai_client.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": text},
        ],
        response_format=EnglishWritingAssessment,
    )
    client_total_ms = (time.perf_counter() - start) * 1000
    assessment = resp.choices[0].message.parsed
    if assessment is None:
        print(f"Model refused: {resp.choices[0].message.refusal}")
    else:
        print_assessment(assessment)
    print("Usage:")
    print(f"Tokens: {resp.usage.total_tokens}")
    latency = getattr(resp.usage, "latency_checkpoint", None) or {}
    print(f"Time to first token: {latency.get('user_visible_ttft_ms', 'n/a')} ms")
    print(f"Service total time: {latency.get('service_ttlt_ms', 'n/a')} ms")
    print(f"Client total time: {client_total_ms:.0f} ms")
except KeyError as e:
    print(f"Missing environment variable: {e}")
except Exception as e:
    print(f"Error: {e}")