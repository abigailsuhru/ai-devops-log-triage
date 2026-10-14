# AI DevOps Log Triage

A Python-based DevOps log triage assistant using a locally hosted LLM through Ollama.

## Features

- Reads application logs from a local file.
- Uses a local LLM to summarise incidents and suggest investigation steps.
- Returns structured JSON containing severity, summary, likely cause, evidence, and recommended checks.
- Validates required fields and data types.
- Includes unit tests that run without an LLM.

## Requirements

- Python 3.12 or newer
- Git
- Ollama
- The `llama3.2:3b` model

## Setup

Create and activate a virtual environment on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Download the model:

```powershell
ollama pull llama3.2:3b
```

## Run

```powershell
py triage.py sample.log
```

## Test

```powershell
py -m unittest -v
```

## Safety limitations

This is an experimental assistant, not an autonomous incident-response system. Its recommendations may be incorrect. Validation checks output structure, not factual correctness. It has no infrastructure credentials and cannot execute remediation actions.

All initial experiments use synthetic logs and local model inference.