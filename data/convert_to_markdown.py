"""Convert every downloaded SEC HTML filing to Markdown with Docling."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from docling.document_converter import DocumentConverter

DATA_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = DATA_DIR / "downloads"
MARKDOWN_DIR = DATA_DIR / "markdown"


def markdown_path(source: Path) -> Path:
    return MARKDOWN_DIR / source.relative_to(DOWNLOADS_DIR).with_suffix(".md")


def convert_all() -> dict:
    source_manifest = json.loads((DOWNLOADS_DIR / "manifest.json").read_text(encoding="utf-8"))
    filings_by_path = {
        Path(filing["local_path"]): filing for filing in source_manifest["filings"]
    }
    sources = sorted(
        path for path in DOWNLOADS_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in {".html", ".htm"}
    )
    converter = DocumentConverter()
    converted = []

    for index, source in enumerate(sources, start=1):
        relative = source.relative_to(DOWNLOADS_DIR)
        target = markdown_path(source)
        print(f"[{index}/{len(sources)}] {relative} -> {target.relative_to(MARKDOWN_DIR)}", flush=True)
        markdown = converter.convert(source).document.export_to_markdown()
        if not markdown.strip():
            raise ValueError(f"Docling produced empty Markdown for {source}")
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".md.tmp")
        temporary.write_text(markdown, encoding="utf-8")
        temporary.replace(target)

        filing = filings_by_path.get(relative, {})
        converted.append({
            **filing,
            "source_html_path": str(relative),
            "local_path": str(target.relative_to(MARKDOWN_DIR)),
        })

    manifest = {
        "source": source_manifest["source"],
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "form": source_manifest["form"],
        "converted_count": len(converted),
        "filings": converted,
    }
    MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
    (MARKDOWN_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    result = convert_all()
    print(f"Converted {result['converted_count']} filing(s) to {MARKDOWN_DIR}")
