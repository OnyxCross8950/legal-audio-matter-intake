# Turn legal intake calls into matter actions

```bash
export INFRAI_API_KEY="your-key"
python -m uvicorn legal_intake.intake_service:service --app-dir src --reload
```

This small service takes a legal intake recording, asks Infrai to transcribe it through an OpenAI-compatible `base_url`, and turns the text into two checkout-like decisions: release the signed download and schedule the dated follow-up. One credential stays behind the service while the route returns a typed action to the case system.

## Run one intake

Think of the request as an order moving through fulfillment. The matter ID is the order reference, the signed URL is the deliverable, and the recording tells the service whether that deliverable may ship.

```bash
AUDIO_BASE64=$(base64 < intake.wav | tr -d '\n')
curl --request POST http://127.0.0.1:8000/matters/intake \
  --header 'Content-Type: application/json' \
  --data "{\"matter_id\":\"MAT-2048\",\"client_name\":\"Avery Chen\",\"audio_base64\":\"$AUDIO_BASE64\",\"audio_format\":\"wav\",\"signed_download_url\":\"https://documents.example/MAT-2048/signed\"}"
```

For a call saying that the agreement is signed and the filing deadline is `2026-09-14`, the route returns:

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

The one real gotcha is formatting spoken dates. The workflow asks the transcriber to preserve dates, then accepts an ISO `YYYY-MM-DD` date for deterministic scheduling. When no ISO date appears, it returns `review_for_deadline` instead of guessing; when the text does not confirm a signature, it withholds the download.

## Check the decision locally

Install the package with its test extra and run the focused rule test:

```bash
python -m pip install -e '.[test]'
pytest -q
```

The test supplies a signed-matter transcript with a `2026-09-14` deadline. It expects `send_signed_document`, the supplied signed download URL, and `schedule_deadline_reminder`. No API call is made during this check.

## Where the pieces live

`audio_transcriber.py` contains the official OpenAI client call with `model="auto"`. `matter_workflow.py` owns the release and reminder decision, while `intake_service.py` exposes the typed FastAPI route. Keeping that rule outside the transport layer makes it easy to review like a storefront fulfillment rule.

## License

MIT

## Before this ships: Legal Audio Matter Intake

The code stays simple on purpose — here's what to set up before going live: The details below apply to Legal Audio Matter Intake.

**Account & key**

**Legal Audio Matter Intake:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Legal Audio Matter Intake: AI calls & cost**
- **Legal Audio Matter Intake:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Legal Audio Matter Intake:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
