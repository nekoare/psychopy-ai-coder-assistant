"""Command line interface for PsychoPy AI Coder Assistant.

This CLI enables offline (pattern-only) or LLM-assisted analysis of a Python
script so it can be frozen into a standalone Windows executable (e.g. with
PyInstaller) without requiring the full PsychoPy GUI environment.

Usage (after install):
  ai-coder-assistant path/to/script.py --json > result.json
  ai-coder-assistant path/to/script.py --provider openai --api-key sk-XXXX

When frozen as an .exe, environment variables or command line flags can supply
API keys. If no key is present, local pattern detection only is performed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

from .config import ConfigManager
from .analyzer import CodeAnalyzer


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Analyze a Python script for PsychoPy-related improvements"
    )
    p.add_argument("path", help="Path to the Python script to analyze")
    p.add_argument("--provider", choices=["openai", "anthropic", "google"], default=None,
                   help="LLM provider (omit for pattern-only)")
    p.add_argument("--api-key", dest="api_key", default=None,
                   help="API key (overrides environment variable if given)")
    p.add_argument("--json", action="store_true", help="Output JSON instead of text table")
    p.add_argument("--max", type=int, default=10, help="Maximum number of suggestions to show")
    p.add_argument("--no-llm", action="store_true", help="Force disable LLM even if key provided")
    return p


def _configure_for_cli(provider: str | None, api_key: str | None, disable_llm: bool) -> ConfigManager:
    cfg = ConfigManager()
    # In CLI mode we avoid writing secrets unless user explicitly requests.
    if provider and api_key and not disable_llm:
        cfg.set("api_provider", provider)
        cfg.set_api_key(provider, api_key)
    return cfg


def _read_code(path: str) -> str:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _suggestions_to_dict(s) -> Dict[str, Any]:  # helper for JSON
    return {
        "category": s.category,
        "title": s.title,
        "description": s.description,
        "original_code": s.original_code,
        "improved_code": s.improved_code,
        "line_numbers": s.line_numbers,
        "priority": s.priority,
    }


def output_text(result, limit: int):
    print(f"Summary: {result.summary}")
    print("Suggestions:")
    for i, s in enumerate(result.suggestions[:limit], 1):
        print(f"\n[{i}] ({s.priority}) {s.category} - {s.title}")
        if s.description:
            print(f"  {s.description}")
        if s.original_code:
            print("  Original: ")
            print("    " + s.original_code.replace("\n", "\n    "))
        if s.improved_code:
            print("  Improved: ")
            print("    " + s.improved_code.replace("\n", "\n    "))


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # Resolve API key precedence: CLI flag > ENV > none
    env_key_map = {
        "openai": os.environ.get("OPENAI_API_KEY"),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
        "google": os.environ.get("GOOGLE_API_KEY"),
    }
    provider = None if args.no_llm else args.provider
    key = None if args.no_llm else (args.api_key or (provider and env_key_map.get(provider)))

    cfg = _configure_for_cli(provider, key, args.no_llm or not key)
    analyzer = CodeAnalyzer(cfg)

    try:
        code = _read_code(args.path)
        result = analyzer.analyze_code(code)
    except Exception as e:  # pragma: no cover - CLI runtime path
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.json:
        payload = {
            "summary": result.summary,
            "success": result.success,
            "analysis_time": result.analysis_time,
            "suggestions": [
                _suggestions_to_dict(s) for s in result.suggestions[: args.max]
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        output_text(result, args.max)

    return 0 if result.success else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())