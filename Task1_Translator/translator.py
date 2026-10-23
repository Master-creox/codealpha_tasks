"""Language Translator — translate text with Google Translate.

Upgraded from the original single-shot script: any target language,
auto or explicit source language, multiple texts, file input, and a
reusable translate_text() function. Translation itself is done by the
`deep-translator` package (free Google Translate endpoint — needs
internet); the CLI, validation and plumbing are offline-testable.

Examples:
    python translator.py "Hello, how are you?"                # -> Hindi (default)
    python translator.py --to es "Good morning"               # -> Spanish
    python translator.py --from en --to hi "Thank you"
    python translator.py --file phrases.txt --to hi           # line by line
    python translator.py                                      # interactive mode
    python translator.py --list-languages                     # supported codes
"""
from __future__ import annotations

import argparse
import sys

DEFAULT_TARGET = "hi"  # Hindi, as in the original task


def get_translator(source: str, target: str):
    """Create a translator object (isolated so tests can inject a fake)."""
    from deep_translator import GoogleTranslator
    return GoogleTranslator(source=source, target=target)


def supported_languages() -> dict:
    from deep_translator import GoogleTranslator
    return GoogleTranslator().get_supported_languages(as_dict=True)


def translate_text(text: str, target: str = DEFAULT_TARGET, source: str = "auto",
                   translator_factory=get_translator) -> str:
    """Translate one string. Raises ValueError on empty input."""
    text = (text or "").strip()
    if not text:
        raise ValueError("No text to translate.")
    translator = translator_factory(source, target)
    result = translator.translate(text)
    if result is None:
        raise RuntimeError("Translation returned nothing — check the language codes.")
    return result


def translate_lines(lines, target: str, source: str = "auto",
                    translator_factory=get_translator) -> list[str]:
    """Translate many lines, preserving blank lines as-is."""
    return [translate_text(line, target, source, translator_factory) if line.strip() else ""
            for line in lines]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Language translator (Google Translate).")
    parser.add_argument("text", nargs="*", help="Text to translate. Omit for interactive mode.")
    parser.add_argument("--to", default=DEFAULT_TARGET, help="Target language code (default: hi).")
    parser.add_argument("--from", dest="source", default="auto",
                        help="Source language code (default: auto-detect).")
    parser.add_argument("--file", default=None, help="Translate this text file line by line.")
    parser.add_argument("--list-languages", action="store_true", help="Print supported language codes.")
    args = parser.parse_args(argv)

    if args.list_languages:
        for name, code in sorted(supported_languages().items()):
            print(f"{code:>6}  {name}")
        return 0

    try:
        if args.file:
            with open(args.file, encoding="utf-8") as fh:
                lines = fh.read().splitlines()
            for original, translated in zip(lines, translate_lines(lines, args.to, args.source)):
                if original.strip():
                    print(f"{original}  ->  {translated}")
            return 0
        if args.text:
            print("Translated:", translate_text(" ".join(args.text), args.to, args.source))
            return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}")
        return 1
    except Exception as exc:  # network/API failures from deep-translator
        print(f"Translation error: {exc}")
        return 1

    # Interactive mode (the original behaviour, kept).
    print("=== Language Translator ===")
    text = input("Enter text: ").strip()
    if not text:
        print("No text entered.")
        return 0
    try:
        print("Translated:", translate_text(text, args.to, args.source))
    except Exception as exc:
        print(f"Translation error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
