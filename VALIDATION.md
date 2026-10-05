# Local validation — October 5, 2026

Environment: Python 3.12.14; `google-genai` 2.28.0; exact installed dependency
versions captured in `requirements-lock.txt`.

- Four offline tests passed using the real SDK with a mocked HTTP transport:
  preview does not send a request; a missing key does not send a request;
  prediction is saved before the mocked successful request; a mocked HTTP 429
  makes exactly one attempt and does not retry or save the secret error text.
- The independent in-memory SQLite binding check passed.
- Prompt preview succeeded without a Gemini request.
- Git ignores `.env`, `.env.local`, local environments, and common credential files.

**Zero live Gemini calls were made.** These checks verify local behavior, not
model availability, account quota, model output quality, or assignment completion.
