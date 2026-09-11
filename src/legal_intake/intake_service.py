from fastapi import FastAPI

from .audio_transcriber import InfraiAudioTranscriber
from .matter_models import MatterAction, MatterAudio
from .matter_workflow import MatterWorkflow

service = FastAPI(title="Legal audio matter intake")


@service.post("/matters/intake", response_model=MatterAction)
def intake_matter(matter: MatterAudio) -> MatterAction:
    workflow = MatterWorkflow(InfraiAudioTranscriber())
    return workflow.process(matter)
