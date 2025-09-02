# Adept 🚀

The multi-cloud, context-aware AI agent that lives in your terminal.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#) [![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)](#) [![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](#)

## Visual Demo

<video src="adept/video.mp4" controls autoplay loop muted playsinline width="100%"></video>

If the video does not load, download it: [Adept demo video](adept/video.mp4)

## What is Adept?

Adept is a multi-cloud, context-aware AI orchestrator and intelligent agent for the terminal. It unifies provider-agnostic model access, local-context RAG, and stateful multi-step automation into a single, elegant CLI. With Adept, you can index your codebase, ask grounded questions, chain complex tasks, and fail over between providers—all without leaving your shell.

## Why Adept?

- **Generic LLMs are context-blind**: They don’t know your repo, your stack, or your constraints. Adept builds a local semantic index to inject the right code context at the right moment.
- **APIs change and clouds fail**: Vendor lock-in and outages disrupt work. Adept lets you switch providers on demand with `--provider`, keeping you productive.
- **Real workflows are multi-step**: Hard problems need structured, stateful execution. Adept’s `chain` runs multi-step plans with conversational memory across steps.

## Features

| Feature | What it does | CLI |
|---|---|---|
| **Multi-Cloud Resilience** | First-class support for Gemini and Groq with a unified interface and request shaping. | `--provider gemini|groq` |
| **Intelligent Model Selection** | Human-friendly model aliases mapped to production IDs. | `--model <alias>` |
| **Stateful Workflow Automation** | Execute numbered, multi-step task lists with conversational continuity. | `adept chain execute "1. … 2. … 3. …"` |
| **The "Adept Brain" (Context-Aware RAG)** | Build a LanceDB index over your repo and inject relevant snippets into prompts. | `adept index create` + `--context` |
| **Self-Diagnostics** | Verify provider access and discover available models via the live APIs. | `adept check models -p <provider>` |
| **Premium Terminal UX** | Rich banners, panels, tables, and progress bars for clarity under pressure. | Built with `rich` |

### Providers and Model Aliases

- **Gemini**: `default → gemini-1.5-pro`, `pro → gemini-1.5-pro`, `flash → gemini-1.5-flash`
- **Groq**: `default → llama-3.1-8b-instant`, `llama3-8b → llama-3.1-8b-instant`, `llama3-70b → llama-3.1-70b-versatile`, `mixtral → mixtral-8x7b-32768`, `gemma → gemma2-9b-it`

## Getting Started

```bash
# 1) Clone
git clone https://github.com/yourname/adept-cli.git
cd adept-cli

# 2) (Recommended) Use a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 3) Install
pip install -r requirements.txt

# 4) Configure environment
# Create .env in the project root with your provider keys
cat > .env << 'EOF'
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
EOF

# 5) (Optional but powerful) Index your codebase for RAG
adept index create
```

## Usage

- **Ask with context (RAG-powered)**

```bash
# Ensure you have an index first
adept index create

# Ask a grounded question with your code context
adept write execute "Refactor the data loader for streaming efficiency." \
  --provider groq --model llama3-8b --context
```

- **Run a multi-step chain with memory**

```bash
description='1. Audit the repository for dead code. 2. Propose unit tests for core modules. 3. Draft a CI test matrix.'
adept chain execute "$description" --provider gemini --model flash --context
```

- **Discover models for a provider**

```bash
adept check models --provider groq
```

- **Switch providers and models on demand**

```bash
# Gemini Pro
adept write execute "Summarize the architecture of this project." -p gemini -m pro

# Groq Llama 3.1 70B
adept write execute "Generate a test plan for the indexing module." -p groq -m llama3-70b
```

## A Note on Engineering

Adept was engineered as a production-grade CLI with a clean Typer-based command architecture, rich terminal UX, and robust provider abstractions. Building it meant normalizing divergent chat schemas (Gemini vs. Groq), handling real-world API quirks and auth flows, and designing a resilient model-alias system for rapid iteration. The RAG pipeline indexes your repo with SentenceTransformers (`all-MiniLM-L6-v2`) and LanceDB, then injects the most relevant snippets into prompts via `--context`. The `chain` executor maintains conversational state across steps, enabling complex, stateful workflows. Throughout, I focused on fault-tolerant HTTP, meaningful error surfaces, and a developer experience that feels fast, legible, and dependable under deadline pressure.

## Tech Stack

- **CLI**: Typer
- **Terminal UI**: Rich
- **HTTP**: httpx
- **Config**: python-dotenv
- **Vector DB**: LanceDB
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **Python**: 3.11+

## License

MIT © Contributors
