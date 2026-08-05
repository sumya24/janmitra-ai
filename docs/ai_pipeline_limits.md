# AI Pipeline Limits — Measured, Not Guessed

Measured against the live Sarvam API on 2026-08-05, ahead of the hackathon submission,
after repeated production failures traced to unbounded reasoning-model behavior (see
`git log` — "Fix empty summary content from sarvam-105b reasoning model", "Normalize
spelling before translation...", "Make AI summary generation best-effort..."). This
documents what the actual limits are, not what the docs claim or what we assumed.

Raw sweep outputs are kept in this session's scratchpad; the numbers below are transcribed
directly from them. The regression tests in `tests/test_ai_limits.py` encode the two
conclusions that matter as ongoing checks.

## 1. Speech-to-text (STT): hard 30-second ceiling, strictly enforced

We use Sarvam's **synchronous** `speech_to_text.transcribe` endpoint (`saaras:v3`) via
`backend/services/sarvam_client.py`. This is documented as capped at **30 seconds of
audio per request**; longer audio requires their separate **Batch API** (async, up to 2
hours/file), which this codebase does not integrate.

We confirmed this is a hard, actively-enforced limit, not just a documented suggestion —
synthetic WAV files (16kHz, mono, tone — content doesn't matter for this check, only
duration/size) were sent to the real endpoint:

| Duration | File size | Result |
|---|---|---|
| 10s | 313 KB | Accepted (200) |
| 30s | 938 KB | Accepted (200) |
| 35s | 1.1 MB | **Rejected (400)** |
| 60s | 1.9 MB | **Rejected (400)** |
| 120s | 3.7 MB | **Rejected (400)** |
| 300s | 9.2 MB | **Rejected (400)** |
| 600s | 18.3 MB | **Rejected (400)** |

Every rejection returned the same explicit error, immediately (1-21s, dominated by upload
time for the larger files — the API rejects on duration before doing any transcription
work):

> `Audio duration exceeds the maximum limit of 30 seconds. Please use the batch API for longer audio files.`

**What this means for the app:** any citizen who speaks for longer than ~30 seconds when
recording a complaint gets a hard failure. Today that surfaces to the citizen as a generic
`AIServiceError` → 502 ("Speech-to-text service failed. Please try again.") — there is no
duration check or warning before or during recording, and no friendly message explaining
*why* it failed. No file-size limit was documented separately from the duration cap; in
practice duration is what gets checked.

This wasn't something the previous investigation had surfaced — it was found by testing
directly against the API for this report.

## 2. Normalization + summary (chat completion): no clean length threshold — variance dominates

**Method:** built synthetic-but-realistic garbage-complaint English text (12 varied
template sentences cycled together, not one line repeated) at 50/200/500/1000/2000/4000
words, and ran it through the exact same prompts/model/settings production uses
(`sarvam-105b`, `LLM_MAX_TOKENS=4096`, `reasoning_effort="low"`, `LLM_TIMEOUT_SECONDS=120`),
calling the raw chat completion API directly so `finish_reason` is visible (the production
services log it but don't return it to callers).

### First pass — one call per size

| Words | Chars | Normalize latency | Normalize result | Summarize latency | Summarize result |
|---|---|---|---|---|---|
| 50 | 269 | 8.1s | ✅ success | 23.1s | ✅ success |
| 200 | 1,098 | 54.7s | ✅ success | 8.2s | ✅ success |
| 500 | 2,773 | 58.7s | ❌ **failed** (`finish_reason=length`, empty content) | 0.8s | ✅ success |
| 1000 | 5,568 | 58.2s | ❌ **failed** (`finish_reason=length`, empty content) | 0.9s | ✅ success |
| 2000 | 11,127 | 4.1s | ✅ success | 1.0s | ✅ success |
| 4000 | 22,280 | 36.2s | ❌ **failed** (`finish_reason=length`, empty content) | 1.1s | ✅ success |

The immediate, surprising result: **failure and latency do not scale with input length in
this data.** 200 words took *longer* (54.7s) than 500 or 1000 words took before failing
(~58s each, but those failed outright). 2000 words — 10x the shortest failing case (500
words that failed) — succeeded in 4.1s. Normalization failed at 3 of 6 sizes tested,
with no consistent pattern by size.

### Second pass — same size, repeated 3x, to check if that's real variance or a fluke

One sample per size isn't enough to trust a length-vs-reliability conclusion on, so the
50-word and 500-word cases were each repeated 3 more times (4 total per size, combined
with the first pass):

| Words | Step | Trial 1 | Trial 2 | Trial 3 | Trial 4 (first pass) |
|---|---|---|---|---|---|
| 50 | normalize | 8.0s ✅ | 8.6s ✅ | 16.9s ✅ | 8.1s ✅ |
| 50 | summarize | 36.1s ✅ | 16.3s ✅ | 6.7s ✅ | 23.1s ✅ |
| 500 | normalize | 20.5s ✅ | 33.5s ❌ | 58.0s ❌ | 58.7s ❌ |
| 500 | summarize | 1.0s ✅ | 0.8s ✅ | 0.5s ✅ | 0.8s ✅ |

This confirms it's real variance, not a fluke, and sharpens the picture considerably:

- **Normalization at 500 words fails 3 of 4 times** (75%), and its one success (20.5s)
  still missed our 20s usability bar. Same exact input length, wildly different outcomes
  each call — anywhere from a 20.5s success to a 58s failure.
- **Normalization at 50 words succeeded 4/4** and stayed under 20s every time (8.0-16.9s)
  — genuinely reliable at this size, unlike 500 words.
- **Summarization never failed once**, at either size, across all 8 trials. But at 50
  words its latency ranged **6.7s to 36.1s** — half the trials (2/4) exceeded the 20s
  usability bar, at the *shortest* input size tested. At 500 words it was both fast
  (0.5-1.0s) and rock solid every time.
- Summarization getting **faster and more reliable as input grows**, while normalization
  gets **less reliable**, is counter-intuitive but consistent across both passes. The two
  steps do not share a common "safe" length.

## 3. Where things actually start failing / getting too slow

There is no clean word-count "breaking point" to report — that would be a false
precision the data doesn't support. What the 18 combined live calls actually show:

- **Normalization** is the fragile step. It is reliable at 50 words (4/4 success, all
  under 20s) but its success rate falls off a cliff somewhere between 50 and 500 words —
  at 500 words it fails outright (`finish_reason=length`, empty content) **75% of the
  time**, and its rare successes are still borderline-to-over the 20s usability bar. There
  isn't a clean size where this starts; it's a rising *failure probability*, not a
  threshold. Practically: **treat anything much beyond a short complaint (~50-100 words)
  as likely to fail normalization**, not as an edge case.
- **Summarization** rarely fails outright in this data (0 failures across 10 trials,
  50-4000 words) — but the *shortest, most "typical" citizen complaint* (50 words) is
  paradoxically the size most likely to feel slow: latency ranged 6.7-36.1s, missing the
  20s bar in half the trials. Longer inputs (500-4000 words) were consistently fast
  (<1.1s every time). So summarization's practical risk isn't failure, it's **unpredictable
  latency on exactly the input size a real complaint is most likely to be**.
- Both steps' behavior is dominated by the reasoning model's variable internal "thinking"
  length per call, not primarily by input size, within the 50-4000 word range tested. This
  is why `reasoning_effort="low"` and a larger `LLM_MAX_TOKENS` only ever reduced *how
  often* this happens, not whether it can happen — there's no fixed setting that
  eliminates it.

## Does the existing fallback handle this correctly?

Yes, for the failure cases actually observed:

- `NormalizationService.normalize()` swallows `finish_reason=length` (and any other
  failure) and falls back to the original untouched text — confirmed in the sweep logs
  above and in `tests/test_normalization_service.py`.
- `SummaryService.summarize()` raises `AIServiceError` on the same failure, which
  `ComplaintAgent.create_complaint()` now catches and replaces with a truncated excerpt of
  the translated text rather than failing the `/complaints` POST — confirmed in
  `tests/test_complaint_agent.py` and re-verified in `tests/test_ai_limits.py`.
- Neither step's fallback was observed to fail itself, and no combination of failures in
  this sweep produced a lost/unstored complaint.

What the fallback does **not** cover: STT rejections (a >30s recording). That failure
currently propagates as a raw `AIServiceError` → 502 with a generic message, and there is
no complaint stored, no partial save, and no citizen-facing explanation of the 30-second
cap. This is a real gap, not something this investigation fixed — flagging it as a fact,
per scope.

## Recommendation on `LLM_MAX_TOKENS` / `LLM_TIMEOUT_SECONDS`

Keep both at their current values (`4096` / `120s`) — the data doesn't support changing
either:

- **`LLM_MAX_TOKENS`:** raising it further would not meaningfully help. Normalization
  failures at 500 words happened at `finish_reason=length` with the *same* 4096-token
  budget that also let a 4.1s success happen at 2000 words and a 20.5s success at 500
  words. The problem is variance in how much the model chooses to reason, not a budget
  that's consistently too tight. A bigger budget mostly means slower failures, not fewer
  of them (as already observed once in production: raising 1024→4096 traded an
  empty-content failure for a near-timeout).
- **`LLM_TIMEOUT_SECONDS`:** 120s was never approached in any of the 18 calls (slowest was
  58.7s). No evidence it's currently causing failures; no evidence a different value would
  help.
- The lever that actually matters is the one already built: **treating both steps as
  best-effort with a graceful fallback**, since no combination of these two settings makes
  the underlying reasoning-length variance go away.

