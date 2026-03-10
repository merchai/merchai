"""
app.py  —  MerchAI Share of Voice API
--------------------------------------
Run locally:
    python app.py

Endpoints
---------
POST /api/share-of-voice
    Body : { "mentions": ["Nike", "Adidas", "Nike"], "query_label": "optional" }
    Returns: full analytics report (see compute_analytics)

GET  /api/health
    Returns: { status: "ok" }
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request
from flask_cors import CORS  # type: ignore[import-untyped]

from src.metrics.share_of_voice import compute_analytics
from src.extraction import extract_brands_from_text

app = Flask(__name__)
CORS(app)   # allow the React dev server to call us


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "MerchAI Share of Voice"})


@app.post("/api/share-of-voice")
def share_of_voice():
    body = request.get_json(silent=True) or {}

    mentions = body.get("mentions")
    query_label = body.get("query_label", "")

    # ── Validate ──────────────────────────────────────────────────────────────
    if mentions is None:
        return jsonify({"error": "Missing required field: mentions"}), 400

    if not isinstance(mentions, list):
        return jsonify({"error": "mentions must be an array of strings"}), 400

    if not all(isinstance(m, str) for m in mentions):
        return jsonify({"error": "Every item in mentions must be a string"}), 400

    # ── Compute ───────────────────────────────────────────────────────────────
    try:
        result = compute_analytics(mentions, query_label)
    except TypeError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)


@app.post("/api/extract-brands")
def extract_brands_endpoint():
    body = request.get_json(silent=True) or {}
    text = body.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "text is required"}), 400
    brands = extract_brands_from_text(text)
    return jsonify({"brands": brands, "count": len(brands)})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
