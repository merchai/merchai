"""
src/pipeline.py

End-to-end MerchAI pipeline: prompt → LLM → extract → SOV → persist.

This is the single entry point for running a brand share-of-voice analysis.
Chains perplexity_client, extraction, and db together. Handles errors at
each stage and persists every run for historical tracking.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.tracking.perplexity_client import PerplexityError, query_perplexity
from src.extraction import ExtractionResult, extract_brands_from_text
from src import db as database

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

PROMPT_VERSION = "v1.1"

_SOV_PROMPT_TEMPLATE = """What brands sell {category}?

List as many brands as possible, from mass-market to premium.
Mention each brand name explicitly and repeatedly where relevant.
Include both dominant market leaders and niche or emerging players.
Be comprehensive and factual."""


def build_sov_prompt(category: str) -> str:
    """Build a share-of-voice prompt for a product category."""
    return _SOV_PROMPT_TEMPLATE.format(category=category.strip().lower())


# ---------------------------------------------------------------------------
# Default categories NOBE cares about
# ---------------------------------------------------------------------------

DEFAULT_CATEGORIES = [
    "hoodies",
    "t-shirts",
    "sweatpants",
    "hats and caps",
    "varsity jackets",
    "collegiate merchandise",
]

# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class PipelineResult:
    """Full output of one pipeline run."""
    category: str
    prompt: str
    raw_response: str
    extraction: ExtractionResult
    run_id: int | None = None
    error: str | None = None
    skipped: bool = False  # True if deduplication prevented a new run

    @property
    def success(self) -> bool:
        return self.error is None and not self.skipped

    def summary(self) -> dict[str, Any]:
        """Return a JSON-serialisable summary for the dashboard."""
        return {
            "category": self.category,
            "run_id": self.run_id,
            "success": self.success,
            "skipped": self.skipped,
            "error": self.error,
            "total_mentions": len(self.extraction.mentions),
            "unique_brands": len(set(self.extraction.brand_names)),
            "share_of_voice": self.extraction.share_of_voice(),
            "high_confidence_brands": self.extraction.high_confidence(),
        }


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run(
    category: str,
    *,
    min_confidence: float = 0.3,
    skip_duplicates: bool = True,
    dedupe_hours: int = 24,
    db_path: Path = database.DEFAULT_DB_PATH,
) -> PipelineResult:
    """
    Run the full MerchAI pipeline for a product category.

    Steps:
        1. Build a structured prompt from the category string.
        2. Check for duplicate run within dedupe_hours (if skip_duplicates).
        3. Query Perplexity API (with retries + backoff).
        4. Extract brand mentions with confidence scoring.
        5. Persist run to SQLite.
        6. Return a PipelineResult with SOV data.

    Args:
        category:        Product category to analyse (e.g. "hoodies").
        min_confidence:  Minimum confidence score to include a brand mention.
        skip_duplicates: Skip if identical prompt ran within dedupe_hours.
        dedupe_hours:    Deduplication window in hours.
        db_path:         Path to the SQLite database file.

    Returns:
        PipelineResult — always returns, never raises. Check .success.
    """
    database.init_db(db_path)
    prompt = build_sov_prompt(category)
    logger.info("Running pipeline for category: %r", category)

    # Stage 0: Deduplication
    if skip_duplicates and database.is_duplicate(prompt, within_hours=dedupe_hours, db_path=db_path):
        logger.info("Skipping duplicate run for category=%r", category)
        latest_sov = database.get_latest_sov(category, db_path=db_path)
        # Reconstruct a minimal result from cached data
        extraction = ExtractionResult()
        return PipelineResult(
            category=category,
            prompt=prompt,
            raw_response="[cached]",
            extraction=extraction,
            skipped=True,
        )

    # Stage 1: Query LLM
    try:
        raw_response = query_perplexity(prompt)
        logger.info("Got %d chars from Perplexity", len(raw_response))
    except PerplexityError as e:
        logger.error("Perplexity query failed: %s", e)
        run_id = database.save_run(
            category=category, prompt=prompt, raw_response="",
            sov={}, brand_count=0, mention_count=0,
            success=False, error=str(e), db_path=db_path,
        )
        return PipelineResult(
            category=category, prompt=prompt, raw_response="",
            extraction=ExtractionResult(), run_id=run_id, error=str(e),
        )

    # Stage 2: Extract brands
    extraction = extract_brands_from_text(raw_response, min_confidence=min_confidence)
    sov = extraction.share_of_voice()
    unique_brands = len(set(extraction.brand_names))
    logger.info(
        "Extracted %d mentions → %d unique brands",
        len(extraction.mentions), unique_brands,
    )

    # Stage 3: Persist
    run_id = database.save_run(
        category=category,
        prompt=prompt,
        raw_response=raw_response,
        sov=sov,
        brand_count=unique_brands,
        mention_count=len(extraction.mentions),
        db_path=db_path,
    )

    return PipelineResult(
        category=category,
        prompt=prompt,
        raw_response=raw_response,
        extraction=extraction,
        run_id=run_id,
    )


def run_all(
    categories: list[str] = DEFAULT_CATEGORIES,
    **kwargs: Any,
) -> list[PipelineResult]:
    """
    Run the pipeline for multiple categories sequentially.

    Args:
        categories: List of product categories to analyse.
        **kwargs:   Passed through to run().

    Returns:
        List of PipelineResult, one per category.
    """
    results = []
    for category in categories:
        logger.info("--- Running category: %s ---", category)
        result = run(category, **kwargs)
        results.append(result)
    return results


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if len(sys.argv) > 1:
        categories = sys.argv[1:]
    else:
        categories = DEFAULT_CATEGORIES

    results = run_all(categories)
    for r in results:
        print(json.dumps(r.summary(), indent=2))