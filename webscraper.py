# A webscraper project made for fun and for learning more Python and using AI APIs
# @Author: Håkon Trønnes - hatron
#
# Usage:
#   python webscraper.py "https://example.com"                    # using OpenAI as default
#   python webscraper.py "https://spa.example.com" --render       # force Chromium (CSR/SPA)
#   python webscraper.py "https://spa.example.com" --auto-render  # browser only if static text is tiny
#   python webscraper.py <URL> --provider ollama                  # using Ollama
#   python webscraper.py <URL> --provider google                  # using Gemini
#
# After first install: playwright install chromium

import argparse
import os
import re
import sys
from typing import Callable
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import NotFoundError, OpenAI
from rich.console import Console
from rich.markdown import Markdown

_console = Console()

MAX_TEXT_CHARS = 80_000
AUTO_RENDER_MIN_CHARS = 400

DEFAULT_SYSTEM_PROMPT = """You are an assistant that analyzes the contents of a website 
and provides a short summary, ignoring text that might be navigation related. 
Summarize the main content clearly for the average reader. 
If the text looks like boilerplate or is very short, say so and summarize what is available. 
Respond in markdown."""


class Website:
    """Parse fetched HTML into a title and plain text (noise tags stripped)."""

    def __init__(self, html: str) -> None:
        soup = BeautifulSoup(html, "lxml")
        raw_title = soup.title.get_text(strip=True) if soup.title else ""
        self.title = raw_title or "No title found"

        for tag in soup(["script", "style", "noscript", "img", "input"]):
            tag.decompose()

        root = soup.body if soup.body else soup
        raw = root.get_text(separator="\n", strip=True)
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        self.text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def fetch_html_static(url: str, timeout: float = 30.0) -> str:
    r = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; AIWebScraper/1.0)"},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.text


def fetch_html_rendered(url: str, timeout_ms: int = 60_000, settle_ms: int = 2_000) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="load", timeout=timeout_ms)
            page.wait_for_timeout(settle_ms)
            return page.content()
        finally:
            browser.close()


def _truncated_extract(text: str) -> str:
    chunk = text[:MAX_TEXT_CHARS]
    if len(text) > MAX_TEXT_CHARS:
        chunk += "\n\n[... truncated for context length ...]"
    return chunk


def _summarize_openai_chat(
    *,
    model: str,
    api_key: str,
    base_url: str | None,
    system_prompt: str,
    text: str,
) -> str:
    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": _truncated_extract(text)},
        ],
        temperature=0.3,
    )
    return completion.choices[0].message.content or ""


def summarize_openai(text: str, system_prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.exit("OPENAI_API_KEY is not set (check your .env).")
    return _summarize_openai_chat(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        system_prompt=system_prompt,
        text=text,
    )


def summarize_ollama(text: str, system_prompt: str) -> str:
    return _summarize_openai_chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        api_key=os.getenv("OLLAMA_API_KEY") or "ollama",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        system_prompt=system_prompt,
        text=text,
    )


def summarize_google(text: str, system_prompt: str) -> str:
    from google import genai

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        sys.exit("GOOGLE_API_KEY is not set.")
    model = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    client = genai.Client(api_key=api_key)
    prompt = f"{system_prompt}\n\n{_truncated_extract(text)}"
    response = client.models.generate_content(model=model, contents=prompt)
    return (response.text or "").strip()


def _load_html(url: str, *, use_browser: bool) -> str:
    try:
        return fetch_html_rendered(url) if use_browser else fetch_html_static(url)
    except requests.RequestException as e:
        sys.exit(f"HTTP fetch failed: {e}")
    except Exception as e:
        sys.exit(f"Fetch failed: {e}")


def _extract_page(url: str, *, render: bool, auto_render: bool) -> tuple[str, str]:
    """Return (page title, plain body text) from the final fetch (static or browser)."""
    html = _load_html(url, use_browser=render)
    page = Website(html)
    title, text = page.title, page.text
    if auto_render and not render and len(text) < AUTO_RENDER_MIN_CHARS:
        try:
            page = Website(fetch_html_rendered(url))
            title, text = page.title, page.text
        except Exception as e:
            sys.exit(f"Auto-render (Playwright) failed: {e}")
    return title, text


SUMMARIZERS: dict[str, Callable[[str, str], str]] = {
    "openai": summarize_openai,
    "ollama": summarize_ollama,
    "google": summarize_google,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fetch a webpage, extract text, summarize with an LLM.",
    )
    p.add_argument("url", help="Full URL to scrape (e.g. https://example.com).")
    p.add_argument(
        "--provider",
        choices=tuple(SUMMARIZERS),
        default="openai",
        help="LLM backend (default: openai).",
    )
    p.add_argument(
        "--render",
        action="store_true",
        help="Use headless Chromium (Playwright) for CSR/SPA pages.",
    )
    p.add_argument(
        "--auto-render",
        action="store_true",
        help="HTTP first; if text is tiny, retry with Playwright.",
    )
    p.add_argument(
        "--system-prompt",
        default=DEFAULT_SYSTEM_PROMPT,
        help="System prompt for the summarizer.",
    )
    return p.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    url = args.url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        sys.exit("Provide a valid http(s) URL.")
    if args.render and args.auto_render:
        sys.exit("Use either --render or --auto-render, not both.")

    title, text = _extract_page(url, render=args.render, auto_render=args.auto_render)
    if not text:
        sys.exit(
            "No text extracted (empty document or blocked). "
            "Try using --render if the site is client-rendered.",
        )

    try:
        summary = SUMMARIZERS[args.provider](text, args.system_prompt)
    except NotFoundError as err:
        if args.provider == "ollama":
            model = os.getenv("OLLAMA_MODEL", "llama3.2")
            sys.exit(
                f"Ollama: The model {model!r} doesn't exist (404). "
                "Check `ollama list`, pull model with `ollama pull <model_name>`, "
                "and update OLLAMA_MODEL in .env if necessary. "
                f"Details: {err}"
            )
        raise

    heading = " ".join(title.split())
    _console.print(Markdown(f"# {heading}\n\n{summary}"))


if __name__ == "__main__":
    main()