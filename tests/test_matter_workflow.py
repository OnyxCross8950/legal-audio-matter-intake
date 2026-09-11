from legal_intake.matter_models import MatterAudio
from legal_intake.matter_workflow import MatterWorkflow


class RecordedCall:
    def transcribe(self, matter: MatterAudio) -> str:
        return (
            "The settlement agreement is signed. Send the client their copy. "
            "The filing deadline is 2026-09-14."
        )


def test_signed_matter_is_delivered_and_deadline_is_scheduled() -> None:
    matter = MatterAudio(
        matter_id="MAT-2048",
        client_name="Avery Chen",
        audio_base64="dGVzdCBhdWRpbw==",
        audio_format="wav",
        signed_download_url="https://documents.example/MAT-2048/signed",
    )

    action = MatterWorkflow(RecordedCall()).process(matter)

    assert action.delivery == "send_signed_document"
    assert str(action.signed_download_url) == (
        "https://documents.example/MAT-2048/signed"
    )
    assert action.deadline.isoformat() == "2026-09-14"
    assert action.follow_up == "schedule_deadline_reminder"
