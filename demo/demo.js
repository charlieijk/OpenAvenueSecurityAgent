"use strict";
const titles = {"bound-query": ["Bound SQL query", "Code review · separate binding from authentication"], "web-config": ["Production configuration", "Configuration review · identify what is missing"], "login-log": ["Authentication log", "Evidence review · investigate without overclaiming"]};
const byId = (id) => document.getElementById(id);
const expectations = new Map();
const records = new Map();
let cases = [];
let selected;
let checkResult;

function showTab(name) {
  for (const kind of ["input", "prompt", "response"]) {
    byId(`${kind}-tab`).setAttribute("aria-selected", String(kind === name));
    byId(`${kind}-tab`).tabIndex = kind === name ? 0 : -1;
    byId(`${kind}-panel`).hidden = kind !== name;
  }
}

function displayRecord() {
  const panel = byId("recorded-response");
  panel.replaceChildren();
  const record = records.get(selected.id);
  if (!record) {
    const heading = document.createElement("h3");
    heading.textContent = "No recorded response loaded";
    const text = document.createElement("p");
    text.textContent = "Run experiment.py with your own expectation and a free-tier Gemini key, then load its JSON record here.";
    panel.append(heading, text);
    return;
  }
  for (const [label, content] of [[`Recorded Gemini response · ${record.model_requested}`, record.response_text], ["Expectation before the run", record.expectation_before_run], ["Reflection after the run", JSON.stringify(record.reflection_after_run ?? {}, null, 2)]]) {
    const heading = document.createElement("h3");
    heading.textContent = label;
    const body = document.createElement("pre");
    body.textContent = content;
    panel.append(heading, body);
  }
}

function choose(item) {
  if (selected) expectations.set(selected.id, byId("expectation").value);
  selected = item;
  byId("case-title").textContent = titles[item.id][0];
  byId("case-number").textContent = `EXPERIMENT 0${cases.indexOf(item) + 1}`;
  byId("case-input").textContent = item.input;
  byId("exact-prompt").textContent = item.prompt;
  byId("prediction-question").textContent = item.prediction_questions;
  byId("expectation").value = expectations.get(item.id) ?? "";
  byId("verification").hidden = item.id !== "bound-query";
  byId("verification-result").textContent = checkResult ?? "Not run yet.";
  byId("record-error").textContent = "";
  for (const button of byId("cases").querySelectorAll("button")) button.setAttribute("aria-pressed", String(button.dataset.case === item.id));
  displayRecord();
  showTab("input");
}

for (const kind of ["input", "prompt", "response"]) {
  byId(`${kind}-tab`).addEventListener("click", () => showTab(kind));
  byId(`${kind}-tab`).addEventListener("keydown", (event) => {
    const names = ["input", "prompt", "response"];
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const index = names.indexOf(kind);
    const next = event.key === "Home" ? 0 : event.key === "End" ? 2 : (index + (event.key === "ArrowRight" ? 1 : 2)) % 3;
    showTab(names[next]);
    byId(`${names[next]}-tab`).focus();
  });
}

byId("download-plan").addEventListener("click", () => {
  if (!selected) return;
  const expectation = byId("expectation").value.trim();
  if (!expectation) { byId("status").textContent = "Write an expectation before downloading a plan."; byId("expectation").focus(); return; }
  const plan = {case: selected.id, expectation_before_run: expectation, input: selected.input, prompt: selected.prompt, status: "plan_only_no_model_request"};
  const url = URL.createObjectURL(new Blob([JSON.stringify(plan, null, 2)], {type:"application/json"}));
  const link = document.createElement("a");
  link.href = url;
  link.download = `${selected.id}-experiment-plan.json`;
  link.click();
  URL.revokeObjectURL(url);
  byId("status").textContent = "Experiment plan downloaded. No Gemini request was made.";
});

byId("verify").addEventListener("click", async () => {
  const button = byId("verify");
  button.disabled = true;
  byId("verification-result").textContent = "Running local SQLite check…";
  try {
    const response = await fetch("/api/verify-sqlite", {method:"POST"});
    if (!response.ok) throw new Error("Local check unavailable");
    const result = await response.json();
    checkResult = `PASS · ${result.claim}\nQueried: ${result.queried_username}\nReturned: ${JSON.stringify(result.returned_row)}\nRows still present: ${result.remaining_rows}\n\n${result.scope}\n${result.reference}`;
    byId("verification-result").textContent = checkResult;
  } catch { byId("verification-result").textContent = "The local check failed. Check the terminal and try again."; }
  finally { button.disabled = false; }
});

byId("record-file").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  try {
    if (file.size > 1024 * 1024) throw new Error("Choose a run record smaller than 1 MiB.");
    const record = JSON.parse(await file.text());
    const item = cases.find((entry) => entry.id === record.case);
    if (!item || record.status !== "completed" || typeof record.response_text !== "string" || !record.response_text.trim() || typeof record.expectation_before_run !== "string" || typeof record.model_requested !== "string" || typeof record.prompt !== "string" || record.input !== item.input || record.prompt !== item.prompt) throw new Error("Load a completed experiment record matching one of these exact examples and prompts.");
    records.set(item.id, record);
    choose(item);
    showTab("response");
    byId("status").textContent = "Loaded a local run record. Its response is recorded model output, not a verified security verdict.";
  } catch (error) { byId("record-error").textContent = error instanceof Error ? error.message : "Could not load this record."; }
  event.target.value = "";
});

async function initialize() {
  try {
    const response = await fetch("/api/cases");
    if (!response.ok) throw new Error("Examples unavailable");
    cases = (await response.json()).cases;
    byId("cases").replaceChildren();
    for (const [index, item] of cases.entries()) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "case-button";
      button.dataset.case = item.id;
      const number = document.createElement("span");
      number.textContent = `0${index + 1} / DEFENSIVE EXAMPLE`;
      const title = document.createElement("strong");
      title.textContent = titles[item.id][0];
      const subtitle = document.createElement("small");
      subtitle.textContent = titles[item.id][1];
      button.append(number, title, subtitle);
      button.addEventListener("click", () => choose(item));
      byId("cases").append(button);
    }
    choose(cases[0]);
  } catch { byId("status").textContent = "Examples could not load. Start demo.py from the repository and refresh this page."; }
}
initialize();
