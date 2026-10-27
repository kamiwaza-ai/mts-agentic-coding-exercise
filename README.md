# Kamiwaza MTS agentic coding exercise

This exercise helps us understand how you work with a coding agent on an unfamiliar
repository. We care about the decisions you make, the context and constraints you give the
agent, how you inspect its work, and how you verify the result. A polished final implementation
without a clear working process gives us less useful evidence than a thoughtful, visible process.

The repository contains a working local job queue and a feature request in [`TASK.md`](TASK.md).
The feature is intentionally incomplete. You will design and implement as much of it as you can
while explaining your work.

## Recording requirements

The recording is a required part of the exercise and is the primary evidence we use to understand
your working process. Record your **entire screen**, not only one application or window, and keep
your **camera and microphone on for the full working session**. We need to see the coding agent,
prompts and responses, terminal commands, code changes, tests, and corrections while hearing you
explain the decisions you make.

- Start recording before you clone or open the repository.
- Keep your entire screen, camera, and microphone visible and active throughout the exercise.
- Keep the recording continuous whenever possible. Do not edit it into a presentation.
- If recording fails, resume immediately in a clearly numbered second segment and explain what
  happened.

## Time limit

- Aim for **60 minutes** of recorded work. You may use up to **90 minutes**.
- Upload time is separate and does not count toward the limit.

Before recording, you may install and authenticate your tools, configure screen recording, and
close personal or confidential applications. Use a clean desktop and take care not to display
credentials, private source code, or personal information.

## Working with coding agents

Use the coding agent, editor, terminal, and supporting documentation you normally prefer. Web
research is allowed when it is visible in the recording. Human assistance is not allowed.

Keep the complete agent interaction visible. Talk through:

- how you set up the agent and give it repository context;
- how you frame the problem, constraints, and plan;
- what you delegate and what you retain;
- how you inspect and challenge generated changes;
- how code, tests, or other evidence changes your direction; and
- how you decide the implementation is ready to demonstrate.

The application you build must run locally without calling an LLM, paid API, or external service.
Using an LLM-backed coding agent during development is expected.

## Suggested schedule

- **5–10 minutes:** introduce your tools, agent setup, instruction files, and workflow.
- **35–60 minutes:** understand the repository, design, implement, inspect, test, and correct.
- **10–15 minutes:** demonstrate the result and answer the reflection questions below.

Stop at 90 minutes even if the feature is incomplete. Explain what remains and what you would do
next.

## Setup

You need Python 3.11 or later.

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
python -m jobqueue.demo --database demo.db
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

All baseline tests should pass before you begin the feature. [`TASK.md`](TASK.md) is the source of
truth for the required behavior. [`docs/current-design.md`](docs/current-design.md) explains the
existing implementation and operational context.

## What to submit

Upload the following to the private Google Drive folder in your invitation:

1. The complete recording, or clearly numbered recording segments if capture failed.
2. A ZIP of the completed repository, including the completed [`NOTES.md`](NOTES.md).

Create the ZIP from the repository's text source, tests, documentation, and configuration files.
Do not include `.git`, `.venv`, caches, build output, dependency directories, nested archives,
executables or compiled files, HTML/SVG/Office/PDF files, credentials, API keys, personal files, or
unrelated source code. We review the submitted source statically and use the recording as evidence
of the behavior you observed, so installers and runnable binaries are neither needed nor accepted.

Do not open a pull request or publish your solution. Your recording and code will be available only
to the hiring team and will be deleted 90 days after the final decision on your application.

Please complete the exercise within one week of receiving the invitation. If you have a technical
problem or would like to speak with us before starting, reply to the invitation email.

## End-of-recording reflection

Before stopping the recording, answer these questions:

1. Which agent-generated change did you most carefully inspect, change, or reject? Why?
2. What evidence gives you confidence in the behavior you implemented?
3. What important limitation or risk remains?
4. What would you change for durable production storage or multiple service instances?
5. What would you do next with another hour?
