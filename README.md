# ai-playground

Lek/eksperimenter med nettskraping og ulike LLM-leverandører.

## Krav

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Kom i gang

```bash
git clone <repo-url>
cd ai-playground
uv sync
cp .env.example .env
# Rediger .env med API-nøkler / Ollama-innstillinger

# Playwright (første gang)
uv run playwright install chromium

# Kjøring
uv run python webscraper.py "https://example.com"
uv run python webscraper.py "https://example.com" --provider ollama
uv run python webscraper.py "https://example.com" --provider google
```

Se `webscraper.py` øverst for flere CLI-flagg (`--render`, `--auto-render` osv.).

## Konfigurasjon

- **`env`:** Kopier `.env.example` til `.env`. Den eksempelfila er trygg å ha på GitHub; **ikke** legg inn hemmeligheter der.
- **`uv.lock`:** Committ den for reproduserbare installasjoner (anbefalt).

## Lisens

Ikke satt — legg inn en `LICENSE` om du vil at andre skal vite brukervilkår.
