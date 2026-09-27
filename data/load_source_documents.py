"""Load the converted Markdown filings into source_documents."""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

DATA_DIR = Path(__file__).resolve().parent
ROOT_DIR = DATA_DIR.parent
MARKDOWN_DIR = DATA_DIR / "markdown"
COMPANIES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "NVDA": "NVIDIA Corporation",
    "AMZN": "Amazon.com, Inc.",
    "GOOGL": "Alphabet Inc.",
}


def load_documents() -> int:
    # The backend settings module reads backend/.env relative to the working directory.
    os.chdir(ROOT_DIR / "backend")
    sys.path.insert(0, str(ROOT_DIR / "backend"))
    from app.config import settings

    manifest = json.loads((MARKDOWN_DIR / "manifest.json").read_text(encoding="utf-8"))
    filings = manifest["filings"]
    url = make_url(settings.database_url)
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    engine = create_engine(url)
    statement = text("""
        INSERT INTO source_documents (
            ticker, company, filing_type, filing_date, fiscal_year,
            accession_number, source_url, content_markdown
        ) VALUES (
            :ticker, :company, :filing_type, :filing_date, :fiscal_year,
            :accession_number, :source_url, :content_markdown
        ) ON CONFLICT (accession_number) DO UPDATE SET
            ticker = EXCLUDED.ticker,
            company = EXCLUDED.company,
            filing_type = EXCLUDED.filing_type,
            filing_date = EXCLUDED.filing_date,
            fiscal_year = EXCLUDED.fiscal_year,
            source_url = EXCLUDED.source_url,
            content_markdown = EXCLUDED.content_markdown
    """)

    with engine.begin() as connection:
        for filing in filings:
            relative = Path(filing["local_path"])
            path = (MARKDOWN_DIR / relative).resolve()
            if not path.is_relative_to(MARKDOWN_DIR.resolve()):
                raise ValueError(f"Invalid Markdown path: {relative}")
            markdown = path.read_text(encoding="utf-8")
            if not markdown.strip():
                raise ValueError(f"Empty Markdown file: {path}")
            connection.execute(statement, {
                "ticker": filing["ticker"],
                "company": COMPANIES[filing["ticker"]],
                "filing_type": filing["form"],
                "filing_date": date.fromisoformat(filing["filing_date"]),
                "fiscal_year": int(filing["report_date"][:4]),
                "accession_number": filing["accession_number"],
                "source_url": filing["source_url"],
                "content_markdown": markdown,
            })
            print(f"Loaded {filing['accession_number']}", flush=True)

        accession_numbers = [filing["accession_number"] for filing in filings]
        count = connection.execute(
            text("SELECT count(*) FROM source_documents WHERE accession_number = ANY(:accessions)"),
            {"accessions": accession_numbers},
        ).scalar_one()
        if count != len(filings):
            raise RuntimeError(f"Expected {len(filings)} source documents, found {count}")

    return count


if __name__ == "__main__":
    print(f"Verified {load_documents()} source documents in the database")
