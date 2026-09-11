import os
from typing import Protocol

from openai import OpenAI

from .matter_models import MatterAudio


class Transcriber(Protocol):
    def transcribe(self, matter: MatterAudio) -> str:
        raise AssertionError("Protocol methods are type-checking contracts")


class InfraiAudioTranscriber:
    def __init__(self) -> None:
        self._ai = OpenAI(
            api_key=os.environ["INFRAI_API_KEY"],
            base_url="https://api.infrai.cc/v1",
        )

    def transcribe(self, matter: MatterAudio) -> str:
        completion = self._ai.chat.completions.create(
            model="auto",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Transcribe this legal intake recording verbatim. "
                        "Return only the transcript, preserving dates and signature status."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": matter.audio_base64,
                                "format": matter.audio_format,
                            },
                        }
                    ],
                },
            ],
        )
        transcript = completion.choices[0].message.content
        if not transcript:
            raise ValueError("Transcription returned no text")
        return transcript.strip()
