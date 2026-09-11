from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class MatterAudio(BaseModel):
    matter_id: str = Field(min_length=1)
    client_name: str = Field(min_length=1)
    audio_base64: str = Field(min_length=1)
    audio_format: Literal["wav", "mp3"]
    signed_download_url: HttpUrl


class MatterAction(BaseModel):
    matter_id: str
    transcript: str
    delivery: Literal["send_signed_document", "hold_for_signature"]
    signed_download_url: HttpUrl | None
    deadline: date | None
    follow_up: Literal["schedule_deadline_reminder", "review_for_deadline"]
