# AI-playground - *Webscraper*


## Background
I wanted to experiment using AI APIs and Python to build a project, and the choice came down to an AI supported web scraper.
I wanted to be able to use different LLMs, but I have set OpenAI as the default. Possible other APIs included in the project (so far) are Ollama and Gemini.

## Requirements to run project

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- If you're not running Ollama locally, you need one or more API keys to fetch content using [OpenAI](https://www.openai.com) or [Gemini](https://gemini.google.com/)

I find it really easy using _Ollama_ for this kind of work. Visit their website to [learn more about Ollama](https://ollama.com/).

## Get started

```bash
git clone https://github.com/hatron/ai-playground.git
cd ai-playground/webscraper
uv sync
cp .env.example .env
# Edit your .env file with your API keys or Ollama settings
```
The first time, you need to install chromium for Playwright

```bash
# Playwright (first time)
uv run playwright install chromium
```

To run the Webscraper, choose if you want to use OpenAI (no flags needed) or other models (see code for flags). See on the top of `webscraper.py` for more CLI-flags (`--render`, `--auto-render` etc.).

```bash
# Running the Webscraper
uv run python webscraper.py "https://example.com" # will use OpenAI as default provider
uv run python webscraper.py "https://example.com" --provider ollama
uv run python webscraper.py "https://example.com" --provider google
```


## Configuration

- **`env`:** Copy `.env.example` to `.env`. Please note that `.env.example` is safe to leave on GitHub, **do not** put any secrets in it!
- **Gemini:** Uses the same OpenAI Python SDK against Google’s [OpenAI-compatible Gemini endpoint](https://ai.google.dev/gemini-api/docs/openai) (`GOOGLE_BASE_URL` must include `/v1beta/openai/` unless you override it).
- **`uv.lock`:** Commit this file for reusable installations (recommended).

## Help

If you need help when running the script in your CLI, you can use the following command:

```bash
uv run python webscraper.py --help
```

This will display a short help text explaining the different flags available.

## License
GPL-3.0. Please see `LICENSE` for more information.