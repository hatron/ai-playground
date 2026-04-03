# AI-playground - Webscraper

Experimenting with a Python AI supported web scraper using different LLMs.

## Requirements to run project

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Get started

```bash
git clone <https://github.com/hatron/ai-playground.git>
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
Not yet set