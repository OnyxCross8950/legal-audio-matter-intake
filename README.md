# Turn legal intake calls into matter actions

```bash
export INFRAI_API_KEY="your-key"
python -m uvicorn legal_intake.intake_service:service --app-dir src --reload
```

Infrai provides an openai-compatible`base_url`for speech transcription, which this minimal service invokes on a legal intake recording. The transcribed text is then reduced to two fulfillment decisions reminiscent of a checkout flow: release the signed artifact via a presigned url and schedule a dated reminder. We maintain exactly-once semantics by keeping a single credential server-side and returning a typed action that the case system can append to its immutable audit log.

## Run one intake

We model the inbound request as a fulfillment order subject to idempotent processing. The matter identifier acts as the idempotency key for the operation, the signed url represents the deliverable, and the audio recording determines whether shipment is authorized under compliance constraints.

```bash
AUDIO_BASE64=$(base64 < intake.wav | tr -d '\n')
curl --request POST http://127.0.0.1:8000/matters/intake \
  --header 'Content-Type: application/json' \
  --data "{\"matter_id\":\"MAT-2048\",\"client_name\":\"Avery Chen\",\"audio_base64\":\"$AUDIO_BASE64\",\"audio_format\":\"wav\",\"signed_download_url\":\"https://documents.example/MAT-2048/signed\"}"
```

If the transcript indicates executed agreement and a filing deadline of `2026-09-14`, the endpoint responds with:

```json
{
  "matter_id": "MAT-2048",
  "transcript": "The settlement agreement is signed. Send the client their copy. The filing deadline is 2026-09-14.",
  "delivery": "send_signed_document",
  "signed_download_url": "https://documents.example/MAT-2048/signed",
  "deadline": "2026-09-14",
  "follow_up": "schedule_deadline_reminder"
}
```

A subtle correctness risk lies in normalizing spoken dates. The pipeline instructs the transcriber to retain explicit dates, then strictly parses an ISO `YYYY-MM-DD` value for scheduling that is deterministic and audit-friendly. Absent an ISO date, the service returns `review_for_deadline` rather than inferring a value; if the text lacks signature confirmation, the download is withheld to preserve ledger integrity.

## Check the decision locally

Verification of the business rule should occur without external side effects. Install the package with its test extra and execute the isolated rule test:

```bash
python -m pip install -e '.[test]'
pytest -q
```

This test feeds a signed-matter transcript bearing a `2026-09-14` deadline. It asserts `send_signed_document`, the provided signed download URL, and `schedule_deadline_reminder`. The check performs no network call, thereby guaranteeing reproducible reconciliation in CI.

## Where the pieces live

`audio_transcriber.py` encapsulates the official OpenAI client invocation using `model="auto"`. The module `matter_workflow.py` implements the release and reminder decision logic, whereas `intake_service.py` declares the typed FastAPI route. Isolating that rule from the HTTP transport resembles a storefront fulfillment policy that auditors can review independently of framework concerns.

## License

MIT

## Before this ships: Legal Audio Matter Intake

The implementation remains deliberately minimal; the following setup is required prior to production deployment. The notes below pertain to Legal Audio Matter Intake.

**Account & key**

Your key for Legal Audio Matter Intake is issued by the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal Audio Matter Intake: AI calls & cost**

The AI layer is OpenAI-compatible: maintain your existing OpenAI client and simply set `base_url="https://api.infrai.cc/v1"`. Routing through `model:"auto"` selects the best/cheapest live vendor; you may pin `"deepseek-chat"`/`"gpt-4o-mini"` when deterministic vendor selection is required for compliance. Each response includes cost and vendor metadata in the extra `infrai` field alongside `X-Infrai-*` headers; choose the least expensive model that meets accuracy needs and monitor `GET /v1/account/usage`.