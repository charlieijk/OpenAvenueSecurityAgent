This Assignment 1 experiment sends one defensive cybersecurity example to
Gemini per execution, records a prediction before the request, and saves the
actual prompt and response for assessment. It includes three synthetic inputs,
environment-based key handling, disabled automatic retries, and an independent
SQLite parameter-binding check.

The interactive loopback demo lets a reviewer inspect all three inputs and exact
prompts, write a prediction, download a draft plan, execute the real local SQLite
check, and load a completed experiment record locally in the browser. The README
includes a capture of the actual demo and setup instructions. No Gemini response
is fabricated or bundled.

Live Gemini runs, response assessments, instructor invitation/review and Slack
sharing remain pending. Keep this PR as a draft. Instructor approval is required
before merging.

Validation: seven offline tests, local SQLite binding check, prompt preview and
demo JavaScript syntax check passed. Browser checks cover input/prompt tabs and
the local verification result. Zero live Gemini calls were made.
