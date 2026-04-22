import { useState, useEffect, useRef } from "react";

// ── Colour palette per rank ───────────────────────────────────────────────────
const BRAND_COLORS = [
  "#C8F04C", "#4CF0A8", "#4CC8F0", "#F0A84C",
  "#F04C7A", "#A84CF0", "#F0F04C",
];

const CONFIDENCE_COLOR = { Low: "#F04C7A", Medium: "#F0A84C", High: "#4CF0A8" };
const CONFIDENCE_HINT  = { Low: "< 20 mentions", Medium: "20–49 mentions", High: "50+ mentions" };

// ── Brand logos (Clearbit) ────────────────────────────────────────────────────
const BRAND_DOMAIN_OVERRIDES = {
  // Footwear
  "brooks": "brooksrunning.com",
  "hoka": "hoka.com",
  "new balance": "newbalance.com",
  "under armour": "underarmour.com",
  "on running": "on-running.com",
  "on": "on-running.com",
  "k-swiss": "kswiss.com",
  "le coq sportif": "lecoqsportif.com",
  "saucony": "saucony.com",
  "asics": "asics.com",
  "salomon": "salomon.com",
  "merrell": "merrell.com",
  "keen": "keenfootwear.com",
  // Luxury
  "louis vuitton": "louisvuitton.com",
  "saint laurent": "ysl.com",
  "alexander mcqueen": "alexandermcqueen.com",
  "jimmy choo": "jimmychoo.com",
  "hermès": "hermes.com",
  "hermes": "hermes.com",
  // Apparel / lifestyle
  "the north face": "thenorthface.com",
  "new era": "neweracap.com",
  "ralph lauren": "ralphlauren.com",
  "calvin klein": "calvinklein.com",
  "tommy hilfiger": "tommyhilfiger.com",
  "michael kors": "michaelkors.com",
  "kate spade": "katespade.com",
  "marc jacobs": "marcjacobs.com",
  "dolce gabbana": "dolcegabbana.com",
  // Tech
  "google": "google.com",
  "apple": "apple.com",
  "samsung": "samsung.com",
  "oneplus": "oneplus.com",
  "microsoft": "microsoft.com",
  "meta": "meta.com",
  "openai": "openai.com",
};

function getBrandLogoUrl(brand) {
  const key = brand.toLowerCase();
  const domain = BRAND_DOMAIN_OVERRIDES[key] || `${key.replace(/[^a-z0-9]/g, "")}.com`;
  return `https://logo.clearbit.com/${domain}`;
}

function BrandLogo({ brand }) {
  const [show, setShow] = useState(true);
  if (!show) return null;
  return (
    <img
      src={getBrandLogoUrl(brand)}
      alt=""
      onError={() => setShow(false)}
      style={{
        width: 22, height: 22, borderRadius: "50%",
        objectFit: "contain", background: "#fff",
        flexShrink: 0, padding: 1,
      }}
    />
  );
}

// ── Brand extraction (client-side, for "brand names" mode) ───────────────────
const MULTI_WORD_BRANDS = ["New Balance", "Under Armour", "On Running", "K-Swiss", "Le Coq Sportif"];

function extractBrand(line) {
  const trimmed = line.trim();
  if (!trimmed) return "";
  for (const brand of MULTI_WORD_BRANDS) {
    if (trimmed.toLowerCase().startsWith(brand.toLowerCase())) return brand;
  }
  return trimmed.split(/\s+/)[0];
}

const DEMO_QUERIES = [
  { label: "Best running shoes", mentions: ["Nike", "Adidas", "Nike", "Brooks", "Nike", "Adidas", "New Balance", "Nike", "Adidas", "Brooks"] },
  { label: "Luxury handbags", mentions: ["Louis Vuitton", "Gucci", "Louis Vuitton", "Chanel", "Gucci", "Louis Vuitton", "Hermès", "Chanel"] },
  { label: "Smartphone comparison", mentions: ["Apple", "Samsung", "Apple", "Google", "Apple", "Samsung", "Apple", "OnePlus", "Samsung"] },
];

// ── Helpers ───────────────────────────────────────────────────────────────────
function triggerDownload(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

function buildReportText(result) {
  const lines = [
    "SHARE OF VOICE REPORT",
    result.query_label ? `Query: "${result.query_label}"` : "",
    "",
    "RANKINGS",
    ...result.ranked.map(({ brand, share }, i) =>
      `#${i + 1} ${brand} — ${Math.round(share * 100)}% (${result.counts[brand]} mention${result.counts[brand] !== 1 ? "s" : ""})${i === 0 ? " ★ Leader" : ""}`
    ),
    "",
    "COMPETITIVE GAPS",
    ...Object.entries(result.competitive_gaps).map(([b, g]) =>
      `${b}: −${Math.abs(Math.round(g * 100))}% vs leader`
    ),
    "",
    "MARKET INSIGHT",
    result.generated_insight,
    "",
    "SUGGESTED ACTION",
    result.suggested_action,
    "",
    `CONFIDENCE: ${result.confidence_level} (${CONFIDENCE_HINT[result.confidence_level]})`,
    `Market Concentration (Top 3): ${Math.round(result.concentration_top3 * 100)}%`,
  ].filter(l => l !== undefined);
  return lines.join("\n");
}

// ── Animated number ───────────────────────────────────────────────────────────
function AnimatedNumber({ value, suffix = "" }) {
  const [display, setDisplay] = useState(0);
  const raf = useRef();
  useEffect(() => {
    const start = Date.now();
    const tick = () => {
      const p = Math.min((Date.now() - start) / 800, 1);
      setDisplay(value * (1 - Math.pow(1 - p, 3)));
      if (p < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [value]);
  return <span>{Math.round(display)}{suffix}</span>;
}

// ── Bar row ───────────────────────────────────────────────────────────────────
function BrandBar({ brand, share, count, rank, color, animate, isTop, isTied }) {
  const pct = Math.round(share * 100);
  const [width, setWidth] = useState(0);
  useEffect(() => {
    if (animate) { const t = setTimeout(() => setWidth(pct), 80 + rank * 60); return () => clearTimeout(t); }
    else setWidth(pct);
  }, [pct, animate, rank]);

  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{
            width: 22, height: 22, borderRadius: "50%", background: color,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 10, fontWeight: 700, color: "#0a0a0a", flexShrink: 0,
          }}>{rank + 1}</span>
          <BrandLogo brand={brand} />
          <span style={{ fontSize: 15, fontWeight: 600, color: "#f0f0f0", fontFamily: "'Syne', sans-serif" }}>
            {brand}
          </span>
          {isTop && (
            <span style={{
              fontSize: 9, fontWeight: 700, color: "#0a0a0a",
              background: isTied ? "#F0A84C" : "#C8F04C",
              borderRadius: 4, padding: "2px 6px", fontFamily: "'DM Mono', monospace",
              letterSpacing: 1, textTransform: "uppercase",
            }}>{isTied ? "Tied" : "Leader"}</span>
          )}
        </div>
        <span style={{ fontSize: 13, fontWeight: 700, color, fontFamily: "monospace" }}>
          {animate ? <AnimatedNumber value={pct} suffix="%" /> : `${pct}%`}
          <span style={{ fontSize: 11, color: "#555", fontWeight: 400 }}> ({count})</span>
        </span>
      </div>
      <div style={{ height: 6, background: "#1a1a1a", borderRadius: 3, overflow: "hidden" }}>
        <div style={{
          height: "100%", borderRadius: 3, background: color,
          width: `${width}%`, transition: "width 0.7s cubic-bezier(0.16, 1, 0.3, 1)",
          boxShadow: `0 0 12px ${color}55`,
        }} />
      </div>
    </div>
  );
}

// ── Main app ──────────────────────────────────────────────────────────────────
export default function App() {
  const [input, setInput] = useState("");
  const [queryLabel, setQueryLabel] = useState("");
  const [inputMode, setInputMode] = useState("brands"); // "brands" | "response"
  const [result, setResult] = useState(null);
  const [animate, setAnimate] = useState(false);
  const [activeDemo, setActiveDemo] = useState(null);
  const [inputError, setInputError] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [copied, setCopied] = useState(false);
  const [runs, setRuns] = useState(null);
  const [showRuns, setShowRuns] = useState(false);

  const loadRuns = async () => {
    const res = await fetch("/api/runs");
    const data = await res.json();
    setRuns(data);
    setShowRuns(true);
  };

  const runAnalysis = async (mentions, label) => {
    if (!mentions.length) { setInputError("Enter at least one brand mention."); return; }
    setInputError(""); setApiError(""); setResult(null); setLoading(true); setAnimate(false);
    try {
      const res = await fetch("/api/share-of-voice", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mentions, query_label: label }),
      });
      let data;
      try { data = await res.json(); } catch {
        throw new Error("Backend unreachable — make sure it's running on port 5000.");
      }
      if (!res.ok) throw new Error(data.error || "Request failed");
      setAnimate(true); setResult(data);
    } catch (err) { setApiError(err.message); }
    finally { setLoading(false); }
  };

  const handleSubmit = async () => {
    setActiveDemo(null);
    // Auto-detect prose: if any line has >4 words, treat as AI response regardless of mode
    const looksLikeProse = input.split(/[\n,]+/).some(line => line.trim().split(/\s+/).length > 4);
    const effectiveMode = looksLikeProse ? "response" : inputMode;

    if (effectiveMode === "response") {
      if (!input.trim()) { setInputError("Paste an AI response to analyze."); return; }
      setInputError(""); setApiError(""); setResult(null); setLoading(true); setAnimate(false);
      try {
        const extractRes = await fetch("/api/extract-brands", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: input, query_label: queryLabel }),
        });
        let extractData;
        try { extractData = await extractRes.json(); } catch {
          throw new Error("Backend unreachable — make sure it's running on port 5000.");
        }
        if (!extractRes.ok) throw new Error(extractData.error || "Extraction failed");
        const mentions = extractData.brands;
        if (!mentions.length) throw new Error("No brand names detected in the text.");

        const res = await fetch("/api/share-of-voice", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mentions, query_label: queryLabel }),
        });
        let data;
        try { data = await res.json(); } catch {
          throw new Error("Backend unreachable — make sure it's running on port 5000.");
        }
        if (!res.ok) throw new Error(data.error || "Analysis failed");
        setAnimate(true); setResult({ ...data, from_response: true, cached: extractData.cached, cached_at: extractData.cached_at });
      } catch (err) { setApiError(err.message); }
      finally { setLoading(false); }
    } else {
      const mentions = input.split(/[\n,]+/).map(extractBrand).filter(Boolean);
      runAnalysis(mentions, queryLabel);
    }
  };

  const handleDemo = (demo, idx) => {
    setInput(demo.mentions.join("\n"));
    setQueryLabel(demo.label);
    setActiveDemo(idx);
    setInputMode("brands");
    runAnalysis(demo.mentions, demo.label);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
  };

  const copyReport = () => {
    if (!result) return;
    navigator.clipboard.writeText(buildReportText(result)).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const exportCSV = () => {
    if (!result) return;
    const rows = [["Brand", "Share (%)", "Mentions"]];
    result.ranked.forEach(({ brand, share }) => rows.push([brand, Math.round(share * 100), result.counts[brand]]));
    triggerDownload(rows.map(r => r.join(",")).join("\n"), "share-of-voice.csv", "text/csv");
  };

  const exportJSON = () => {
    if (!result) return;
    triggerDownload(JSON.stringify(result, null, 2), "share-of-voice.json", "application/json");
  };

  // ── Styles shared ────────────────────────────────────────────────────────────
  const monoStyle = { fontFamily: "'DM Mono', monospace" };
  const syneStyle = { fontFamily: "'Syne', sans-serif" };

  return (
    <div style={{ minHeight: "100vh", background: "#080808", fontFamily: "'DM Sans', 'Segoe UI', sans-serif", color: "#e8e8e8" }}>
      <link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet" />

      {/* Top bar */}
      <div style={{
        borderBottom: "1px solid #161616", padding: "18px 40px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "#080808", position: "sticky", top: 0, zIndex: 10,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 30, height: 30, borderRadius: 8,
            background: "linear-gradient(135deg, #C8F04C, #4CF0A8)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <span style={{ fontSize: 14, fontWeight: 800, color: "#080808" }}>M</span>
          </div>
          <span style={{ fontSize: 15, fontWeight: 700, ...syneStyle, letterSpacing: 0.5 }}>MerchAI</span>
          <span style={{ fontSize: 10, letterSpacing: 2, color: "#444", textTransform: "uppercase", marginLeft: 4, ...monoStyle }}>Share of Voice</span>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {DEMO_QUERIES.map((d, i) => (
            <button key={i} onClick={() => handleDemo(d, i)} style={{
              padding: "6px 14px", borderRadius: 20, fontSize: 11,
              border: `1px solid ${activeDemo === i ? "#C8F04C" : "#222"}`,
              background: activeDemo === i ? "#C8F04C18" : "transparent",
              color: activeDemo === i ? "#C8F04C" : "#555",
              cursor: "pointer", ...monoStyle, transition: "all 0.2s",
            }}>{d.label}</button>
          ))}
        </div>
      </div>

      {/* Main layout */}
      <div style={{
        maxWidth: 1100, margin: "0 auto", padding: "48px 40px",
        display: "grid", gridTemplateColumns: "420px 1fr", gap: 32, alignItems: "start",
      }}>

        {/* Left — Input panel */}
        <div>
          <h1 style={{ ...syneStyle, fontSize: 28, fontWeight: 800, lineHeight: 1.2, margin: "0 0 8px", letterSpacing: -0.5 }}>
            Measure brand<br /><span style={{ color: "#C8F04C" }}>visibility</span> in AI
          </h1>
          <p style={{ fontSize: 13, color: "#444", margin: "0 0 28px", lineHeight: 1.6 }}>
            Paste an AI response to auto-extract brands, or enter brand names directly.
          </p>

          {/* Query label */}
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 10, letterSpacing: 2, color: "#444", textTransform: "uppercase", display: "block", marginBottom: 6, ...monoStyle }}>
              Query / Campaign
            </label>
            <input
              value={queryLabel} onChange={e => setQueryLabel(e.target.value)}
              placeholder='e.g. "best running shoes 2025"'
              style={{
                width: "100%", boxSizing: "border-box", background: "#111",
                border: "1px solid #1e1e1e", borderRadius: 8, padding: "10px 14px",
                color: "#e0e0e0", fontSize: 13, outline: "none", fontFamily: "'DM Sans', sans-serif",
              }}
            />
          </div>

          {/* Mode toggle + textarea */}
          <div style={{ marginBottom: 6 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <label style={{ fontSize: 10, letterSpacing: 2, color: "#444", textTransform: "uppercase", ...monoStyle }}>
                {inputMode === "brands" ? "Brand Mentions" : "AI Response"}
              </label>
              <div style={{ display: "flex", background: "#111", borderRadius: 6, padding: 2, border: "1px solid #1e1e1e" }}>
                {[["brands", "Brand Names"], ["response", "AI Response"]].map(([mode, label]) => (
                  <button key={mode} onClick={() => { setInputMode(mode); setInputError(""); }} style={{
                    padding: "4px 10px", borderRadius: 4, fontSize: 10, border: "none",
                    background: inputMode === mode ? "#C8F04C" : "transparent",
                    color: inputMode === mode ? "#0a0a0a" : "#555",
                    cursor: "pointer", ...monoStyle, fontWeight: inputMode === mode ? 700 : 400,
                    transition: "all 0.15s",
                  }}>{label}</button>
                ))}
              </div>
            </div>
            <textarea
              value={input}
              onChange={e => { setInput(e.target.value); setInputError(""); }}
              onKeyDown={handleKeyDown}
              placeholder={inputMode === "brands"
                ? "Nike\nAdidas\nNike\nPuma\n\nor comma-separated…"
                : "Paste an AI response here…\n\ne.g. \"The best running shoes include Nike Pegasus, Adidas Ultraboost, and Brooks Ghost…\""}
              rows={9}
              style={{
                width: "100%", boxSizing: "border-box", background: "#111",
                border: `1px solid ${inputError ? "#F04C7A" : "#1e1e1e"}`,
                borderRadius: 8, padding: "12px 14px", resize: "vertical",
                color: "#ccc", fontSize: 13, lineHeight: 1.8, outline: "none", ...monoStyle,
              }}
            />
          </div>
          {inputError && <p style={{ fontSize: 12, color: "#F04C7A", margin: "0 0 8px" }}>{inputError}</p>}
          <p style={{ fontSize: 11, color: "#333", margin: "0 0 20px", ...monoStyle }}>
            {inputMode === "brands" ? "One per line or comma-separated · ⌘↵ to run" : "Brands auto-extracted from response · ⌘↵ to run"}
          </p>

          <button onClick={handleSubmit} disabled={loading} style={{
            width: "100%", padding: "13px 0",
            background: loading ? "#3a4a14" : "#C8F04C", color: "#0a0a0a",
            border: "none", borderRadius: 8, fontSize: 14, fontWeight: 700,
            ...syneStyle, cursor: loading ? "default" : "pointer",
            letterSpacing: 0.3, transition: "all 0.15s",
          }}
            onMouseEnter={e => { if (!loading) e.target.style.opacity = "0.88"; }}
            onMouseLeave={e => { e.target.style.opacity = "1"; }}
          >
            {loading ? "Analyzing…" : inputMode === "response" ? "Extract & Analyze →" : "Compute Share of Voice →"}
          </button>
        </div>

        {/* Right — Results panel */}
        <div style={{ minHeight: 400 }}>

          {/* Loading */}
          {loading && (
            <div style={{ height: 400, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 12, color: "#333" }}>
              <div style={{ fontSize: 32, animation: "spin 1.2s linear infinite" }}>◌</div>
              <style>{`@keyframes spin { to { transform: rotate(360deg) } } @keyframes fadeIn { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:translateY(0) } }`}</style>
              <p style={{ fontSize: 13, ...monoStyle }}>Analyzing mentions…</p>
            </div>
          )}

          {/* Error */}
          {!loading && apiError && (
            <div style={{ height: 400, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8, border: "1px dashed #2a1a1a", borderRadius: 12, color: "#F04C7A" }}>
              <div style={{ fontSize: 28 }}>⚠</div>
              <p style={{ fontSize: 13, ...monoStyle, textAlign: "center", maxWidth: 280 }}>{apiError}</p>
              <p style={{ fontSize: 11, color: "#444", ...monoStyle }}>Is the backend running on port 5000?</p>
            </div>
          )}

          {/* Empty state */}
          {!loading && !apiError && !result && (
            <div style={{ height: 400, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10, border: "1px dashed #1a1a1a", borderRadius: 12, color: "#2a2a2a", padding: 32, textAlign: "center" }}>
              <div style={{ fontSize: 36 }}>◎</div>
              <p style={{ fontSize: 14, ...monoStyle, color: "#333" }}>Paste an AI response or brand names to analyze share of voice</p>
              <p style={{ fontSize: 11, color: "#222", ...monoStyle, lineHeight: 1.8 }}>
                Use <span style={{ color: "#444" }}>AI Response</span> mode to auto-extract brands<br />
                Use <span style={{ color: "#444" }}>Brand Names</span> to enter one per line
              </p>
            </div>
          )}

          {/* Results */}
          {!loading && result && (
            <div style={{ animation: "fadeIn 0.4s ease" }}>

              {/* Result header */}
              <div style={{ marginBottom: 20 }}>
                {result.query_label && (
                  <h2 style={{ ...syneStyle, fontSize: 17, fontWeight: 700, margin: "0 0 4px", color: "#e8e8e8" }}>
                    "{result.query_label}"
                  </h2>
                )}
                <p style={{ fontSize: 12, color: "#444", ...monoStyle, margin: 0 }}>
                  {result.total_mentions} mention{result.total_mentions !== 1 ? "s" : ""} analyzed
                  {" · "}{result.brand_count} brand{result.brand_count !== 1 ? "s" : ""} detected
                  {result.from_response && <span style={{ color: "#4CF0A8" }}> · extracted from AI response</span>}
                  {result.cached && (
                    <span style={{
                      display: "inline-block", marginLeft: 8,
                      fontSize: 9, fontWeight: 700, color: "#0a0a0a",
                      background: "#4CC8F0", borderRadius: 4,
                      padding: "2px 6px", fontFamily: "'DM Mono', monospace",
                      letterSpacing: 1, textTransform: "uppercase", verticalAlign: "middle",
                    }}
                      title={result.cached_at ? `Cached at ${new Date(result.cached_at).toLocaleString()}` : "Served from cache"}
                    >Cached</span>
                  )}
                </p>
              </div>

              {/* Stats — 2 rows of 3 */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, marginBottom: 20 }}>
                {/* Row 1 */}
                <div style={{ background: "#0e0e0e", border: "1px solid #1a1a1a", borderRadius: 10, padding: "12px 14px" }}>
                  <p style={{ fontSize: 9, color: "#444", textTransform: "uppercase", letterSpacing: 2, margin: "0 0 5px", ...monoStyle }}>Top Brand</p>
                  {result.is_tied
                    ? <p style={{ fontSize: 12, fontWeight: 700, margin: 0, ...syneStyle, color: "#F0A84C", lineHeight: 1.2 }}>{result.tied_leaders.length}-way tie</p>
                    : <p style={{ fontSize: 13, fontWeight: 700, margin: 0, ...syneStyle, color: "#C8F04C", lineHeight: 1.2, wordBreak: "break-word" }}>{result.top_brand}</p>
                  }
                </div>
                <div style={{ background: "#0e0e0e", border: "1px solid #1a1a1a", borderRadius: 10, padding: "12px 14px" }}>
                  <p style={{ fontSize: 9, color: "#444", textTransform: "uppercase", letterSpacing: 2, margin: "0 0 5px", ...monoStyle }}>Top Share</p>
                  <p style={{ fontSize: 22, fontWeight: 800, margin: 0, ...syneStyle, color: "#C8F04C" }}>
                    <AnimatedNumber value={Math.round((result.top_share ?? 0) * 100)} suffix="%" />
                  </p>
                </div>
                <div style={{ background: "#0e0e0e", border: "1px solid #1a1a1a", borderRadius: 10, padding: "12px 14px" }}>
                  <p style={{ fontSize: 9, color: "#444", textTransform: "uppercase", letterSpacing: 2, margin: "0 0 5px", ...monoStyle }}>Concentration</p>
                  <p style={{ fontSize: 22, fontWeight: 800, margin: 0, ...syneStyle, color: "#C8F04C" }}>
                    <AnimatedNumber value={Math.round((result.concentration_top3 ?? 0) * 100)} suffix="%" />
                  </p>
                  <p style={{ fontSize: 9, color: "#333", margin: "3px 0 0", ...monoStyle }}>top 3 brands</p>
                </div>
                {/* Row 2 */}
                <div style={{ background: "#0e0e0e", border: "1px solid #1a1a1a", borderRadius: 10, padding: "12px 14px" }}>
                  <p style={{ fontSize: 9, color: "#444", textTransform: "uppercase", letterSpacing: 2, margin: "0 0 5px", ...monoStyle }}>Mentions</p>
                  <p style={{ fontSize: 22, fontWeight: 800, margin: 0, ...syneStyle, color: "#C8F04C" }}>
                    <AnimatedNumber value={result.total_mentions} />
                  </p>
                </div>
                <div style={{ background: "#0e0e0e", border: "1px solid #1a1a1a", borderRadius: 10, padding: "12px 14px" }}>
                  <p style={{ fontSize: 9, color: "#444", textTransform: "uppercase", letterSpacing: 2, margin: "0 0 5px", ...monoStyle }}>Brands</p>
                  <p style={{ fontSize: 22, fontWeight: 800, margin: 0, ...syneStyle, color: "#C8F04C" }}>
                    <AnimatedNumber value={result.brand_count} />
                  </p>
                </div>
                <div style={{ background: "#0e0e0e", border: "1px solid #1a1a1a", borderRadius: 10, padding: "12px 14px" }}>
                  <p style={{ fontSize: 9, color: "#444", textTransform: "uppercase", letterSpacing: 2, margin: "0 0 5px", ...monoStyle }}>Confidence</p>
                  <p style={{ fontSize: 13, fontWeight: 700, margin: 0, ...syneStyle, color: CONFIDENCE_COLOR[result.confidence_level] }}>
                    {result.confidence_level}
                  </p>
                  <p style={{ fontSize: 9, color: "#333", margin: "3px 0 0", ...monoStyle }}>{CONFIDENCE_HINT[result.confidence_level]}</p>
                </div>
              </div>

              {/* Insight */}
              {result.generated_insight && (
                <div style={{ marginBottom: 12, background: "#0c0f08", border: "1px solid #1e2812", borderRadius: 10, padding: "14px 18px" }}>
                  <p style={{ fontSize: 9, letterSpacing: 2, color: "#3a4a20", textTransform: "uppercase", margin: "0 0 6px", ...monoStyle }}>Market Insight</p>
                  <p style={{ fontSize: 13, color: "#a0b870", margin: 0, lineHeight: 1.65 }}>{result.generated_insight}</p>
                </div>
              )}

              {/* Suggested action */}
              {result.suggested_action && (
                <div style={{ marginBottom: 20, background: "#0a0c10", border: "1px solid #181e28", borderRadius: 10, padding: "14px 18px" }}>
                  <p style={{ fontSize: 9, letterSpacing: 2, color: "#2a3a4a", textTransform: "uppercase", margin: "0 0 6px", ...monoStyle }}>Suggested Action</p>
                  <p style={{ fontSize: 13, color: "#70a0c0", margin: 0, lineHeight: 1.65 }}>{result.suggested_action}</p>
                </div>
              )}

              {/* Brand bars */}
              <div style={{ background: "#0c0c0c", border: "1px solid #161616", borderRadius: 12, padding: "24px 28px", marginBottom: 16 }}>
                <p style={{ fontSize: 10, letterSpacing: 2, color: "#333", textTransform: "uppercase", margin: "0 0 20px", ...monoStyle }}>
                  Share of Voice Distribution
                </p>
                {result.ranked.map(({ brand, share }, i) => (
                  <BrandBar
                    key={brand} brand={brand} share={share}
                    count={result.counts[brand]} rank={i}
                    color={BRAND_COLORS[i % BRAND_COLORS.length]}
                    animate={animate}
                    isTop={result.is_tied ? result.tied_leaders.includes(brand) : i === 0}
                    isTied={result.is_tied}
                  />
                ))}
              </div>

              {/* Competitive gap */}
              {!result.is_tied && Object.keys(result.competitive_gaps).length > 0 && (
                <div style={{ background: "#0a0a0a", border: "1px solid #141414", borderRadius: 10, padding: "16px 20px", marginBottom: 16 }}>
                  <p style={{ fontSize: 10, letterSpacing: 2, color: "#333", textTransform: "uppercase", margin: "0 0 12px", ...monoStyle }}>
                    Competitive Gap vs Leader
                  </p>
                  {Object.entries(result.competitive_gaps).map(([brand, gap], i, arr) => (
                    <div key={brand} style={{
                      display: "flex", justifyContent: "space-between", alignItems: "center",
                      paddingBottom: 8, marginBottom: i < arr.length - 1 ? 8 : 0,
                      borderBottom: i < arr.length - 1 ? "1px solid #151515" : "none",
                    }}>
                      <span style={{ fontSize: 13, color: "#aaa" }}>{brand}</span>
                      <span style={{ fontSize: 12, color: "#F04C7A", ...monoStyle, fontWeight: 600 }}>
                        −{Math.abs(Math.round(gap * 100))}% behind leader
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Export row */}
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={copyReport} style={{
                  flex: 1, padding: "10px 0", borderRadius: 8, fontSize: 12,
                  border: `1px solid ${copied ? "#4CF0A8" : "#222"}`,
                  background: copied ? "#4CF0A810" : "transparent",
                  color: copied ? "#4CF0A8" : "#666",
                  cursor: "pointer", ...monoStyle, transition: "all 0.15s",
                }}>
                  {copied ? "✓ Copied!" : "⎘ Copy Report"}
                </button>
                <button onClick={exportCSV} style={{
                  flex: 1, padding: "10px 0", borderRadius: 8, fontSize: 12,
                  border: "1px solid #222", background: "transparent",
                  color: "#666", cursor: "pointer", ...monoStyle, transition: "all 0.15s",
                }}
                  onMouseEnter={e => { e.target.style.borderColor = "#C8F04C"; e.target.style.color = "#C8F04C"; }}
                  onMouseLeave={e => { e.target.style.borderColor = "#222"; e.target.style.color = "#666"; }}
                >↓ Export CSV</button>
                <button onClick={exportJSON} style={{
                  flex: 1, padding: "10px 0", borderRadius: 8, fontSize: 12,
                  border: "1px solid #222", background: "transparent",
                  color: "#666", cursor: "pointer", ...monoStyle, transition: "all 0.15s",
                }}
                  onMouseEnter={e => { e.target.style.borderColor = "#4CF0A8"; e.target.style.color = "#4CF0A8"; }}
                  onMouseLeave={e => { e.target.style.borderColor = "#222"; e.target.style.color = "#666"; }}
                >↓ Export JSON</button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Run History */}
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 40px 60px" }}>
        <div style={{ borderTop: "1px solid #161616", paddingTop: 28 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: showRuns ? 20 : 0 }}>
            <div>
              <span style={{ fontSize: 11, letterSpacing: 2, color: "#444", textTransform: "uppercase", ...monoStyle }}>Pipeline Run History</span>
              <span style={{ fontSize: 11, color: "#2a2a2a", ...monoStyle }}> · persisted to SQLite</span>
            </div>
            <button onClick={showRuns ? () => setShowRuns(false) : loadRuns} style={{
              padding: "6px 16px", borderRadius: 6, fontSize: 11, border: "1px solid #222",
              background: "transparent", color: "#555", cursor: "pointer", ...monoStyle,
            }}>
              {showRuns ? "Hide" : "Show runs →"}
            </button>
          </div>

          {showRuns && runs !== null && (
            runs.length === 0
              ? <p style={{ fontSize: 12, color: "#333", ...monoStyle }}>No runs saved yet. Analyze something first.</p>
              : <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {runs.map(run => (
                    <div key={run.id} style={{
                      background: "#0c0c0c", border: "1px solid #161616", borderRadius: 10,
                      padding: "14px 18px", display: "grid",
                      gridTemplateColumns: "32px 1fr auto", gap: 16, alignItems: "start",
                    }}>
                      <span style={{ fontSize: 11, color: "#333", ...monoStyle, paddingTop: 2 }}>#{run.id}</span>
                      <div>
                        <p style={{ fontSize: 13, color: "#ccc", margin: "0 0 4px", fontFamily: "'DM Sans', sans-serif" }}>
                          {run.prompt.length > 120 ? run.prompt.slice(0, 120) + "…" : run.prompt}
                        </p>
                        <p style={{ fontSize: 11, color: "#444", margin: 0, ...monoStyle }}>
                          {run.brands.length} brand{run.brands.length !== 1 ? "s" : ""} extracted
                          {run.brands.length > 0 && <span style={{ color: "#333" }}> · {run.brands.slice(0, 5).join(", ")}{run.brands.length > 5 ? "…" : ""}</span>}
                        </p>
                      </div>
                      <span style={{ fontSize: 10, color: "#333", ...monoStyle, whiteSpace: "nowrap", paddingTop: 2 }}>
                        {new Date(run.timestamp).toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
          )}
        </div>
      </div>
    </div>
  );
}
