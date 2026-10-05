# OpenAvenueSecurityAgent

Assignment 1 for my AI Security Agents coursework: make a first Gemini API call
with Python and `google-genai`, then compare responses to three defensive
cybersecurity inputs. This assignment makes one request per execution and does
not implement an agent or execute the model's suggestions.

## Current status

The private [GitHub repository](https://github.com/charlieijk/OpenAvenueSecurityAgent)
and [draft PR #1](https://github.com/charlieijk/OpenAvenueSecurityAgent/pull/1) are
created. **Live Gemini runs, response assessments, instructor invitation/review,
and Slack sharing are pending.** Offline checks are not evidence of a successful
Gemini request. Coding assistance was
used to prepare this starter; I should understand the code, adapt the examples,
and write my own expectations and reflection.

## How an API call works

The client sends a model name and prompt to Google's service, authenticating
with an API key read from the environment. Gemini returns generated content and
metadata. The script prints the response and saves a record so I can compare it
with my prediction. Generated text is a claim to evaluate, not proof that the
model executed the example or checked its security.

## Setup

Use Python 3.10 or newer. From this repository folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Read the [Gemini quickstart](https://ai.google.dev/gemini-api/docs/generate-content/get-started)
and [API key guide](https://ai.google.dev/gemini-api/docs/api-key), then create a
key in [Google AI Studio](https://aistudio.google.com/apikey).

In a macOS zsh terminal, enter the key with hidden input so its value is not in
shell history:

```sh
read -s 'GEMINI_API_KEY?Paste your Gemini API key (hidden): '
export GEMINI_API_KEY
```

Press Enter after pasting. The variable lasts for this terminal session. Do not
paste the key into chat, code, README, or Git. `.env` files, local environments,
and common credential files are ignored by Git; the script does not load `.env`.
After running, `unset GEMINI_API_KEY` removes the variable from the session.

The default is `gemini-3.8-flash`, listed with free-tier input and output on
Google's [pricing page](https://ai.google.dev/gemini-api/docs/pricing), checked
October 5, 2026. Confirm that your project has free-tier quota for it in AI
Studio before running. A listed free tier does not prove that your particular
project has remaining quota. No paid upgrade is needed. To use another eligible
model, pass its exact model ID with `--model`.

## Three experiments

All inputs are synthetic. Only the selected case is sent to Gemini; no real
logs, repository contents, or credentials are included in the prompt.

| Case | Input | Question to consider before running |
| --- | --- | --- |
| `bound-query` | A SQLite query with a bound username value | Will Gemini recognize binding while avoiding claims about authentication? |
| `web-config` | Production-intended web configuration | Will it identify settings to change without inventing deployment details? |
| `login-log` | Two failed logins and a later success | Will it distinguish a reason to investigate from proof of compromise? |

Inspect the exact prompt without making an API call:

```sh
python experiment.py --case bound-query --preview
```

Review or adapt `cases.json`, then write your own expectation **before** each
run. Start with one request. The following prediction is an example to edit:

```sh
python experiment.py --case bound-query --expectation "I expect parameter binding to be recognized, but authentication cannot be assessed from this function alone."
```

After reviewing that response, run the other cases with your own predictions:

```sh
python experiment.py --case web-config --expectation "Write my prediction here before running."
python experiment.py --case login-log --expectation "Write my prediction here before running."
```

Do not use the placeholder predictions as your submitted work. Each execution
makes at most one generation request; there are no automatic retries or batch
runs. HTTP 429 means stop and check [your active rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
in AI Studio. Wait for the applicable limit to reset rather than repeatedly
calling or enabling billing. Other failures are recorded without printing
provider error details that might expose a credential.

## Record responses and assess them

Each live attempt produces a distinct JSON file in `runs/`. Before the request,
it saves the input, exact prompt, requested model, SDK version, settings, and
your expectation. Afterward, it saves the actual response and metadata or the
failure status. A response with no text is marked separately and is not treated
as a successful experiment. Do not replace actual results with sample answers.

Fill in `reflection_after_run` in each record, then summarize all three runs in
[REFLECTION.md](REFLECTION.md). Identify what Gemini got right, missed, or claimed
without evidence. Keep the raw response unchanged and put your assessment in the
reflection fields.

Check at least one actual claim independently:

```sh
python verify_claim.py
```

This local SQLite check confirms how a normal quoted name is bound as a value.
Compare an actual claim in Gemini's `bound-query` response with this result and
the [Python documentation](https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders).
It does not prove whole-application security. Record the exact claim, your
verdict, and evidence in the reflection.

## GitHub workflow

Local `main` starts with only the introductory README and Python `.gitignore`.
Code and the expanded documentation are on `assignment-1-gemini`.

After the three actual runs and reflections are ready, inspect the files before
committing. Authenticate the GitHub CLI if needed:

```sh
gh auth login --hostname github.com --web --git-protocol https
git add experiment.py cases.json verify_claim.py requirements.txt requirements-lock.txt tests README.md REFLECTION.md runs
git commit -m "Record three Gemini security experiments and reflections"
```

The repository and draft PR already exist. Push new experiment records to the
assignment branch; do not create another repository or PR:

```sh
git push origin assignment-1-gemini
```

Update `PR_DESCRIPTION.md` with the actual completed results and use that text
to update the existing PR. Invite the instructor and request review when ready:

```sh
gh api --method PUT repos/charlieijk/OpenAvenueSecurityAgent/collaborators/edsioufi -f permission=push
gh pr edit 1 --body-file PR_DESCRIPTION.md
gh pr ready 1
```

The instructor may need to accept the collaborator invitation before a review
request is possible. Once accepted:

```sh
gh pr edit --add-reviewer edsioufi
```

Do not merge until the instructor reviews and approves the PR.

## Slack checklist

- Add a profile picture in the course workspace.
- Create a public project channel named `#p_charlie_cullen`.
- Post the repository link and pin that message.
- Post the PR link before the next workshop and ask the instructor for review.
- Use the channel for progress, questions, and feedback.

## Offline checks

```sh
python -m unittest discover -s tests -v
python verify_claim.py
```

The tests use mocked responses and never contact Gemini. `requirements.txt`
pins the SDK; `requirements-lock.txt` records the complete verified dependency
versions. To reproduce that environment, install from the lock file instead.
