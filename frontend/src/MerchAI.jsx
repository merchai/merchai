import { useState, useEffect, useRef } from "react";

// ── Colour palette per rank ───────────────────────────────────────────────────
const BRAND_COLORS = [
  "#C8F04C", "#4CF0A8", "#4CC8F0", "#F0A84C",
  "#F04C7A", "#A84CF0", "#F0F04C",
];

const CONFIDENCE_COLOR = { Low: "#F04C7A", Medium: "#F0A84C", High: "#4CF0A8" };

// ── Brand extraction ──────────────────────────────────────────────────────────
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

// ── Download helper ───────────────────────────────────────────────────────────
function triggerDownload(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ── Animated number ───────────────────────────────────────────────────────────
function AnimatedNumber({ value, suffix = "", decimals = 0 }) {
  const [display, setDisplay] = useState(0);
  const raf = useRef();
  useEffect(() => {
    const start = Date.now();
    const duration = 800;
    const tick = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(value * eased);
      if (progress < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [value]);
  return <span>{decimals > 0 ? display.toFixed(decimals) : Math.round(display)}{suffix}</span>;
}

// ── Bar row ───────────────────────────────────────────────────────────────────
function BrandBar({ brand, share, count, rank, color, animate, isTop }) {
  const pct = Math.round(share * 100);
  const [width, setWidth] = useState(0);
  useEffect(() => {
    if (animate) { const t = setTimeout(() => setWidth(pct), 80 + rank * 60); return () => clearTimeout(t); }
    else setWidth(pct);
  }, [pct, animate, rank]);

  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{
            width: 22, height: 22, borderRadius: "50%",
            background: color, display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: 10, fontWeight: 700, color: "#0a0a0a", flexShrink: 0,
          }}>{rank + 1}</span>
          <span style={{ fontSize: 15, fontWeight: 600, color: "#f0f0f0", fontFamily: "'Syne', sans-serif" }}>
            {brand}
          </span>
          {isTop && <span style={{ fontSize: 12, color: "#C8F04C", lineHeight: 1 }} title="Leader">♛</span>}
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
  const [result, setResult] = useState(null);
  const [animate, setAnimate] = useState(false);
  const [activeDemo, setActiveDemo] = useState(null);
  const [inputError, setInputError] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  const runAnalysis = async (mentions, label) => {
    if (!mentions.length) { setInputError("Enter at least one brand mention."); return; }
    setInputError("");
    setApiError("");
    setResult(null);
    setLoading(true);
    setAnimate(false);
    try {
      const res = await fetch("/api/share-of-voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mentions, query_label: label }),
      });
      let data;
      try { data = await res.json(); } catch {
        throw new Error("Backend unreachable — make sure it's running on port 5000.");
      }
      if (!res.ok) throw new Error(data.error || "Request failed");
      setAnimate(true);
      setResult(data);
    } catch (err) {
      setApiError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = () => {
    const mentions = input.split(/[\n,]+/).map(extractBrand).filter(Boolean);
    runAnalysis(mentions, queryLabel);
    setActiveDemo(null);
  };

  const handleDemo = (demo, idx) => {
    setInput(demo.mentions.join("\n"));
    setQueryLabel(demo.label);
    setActiveDemo(idx);
    runAnalysis(demo.mentions, demo.label);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
  };

  const exportCSV = () => {
    if (!result) return;
    const rows = [["Brand", "Share (%)", "Mentions"]];
    result.ranked.forEach(({ brand, share }) => {
      rows.push([brand, Math.round(share * 100), result.counts[brand]]);
    });
    triggerDownload(rows.map(r => r.join(",")).join("\n"), "share-of-voice.csv", "text/csv");
  };

  const exportJSON = () => {
    if (!result) return;
    triggerDownload(JSON.stringify(result, null, 2), "share-of-voice.json", "application/json");
  };

  return (
    <div style={{
      minHeight: "100vh", background: "#080808",
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      color: "#e8e8e8",
    }}>
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
          <span style={{ fontSize: 15, fontWeight: 700, fontFamily: "'Syne', sans-serif", letterSpacing: 0.5 }}>
            MerchAI
          </span>
          <span style={{
            fontSize: 10, letterSpacing: 2, color: "#444",
            textTransform: "uppercase", marginLeft: 4, fontFamily: "'DM Mono', monospace",
          }}>Share of Voice</span>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {DEMO_QUERIES.map((d, i) => (
            <button key={i} onClick={() => handleDemo(d, i)} style={{
              padding: "6px 14px", borderRadius: 20, fontSize: 11,
              border: `1px solid ${activeDemo === i ? "#C8F04C" : "#222"}`,
              background: activeDemo === i ? "#C8F04C18" : "transparent",
              color: activeDemo === i ? "#C8F04C" : "#555",
              cursor: "pointer", fontFamily: "'DM Mono', monospace",
              transition: "all 0.2s",
            }}>
              {d.label}
            </button>
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
          <h1 style={{
            fontFamily: "'Syne', sans-serif", fontSize: 28, fontWeight: 800,
            lineHeight: 1.2, margin: "0 0 8px", letterSpacing: -0.5,
          }}>
            Measure brand<br />
            <span style={{ color: "#C8F04C" }}>visibility</span> in AI
          </h1>
          <p style={{ fontSize: 13, color: "#444", margin: "0 0 28px", lineHeight: 1.6 }}>
            Paste brand mentions extracted from an AI response. The engine calculates each brand's share of voice instantly.
          </p>

          {/* Query label */}
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 10, letterSpacing: 2, color: "#444", textTransform: "uppercase", display: "block", marginBottom: 6, fontFamily: "'DM Mono', monospace" }}>
              Query / Campaign
            </label>
            <input
              value={queryLabel}
              onChange={e => setQueryLabel(e.target.value)}
              placeholder='e.g. "best running shoes 2025"'
              style={{
                width: "100%", boxSizing: "border-box",
                background: "#111", border: "1px solid #1e1e1e",
                borderRadius: 8, padding: "10px 14px",
                color: "#e0e0e0", fontSize: 13, outline: "none",
                fontFamily: "'DM Sans', sans-serif",
              }}
            />
          </div>

          {/* Mentions textarea */}
          <div style={{ marginBottom: 6 }}>
            <label style={{ fontSize: 10, letterSpacing: 2, color: "#444", textTransform: "uppercase", display: "block", marginBottom: 6, fontFamily: "'DM Mono', monospace" }}>
              Brand Mentions
            </label>
            <textarea
              value={input}
              onChange={e => { setInput(e.target.value); setInputError(""); }}
              onKeyDown={handleKeyDown}
              placeholder={"Nike\nAdidas\nNike\nPuma\n\nor comma-separated…"}
              rows={9}
              style={{
                width: "100%", boxSizing: "border-box",
                background: "#111", border: `1px solid ${inputError ? "#F04C7A" : "#1e1e1e"}`,
                borderRadius: 8, padding: "12px 14px", resize: "vertical",
                color: "#ccc", fontSize: 13, lineHeight: 1.8, outline: "none",
                fontFamily: "'DM Mono', monospace",
              }}
            />
          </div>
          {inputError && <p style={{ fontSize: 12, color: "#F04C7A", margin: "0 0 8px" }}>{inputError}</p>}
          <p style={{ fontSize: 11, color: "#333", margin: "0 0 20px", fontFamily: "'DM Mono', monospace" }}>
            One per line or comma-separated · ⌘↵ to run
          </p>

          <button onClick={handleSubmit} disabled={loading} style={{
            width: "100%", padding: "13px 0",
            background: loading ? "#3a4a14" : "#C8F04C", color: "#0a0a0a",
            border: "none", borderRadius: 8, fontSize: 14, fontWeight: 700,
            fontFamily: "'Syne', sans-serif", cursor: loading ? "default" : "pointer",
            letterSpacing: 0.3, transition: "all 0.15s",
          }}
            onMouseEnter={e => { if (!loading) e.target.style.opacity = "0.88"; }}
            onMouseLeave={e => { e.target.style.opacity = "1"; }}
          >
            {loading ? "Analyzing…" : "Compute Share of Voice →"}
          </button>
        </div>

        {/* Right — Results panel */}
        <div style={{ minHeight: 400 }}>
          {loading && (
            <div style={{
              height: 400, display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center", gap: 12, color: "#333",
            }}>
              <div style={{ fontSize: 32, animation: "spin 1.2s linear infinite" }}>◌</div>
              <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
              <p style={{ fontSize: 13, fontFamily: "'DM Mono', monospace" }}>Analyzing mentions…</p>
            </div>
          )}

          {!loading && apiError && (
            <div style={{
              height: 400, display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center", gap: 8,
              border: "1px dashed #2a1a1a", borderRadius: 12, color: "#F04C7A",
            }}>
              <div style={{ fontSize: 28 }}>⚠</div>
              <p style={{ fontSize: 13, fontFamily: "'DM Mono', monospace", textAlign: "center", maxWidth: 280 }}>
                {apiError}
              </p>
              <p style={{ fontSize: 11, color: "#444", fontFamily: "'DM Mono', monospace" }}>
                Is the backend running on port 5000?
              </p>
            </div>
          )}

          {!loading && !apiError && !result && (
            <div style={{
              height: 400, display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center", gap: 12,
              border: "1px dashed #1a1a1a", borderRadius: 12, color: "#2a2a2a",
            }}>
              <div style={{ fontSize: 40 }}>◎</div>
              <p style={{ fontSize: 13, fontFamily: "'DM Mono', monospace" }}>
                Results will appear here
              </p>
            </div>
          )}

          {!loading && result && (
            <div style={{ animation: "fadeIn 0.4s ease" }}>
              <style>{`@keyframes fadeIn { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:translateY(0) } }`}</style>

              {/* Result header */}
              <div style={{ marginBottom: 24 }}>
                {result.query_label && (
                  <h2 style={{
                    fontFamily: "'Syne', sans-serif", fontSize: 17, fontWeight: 700,
                    margin: "0 0 4px", color: "#e8e8e8",
                  }}>
                    "{result.query_label}"
                  </h2>
                )}
                <p style={{ fontSize: 12, color: "#444", fontFamily: "'DM Mono', monospace", margin: 0 }}>
                  {result.total_mentions} mention{result.total_mentions !== 1 ? "s" : ""} analyzed
                  {" · "}{result.brand_count} brand{result.brand_count !== 1 ? "s" : ""} detected
                </p>
              </div>

              {/* Visibility summary — 5 stat cards */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8, marginBottom: 20 }}>
                {[
                  { label: "Top Brand", value: result.top_brand, raw: true },
                  { label: "Top Share", value: Math.round((result.top_share ?? 0) * 100), suffix: "%" },
                  { label: "Mentions", value: result.total_mentions },
                  { label: "Brands", value: result.brand_count },
                  {
                    label: "Confidence",
                    value: result.confidence_level,
                    raw: true,
                    color: CONFIDENCE_COLOR[result.confidence_level],
                  },
                ].map(({ label, value, suffix = "", raw, color }) => (
                  <div key={label} style={{
                    background: "#0e0e0e", border: "1px solid #1a1a1a",
                    borderRadius: 10, padding: "12px 14px",
                  }}>
                    <p style={{ fontSize: 9, color: "#444", textTransform: "uppercase", letterSpacing: 2, margin: "0 0 5px", fontFamily: "'DM Mono', monospace" }}>{label}</p>
                    {raw ? (
                      <p style={{ fontSize: 13, fontWeight: 700, margin: 0, fontFamily: "'Syne', sans-serif", color: color || "#C8F04C", lineHeight: 1.2, wordBreak: "break-word" }}>
                        {value}
                      </p>
                    ) : (
                      <p style={{ fontSize: 22, fontWeight: 800, margin: 0, fontFamily: "'Syne', sans-serif", color: "#C8F04C" }}>
                        <AnimatedNumber value={value} suffix={suffix} />
                      </p>
                    )}
                  </div>
                ))}
              </div>

              {/* Insight */}
              {result.generated_insight && (
                <div style={{
                  marginBottom: 20, background: "#0c0f08",
                  border: "1px solid #1e2812", borderRadius: 10, padding: "14px 18px",
                }}>
                  <p style={{ fontSize: 9, letterSpacing: 2, color: "#3a4a20", textTransform: "uppercase", margin: "0 0 6px", fontFamily: "'DM Mono', monospace" }}>
                    AI Insight
                  </p>
                  <p style={{ fontSize: 13, color: "#a0b870", margin: 0, lineHeight: 1.65, fontFamily: "'DM Sans', sans-serif" }}>
                    {result.generated_insight}
                  </p>
                </div>
              )}

              {/* Brand bars */}
              <div style={{
                background: "#0c0c0c", border: "1px solid #161616",
                borderRadius: 12, padding: "24px 28px", marginBottom: 16,
              }}>
                <p style={{ fontSize: 10, letterSpacing: 2, color: "#333", textTransform: "uppercase", margin: "0 0 20px", fontFamily: "'DM Mono', monospace" }}>
                  Share of Voice Distribution
                </p>
                {result.ranked.map(({ brand, share }, i) => (
                  <BrandBar
                    key={brand} brand={brand} share={share}
                    count={result.counts[brand]}
                    rank={i} color={BRAND_COLORS[i % BRAND_COLORS.length]}
                    animate={animate} isTop={i === 0}
                  />
                ))}
              </div>

              {/* Competitive gap */}
              {Object.keys(result.competitive_gaps).length > 0 && (
                <div style={{
                  background: "#0a0a0a", border: "1px solid #141414",
                  borderRadius: 10, padding: "16px 20px", marginBottom: 16,
                }}>
                  <p style={{ fontSize: 10, letterSpacing: 2, color: "#333", textTransform: "uppercase", margin: "0 0 12px", fontFamily: "'DM Mono', monospace" }}>
                    Competitive Gap vs Leader
                  </p>
                  {Object.entries(result.competitive_gaps).map(([brand, gap]) => (
                    <div key={brand} style={{
                      display: "flex", justifyContent: "space-between",
                      alignItems: "center", paddingBottom: 8, marginBottom: 8,
                      borderBottom: "1px solid #151515",
                    }}>
                      <span style={{ fontSize: 13, color: "#aaa", fontFamily: "'DM Sans', sans-serif" }}>{brand}</span>
                      <span style={{ fontSize: 12, color: "#F04C7A", fontFamily: "'DM Mono', monospace", fontWeight: 600 }}>
                        −{Math.abs(Math.round(gap * 100))}% behind leader
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Export */}
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={exportCSV} style={{
                  flex: 1, padding: "10px 0", borderRadius: 8, fontSize: 12,
                  border: "1px solid #222", background: "transparent",
                  color: "#666", cursor: "pointer", fontFamily: "'DM Mono', monospace",
                  transition: "all 0.15s",
                }}
                  onMouseEnter={e => { e.target.style.borderColor = "#C8F04C"; e.target.style.color = "#C8F04C"; }}
                  onMouseLeave={e => { e.target.style.borderColor = "#222"; e.target.style.color = "#666"; }}
                >
                  ↓ Export CSV
                </button>
                <button onClick={exportJSON} style={{
                  flex: 1, padding: "10px 0", borderRadius: 8, fontSize: 12,
                  border: "1px solid #222", background: "transparent",
                  color: "#666", cursor: "pointer", fontFamily: "'DM Mono', monospace",
                  transition: "all 0.15s",
                }}
                  onMouseEnter={e => { e.target.style.borderColor = "#4CF0A8"; e.target.style.color = "#4CF0A8"; }}
                  onMouseLeave={e => { e.target.style.borderColor = "#222"; e.target.style.color = "#666"; }}
                >
                  ↓ Export JSON
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
