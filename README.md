<div align="center">

<h1>🔥 ADEPT — The AI Engineer's Workflow Orchestrator</h1>

<p>
  <em>Lightning-fast, context-aware, multi-cloud terminal agent. Build, reason, and ship without leaving your shell.</em>
</p>

<p>
  <a href="#"><img alt="MIT" src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" /></a>
  <a href="#"><img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?style=for-the-badge&logo=python&logoColor=white" /></a>
  <a href="#"><img alt="Typer" src="https://img.shields.io/badge/CLI-Typer-0A7ACA?style=for-the-badge" /></a>
  <a href="#"><img alt="Rich" src="https://img.shields.io/badge/Terminal-Rich-CA0B4A?style=for-the-badge" /></a>
  <a href="#"><img alt="Gemini" src="https://img.shields.io/badge/Provider-Gemini-1f6feb?style=for-the-badge" /></a>
  <a href="#"><img alt="Groq" src="https://img.shields.io/badge/Provider-Groq-111111?style=for-the-badge" /></a>
</p>

</div>

---

## 🎬 Visual Demo

<video src="adept/video.mp4" controls autoplay loop muted playsinline width="100%"></video>

If the video does not load, download it: [Adept demo video](adept/video.mp4)

---

## ✨ What is Adept?

Adept is a context-aware AI orchestrator designed for real work in real repos. It unifies provider-agnostic model access (Gemini, Groq), local semantic indexing (RAG), and stateful multi-step automation into a single, elegant CLI.

- Index your codebase and ask grounded questions.
- Chain complex tasks with memory across steps.
- Fail over between providers without changing your workflow.

> Adept is engineered to be resilient, legible, and fast under deadline pressure.

---

## ⚡️ Highlights

- Multi-cloud by design — switch between Gemini and Groq with a flag.
- Model aliases that map to production-ready IDs you actually want to use.
- Context-aware RAG over your repo via LanceDB + SentenceTransformers.
- Statefully execute numbered task chains with conversation memory.
- First-class terminal UX: banners, panels, tables, progress bars.

### Supported Providers & Aliases

- Gemini: `default → gemini-1.5-pro`, `pro → gemini-1.5-pro`, `flash → gemini-1.5-flash`
- Groq: `default → llama-3.1-8b-instant`, `llama3-8b → llama-3.1-8b-instant`, `llama3-70b → llama-3.1-70b-versatile`, `mixtral → mixtral-8x7b-32768`, `gemma → gemma2-9b-it`

---

## 🚀 Quickstart

```bash
# 1) Clone
git clone https://github.com/yourname/adept-cli.git
cd adept-cli

# 2) (Recommended) Virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 3) Install dependencies (choose one)
# a) If you have a requirements file
pip install -r requirements.txt
# b) Or install the essentials directly
pip install "typer[all]" rich httpx python-dotenv lancedb sentence-transformers

# 4) Configure environment
cat > .env << 'EOF'
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
EOF

# 5) Build a local code index (optional but powerful)
python -m adept.main index create
```

---

## 🧭 Usage Cheat Sheet

You can use the module entrypoint or an installed console script. Below examples use the module form for portability.

- Ask with context (RAG-powered)

```bash
# Ensure an index exists first
python -m adept.main index create

# Ask a grounded question with code context
python -m adept.main write execute "Refactor the data loader for streaming efficiency." \
  --provider groq --model llama3-8b --context
```

- Run a multi-step chain with memory

```bash
description='1. Audit the repository for dead code. 2. Propose unit tests for core modules. 3. Draft a CI test matrix.'
python -m adept.main chain execute "$description" --provider gemini --model flash --context
```

- Discover models available to your key

```bash
# Gemini
python -m adept.main check models --provider gemini
# Groq
python -m adept.main check models --provider groq
```

- Switch providers/models on demand

```bash
# Gemini Pro
python -m adept.main write execute "Summarize the architecture of this project." -p gemini -m pro

# Groq Llama 3.1 70B
python -m adept.main write execute "Generate a test plan for the indexing module." -p groq -m llama3-70b
```

---

## 🧠 How it Works (High Level)

- CLI & UX: Typer for command structure; Rich for expressive, readable TUI.
- Providers: Normalized request/response across Gemini and Groq.
- RAG: Index your repo with SentenceTransformers (`all-MiniLM-L6-v2`) into LanceDB, retrieve top chunks, and prepend as grounded context.
- Chains: Maintain conversation history across steps for continuity and reasoning.

---

## 🔐 Environment & Secrets

Create a `.env` file at the project root:

```bash
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
```

Tips:
- Never echo secrets in terminals or commit them to git.
- Use provider-specific billing/quota dashboards to increase limits when needed.

---

## 🧰 Troubleshooting

- 429 Quota Exceeded (Gemini): Slow down request rate, switch to a lighter model (e.g., `flash`), or request higher quota. You can verify access with:

```bash
python -m adept.main check models --provider gemini
```

- No index found: Run the indexer first.

```bash
python -m adept.main index create
```

- Invalid API key: Ensure your `.env` file exists and is loaded in the shell where you run the commands.

---

## 🏗️ Tech Stack

- CLI: Typer
- Terminal UI: Rich
- HTTP: httpx
- Config: python-dotenv
- Vector DB: LanceDB
- Embeddings: SentenceTransformers (`all-MiniLM-L6-v2`)
- Python: 3.11+

---

## 📜 License

MIT © Contributors
