# AI-playground - *Webscraper*


## Background
I wanted to experiment using AI APIs and Python to build a project, and the choice came down to an AI supported web scraper.
I wanted to be able to use different LLMs, but I have set OpenAI as the default. Possible other APIs included in the project (so far) are Ollama and Gemini.

## Requirements to run project

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- If you're not running Ollama locally, you need one or more API keys to fetch content using OpenAI or Gemini

## Get started

```bash
git clone https://github.com/hatron/ai-playground.git
cd ai-playground
uv sync
cp .env.example .env
# Edit your .env file with your API keys or Ollama settings

# Playwright (first time)
uv run playwright install chromium

# Running the Webscraper
uv run python webscraper.py "https://example.com"
uv run python webscraper.py "https://example.com" --provider ollama
uv run python webscraper.py "https://example.com" --provider google
```

See on the top of `webscraper.py` for more CLI-flags (`--render`, `--auto-render` etc.).

## Configuration

- **`env`:** Copy `.env.example` to `.env`. That example file is safe to leave on GitHub; **do not** put any secrets in it!
- **`uv.lock`:** Commit this file for reusable installations (recommended).

## License
GPL-3.0