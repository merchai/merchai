import { useState, useEffect, useRef } from "react";

// ── Colour palette per rank ───────────────────────────────────────────────────
const BRAND_COLORS = [
  "#C8F04C", "#4CF0A8", "#4CC8F0", "#F0A84C",
  "#F04C7A", "#A84CF0", "#F0F04C",
];

// ── Pure JS mirror of the Python backend ─────────────────────────────────────
function computeShareOfVoice(mentions) {
  const counts = {};
  const display = {};
  for (const item of mentions) {
    const key = item.trim().toLowerCase();
    if (!key) continue;
    if (!(key in counts)) { counts[key] = 0; display[key] = item.trim(); }
    counts[key]++;
  }
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  if (total === 0) return { shares: {}, counts: {}, total: 0, ranked: [], top_brand: null };
  const shares = {};
  const displayCounts = {};
  for (const k of Object.keys(counts)) {
    shares[display[k]] = Math.round((counts[k] / total) * 100) / 100;
    displayCounts[display[k]] = counts[k];
  }
  const ranked = Object.entries(shares).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  return { shares, counts: displayCounts, total, ranked, top_brand: ranked[0]?.[0] ?? null };
}

const DEMO_QUERIES = [
  { label: "Best running shoes", mentions: ["Nike", "Adidas", "Nike", "Brooks", "Nike", "Adidas", "New Balance", "Nike", "Adidas", "Brooks"] },
  { label: "Luxury handbags", mentions: ["Louis Vuitton", "Gucci", "Louis Vuitton", "Chanel", "Gucci", "Louis Vuitton", "Hermès", "Chanel"] },
  { label: "Smartphone comparison", mentions: ["Apple", "Samsung", "Apple", "Google", "Apple", "Samsung", "Apple", "OnePlus", "Samsung"] },
];

// ── Animated number ───────────────────────────────────────────────────────────
function AnimatedNumber({ value, suffix = "", decimals = 0 }) {
  const [display, setDisplay] = useState(0);
  const raf = useRef();
  useEffect(() => {
    const start = Date.now();
    const duration = 800;
    const from = 0;
    const to = value;
    const tick = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(from + (to - from) * eased);
      if (progress < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [value]);
  return <span>{decimals > 0 ? display.toFixed(decimals) : Math.round(display)}{suffix}</span>;
}

// ── Bar row ───────────────────────────────────────────────────────────────────
function BrandBar({ brand, share, count, total, rank, color, animate }) {
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
            justifyContent: "center", fontSize: 10, fontWeight: 700, color: "#0a0a0a", flexShrink: 0
          }}>{rank + 1}</span>
          <span style={{ fontSize: 15, fontWeight: 600, color: "#f0f0f0", fontFamily: "'Syne', sans-serif" }}>{brand}</span>
        </div>
        <div style={{ display: "flex", gap: 16, alignItems: "baseline" }}>
          <span style={{ fontSize: 12, color: "#555", fontFamily: "monospace" }}>{count} mention{count !== 1 ? "s" : ""}</span>
          <span style={{ fontSize: 18, fontWeight: 700, color, fontFamily: "monospace", minWidth: 48, textAlign: "right" }}>
            {animate ? <AnimatedNumber value={pct} suffix="%" /> : `${pct}%`}
          </span>
        </div>
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

  const runAnalysis = (mentions, label) => {
    if (!mentions.length) { setInputError("Enter at least one brand mention."); return; }
    setInputError("");
    setResult(null);
    setTimeout(() => {
      setAnimate(true);
      setResult(computeShareOfVoice(mentions));
    }, 50);
  };

  const handleSubmit = () => {
    const mentions = input.split(/[\n,]+/).map(s => s.trim()).filter(Boolean);
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
            textTransform: "uppercase", marginLeft: 4, fontFamily: "'DM Mono', monospace"
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

          <button onClick={handleSubmit} style={{
            width: "100%", padding: "13px 0",
            background: "#C8F04C", color: "#0a0a0a",
            border: "none", borderRadius: 8, fontSize: 14, fontWeight: 700,
            fontFamily: "'Syne', sans-serif", cursor: "pointer", letterSpacing: 0.3,
            transition: "opacity 0.15s",
          }}
            onMouseEnter={e => e.target.style.opacity = "0.88"}
            onMouseLeave={e => e.target.style.opacity = "1"}
          >
            Compute Share of Voice →
          </button>

          {/* Code callout */}
          <div style={{
            marginTop: 24, background: "#0e0e0e", border: "1px solid #1a1a1a",
            borderRadius: 8, padding: "14px 16px",
          }}>
            <p style={{ fontSize: 10, letterSpacing: 2, color: "#333", textTransform: "uppercase", margin: "0 0 8px", fontFamily: "'DM Mono', monospace" }}>
              Powered by
            </p>
            <code style={{ fontSize: 12, color: "#4CF0A8", fontFamily: "'DM Mono', monospace", lineHeight: 1.7 }}>
              src/metrics/share_of_voice.py<br />
              <span style={{ color: "#555" }}>→</span> compute_share_of_voice(mentions)
            </code>
          </div>
        </div>

        {/* Right — Results panel */}
        <div style={{ minHeight: 400 }}>
          {!result ? (
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
          ) : (
            <div style={{ animation: "fadeIn 0.4s ease" }}>
              <style>{`@keyframes fadeIn { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:translateY(0) } }`}</style>

              {/* Stats row */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 28 }}>
                {[
                  { label: "Total Mentions", value: result.total, suffix: "", decimals: 0 },
                  { label: "Brands Detected", value: result.ranked.length, suffix: "", decimals: 0 },
                  { label: "Top Share", value: Math.round((result.ranked[0]?.[1] ?? 0) * 100), suffix: "%", decimals: 0 },
                ].map(({ label, value, suffix, decimals }) => (
                  <div key={label} style={{
                    background: "#0e0e0e", border: "1px solid #1a1a1a",
                    borderRadius: 10, padding: "16px 20px",
                  }}>
                    <p style={{ fontSize: 10, color: "#444", textTransform: "uppercase", letterSpacing: 2, margin: "0 0 6px", fontFamily: "'DM Mono', monospace" }}>{label}</p>
                    <p style={{ fontSize: 28, fontWeight: 800, margin: 0, fontFamily: "'Syne', sans-serif", color: "#C8F04C" }}>
                      <AnimatedNumber value={value} suffix={suffix} decimals={decimals} />
                    </p>
                  </div>
                ))}
              </div>

              {/* Query label */}
              {queryLabel && (
                <p style={{ fontSize: 12, color: "#444", fontFamily: "'DM Mono', monospace", marginBottom: 20 }}>
                  Query: <span style={{ color: "#666" }}>"{queryLabel}"</span>
                </p>
              )}

              {/* Brand bars */}
              <div style={{
                background: "#0c0c0c", border: "1px solid #161616",
                borderRadius: 12, padding: "24px 28px",
              }}>
                <p style={{ fontSize: 10, letterSpacing: 2, color: "#333", textTransform: "uppercase", margin: "0 0 20px", fontFamily: "'DM Mono', monospace" }}>
                  Share of Voice Distribution
                </p>
                {result.ranked.map(([brand, share], i) => (
                  <BrandBar
                    key={brand} brand={brand} share={share}
                    count={result.counts[brand]} total={result.total}
                    rank={i} color={BRAND_COLORS[i % BRAND_COLORS.length]}
                    animate={animate}
                  />
                ))}
              </div>

              {/* Raw output */}
              <div style={{
                marginTop: 16, background: "#0a0a0a", border: "1px solid #141414",
                borderRadius: 10, padding: "16px 20px",
              }}>
                <p style={{ fontSize: 10, letterSpacing: 2, color: "#2a2a2a", textTransform: "uppercase", margin: "0 0 10px", fontFamily: "'DM Mono', monospace" }}>
                  Raw Output  <span style={{ color: "#1e1e1e" }}>· compute_share_of_voice()</span>
                </p>
                <pre style={{ margin: 0, fontSize: 12, color: "#3a3a3a", fontFamily: "'DM Mono', monospace", lineHeight: 1.7, overflowX: "auto" }}>
                  <span style={{ color: "#4CF0A8" }}>{JSON.stringify(result.shares, null, 2)}</span>
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}