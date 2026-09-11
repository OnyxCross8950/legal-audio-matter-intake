import re
from datetime import date

from .audio_transcriber import Transcriber
from .matter_models import MatterAction, MatterAudio

DATE_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
SIGNED_PATTERN = re.compile(r"\b(?:is|was|has been) signed\b", re.IGNORECASE)


class MatterWorkflow:
    def __init__(self, transcriber: Transcriber) -> None:
        self._transcriber = transcriber

    def process(self, matter: MatterAudio) -> MatterAction:
        transcript = self._transcriber.transcribe(matter)
        date_match = DATE_PATTERN.search(transcript)
        deadline = date.fromisoformat(date_match.group(1)) if date_match else None
        is_signed = SIGNED_PATTERN.search(transcript) is not None

        return MatterAction(
            matter_id=matter.matter_id,
            transcript=transcript,
            delivery="send_signed_document" if is_signed else "hold_for_signature",
            signed_download_url=matter.signed_download_url if is_signed else None,
            deadline=deadline,
            follow_up=(
                "schedule_deadline_reminder" if deadline else "review_for_deadline"
            ),
        )
