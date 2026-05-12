import { useCallback, useEffect, useRef, useState } from "react";

/** Dev: set VITE_API_URL in .env.development (e.g. http://127.0.0.1:8000). Prod build: leave unset → same-origin /api. */
const API_BASE = String(import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
const apiUrl = (path) => (API_BASE ? `${API_BASE}${path}` : path);
const wsKbUrl = () => {
  if (API_BASE) {
    return `${API_BASE.replace(/^http/, "ws")}/ws/kb`;
  }
  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  return `${proto}://${window.location.host}/ws/kb`;
};

const api = (path, opts = {}) =>
  fetch(apiUrl(path), { ...opts, headers: { ...opts.headers } }).then(async (r) => {
    if (!r.ok) {
      let detail = r.statusText;
      try {
        const body = await r.json();
        if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      } catch {
        /* ignore */
      }
      throw new Error(detail || r.statusText);
    }
    return r.json();
  });

const BUCKET_KEYS = ["behavioural", "environmental", "time", "vehicle", "location"];

const btnPrimary =
  "inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-45";
const btnSecondary =
  "inline-flex items-center justify-center gap-2 rounded-xl border border-zinc-300 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-800 shadow-sm transition hover:bg-zinc-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-offset-2 disabled:opacity-45";
const btnAccent =
  "inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 disabled:opacity-45";

export default function App() {
  const [files, setFiles] = useState([]);
  const [stats, setStats] = useState(null);
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(null);
  const [log, setLog] = useState([]);
  const [showLog, setShowLog] = useState(false);
  const wsRef = useRef(null);

  const pushLog = useCallback((line) => {
    setLog((prev) => [...prev.slice(-120), `${new Date().toLocaleTimeString()} — ${line}`]);
  }, []);

  const refreshFiles = useCallback(() => {
    api("/api/kb/files")
      .then((d) => setFiles(d.files || []))
      .catch(() => pushLog("Could not load file list"));
  }, [pushLog]);

  const refreshStats = useCallback(() => {
    api("/api/kb/stats")
      .then(setStats)
      .catch(() => setStats(null));
  }, []);

  const runSync = useCallback(async () => {
    try {
      const r = await api("/api/kb/sync");
      pushLog(`Synced folder (${r.txt_files_on_disk ?? 0} .txt on disk)`);
      refreshFiles();
    } catch {
      pushLog("Sync failed");
    }
  }, [pushLog, refreshFiles]);

  useEffect(() => {
    refreshFiles();
    refreshStats();
  }, [refreshFiles, refreshStats]);

  const onUpload = async (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const fd = new FormData();
    fd.append("file", f);
    setBusy(true);
    try {
      await api("/api/kb/upload", { method: "POST", body: fd });
      pushLog(`Saved ${f.name} → backend/knowledge/`);
      refreshFiles();
    } catch {
      pushLog("Upload failed");
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  };

  const removeFile = async (filename) => {
    if (!window.confirm(`Remove “${filename}” from the knowledge folder?`)) return;
    setBusy(true);
    try {
      const q = new URLSearchParams({ filename });
      await api(`/api/kb/files?${q.toString()}`, { method: "DELETE" });
      pushLog(`Removed ${filename}`);
      refreshFiles();
      refreshStats();
    } catch {
      pushLog("Delete failed");
    } finally {
      setBusy(false);
    }
  };

  const runAnalyzeHttp = async () => {
    setBusy(true);
    setProgress(null);
    try {
      const res = await api("/api/kb/analyze-all", { method: "POST" });
      setStats(res.stats);
      pushLog("NLP run finished — stats saved to local DB");
      refreshFiles();
    } catch {
      pushLog("Analyze failed");
    } finally {
      setBusy(false);
    }
  };

  const runAnalyzeWs = () => {
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch {
        /* ignore */
      }
    }
    const ws = new WebSocket(wsKbUrl());
    wsRef.current = ws;
    setBusy(true);
    setProgress({ index: 0, total: 0, name: "Connecting…" });
    pushLog("WebSocket batch started");

    ws.onopen = () => {
      ws.send(JSON.stringify({ action: "analyze_all" }));
    };

    ws.onmessage = (ev) => {
      let msg;
      try {
        msg = JSON.parse(ev.data);
      } catch {
        return;
      }
      if (msg.type === "progress") {
        setProgress({
          index: msg.index,
          total: msg.total,
          name: msg.name || "",
        });
      }
      if (msg.type === "stats" && msg.stats) {
        setStats(msg.stats);
      }
      if (msg.type === "complete" && msg.stats) {
        setStats(msg.stats);
        setProgress(null);
        setBusy(false);
        pushLog(`Complete — ${msg.stats.document_count} docs in aggregate (SQLite)`);
        refreshFiles();
        ws.close();
      }
      if (msg.type === "error") {
        pushLog(`Error: ${msg.message}`);
        setBusy(false);
        setProgress(null);
      }
    };

    ws.onerror = () => {
      pushLog("WebSocket error");
      setBusy(false);
      setProgress(null);
    };

    ws.onclose = () => {
      wsRef.current = null;
    };
  };

  const kwEntries = stats?.keyword_counts ? Object.entries(stats.keyword_counts).slice(0, 28) : [];
  const pct =
    progress && progress.total > 0 ? Math.round((100 * progress.index) / progress.total) : 0;
  const sources = Array.isArray(stats?.source_documents) ? stats.source_documents : [];

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-100 to-zinc-200/80">
      <header className="border-b border-zinc-200/80 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-8 md:flex-row md:items-end md:justify-between md:px-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600">Corpus NLP</p>
            <h1 className="mt-1 text-2xl font-bold tracking-tight text-zinc-900 md:text-3xl">
              Accident knowledge base
            </h1>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-zinc-600">
              Drop <code className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs font-mono text-zinc-800">.txt</code>{" "}
              files into <span className="font-mono text-xs">backend/knowledge/</span> or upload here. Runs are
              persisted in <span className="font-mono text-xs">data/kb.sqlite</span> and drive calibration in{" "}
              <code className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs">POST /api/assess</code>.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" className={btnSecondary} disabled={busy} onClick={runSync}>
              Scan folder
            </button>
            <button
              type="button"
              className={btnSecondary}
              disabled={busy}
              onClick={() => {
                refreshFiles();
                refreshStats();
              }}
            >
              Refresh
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-8 px-4 py-8 md:px-8">
        <section className="rounded-2xl border border-zinc-200/80 bg-white p-6 shadow-soft">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold text-zinc-900">Corpus files</h2>
              <p className="text-sm text-zinc-500">Only non-empty .txt files are included in NLP batches.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <label className={`${btnPrimary} cursor-pointer`}>
                <input type="file" accept=".txt,text/plain" className="sr-only" disabled={busy} onChange={onUpload} />
                Upload .txt
              </label>
              <button type="button" className={btnAccent} disabled={busy} onClick={runAnalyzeWs}>
                Run NLP (live)
              </button>
              <button type="button" className={btnSecondary} disabled={busy} onClick={runAnalyzeHttp}>
                Run NLP (sync)
              </button>
            </div>
          </div>

          {progress && progress.total > 0 && (
            <div className="mt-6 space-y-2">
              <div className="flex justify-between text-xs font-medium text-zinc-600">
                <span className="truncate pr-2">
                  {progress.index}/{progress.total} — {progress.name}
                </span>
                <span>{pct}%</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-zinc-100">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-indigo-500 transition-all duration-300"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          )}

          <ul className="mt-6 divide-y divide-zinc-100 rounded-xl border border-zinc-100">
            {files.length === 0 && (
              <li className="px-4 py-10 text-center text-sm text-zinc-500">
                No .txt files detected. Add files under <span className="font-mono">knowledge/</span> or upload.
              </li>
            )}
            {files.map((f) => (
              <li
                key={f.filename}
                className="flex flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium text-zinc-900">{f.filename}</p>
                  <p className="mt-0.5 text-xs text-zinc-500">
                    {f.char_count?.toLocaleString?.() ?? f.char_count} chars
                    {f.last_nlp_at ? (
                      <>
                        {" "}
                        · last NLP{" "}
                        <time className="font-mono text-zinc-600">{f.last_nlp_at.slice(0, 19)}</time>
                      </>
                    ) : (
                      " · not analyzed yet"
                    )}
                  </p>
                </div>
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => removeFile(f.filename)}
                  className="shrink-0 rounded-lg px-3 py-1.5 text-sm font-semibold text-red-600 transition hover:bg-red-50"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-2xl border border-zinc-200/80 bg-white p-6 shadow-soft">
          <div className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between">
            <h2 className="text-lg font-semibold text-zinc-900">Latest aggregate NLP</h2>
            {stats?.aggregate_run_id != null && (
              <span className="text-xs font-medium text-zinc-400">Run #{stats.aggregate_run_id}</span>
            )}
          </div>

          {!stats || stats.document_count === 0 ? (
            <p className="mt-4 text-sm leading-relaxed text-zinc-600">
              No saved aggregate yet. Run NLP on your corpus to populate SQLite and unlock calibration weights for the
              risk API.
            </p>
          ) : (
            <div className="mt-6 space-y-8">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-xl border border-zinc-100 bg-zinc-50/80 p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Documents</p>
                  <p className="mt-1 text-3xl font-bold tabular-nums text-zinc-900">{stats.document_count}</p>
                </div>
                <div className="rounded-xl border border-zinc-100 bg-zinc-50/80 p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Keyword hits</p>
                  <p className="mt-1 text-3xl font-bold tabular-nums text-zinc-900">{stats.total_keyword_hits}</p>
                </div>
                <div className="rounded-xl border border-zinc-100 bg-zinc-50/80 p-4 sm:col-span-2">
                  <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">Run timestamp</p>
                  <p className="mt-1 font-mono text-sm text-zinc-800">{stats.analyzed_at || "—"}</p>
                </div>
              </div>

              {sources.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-zinc-800">Documents in this aggregate</h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {sources.map((name) => (
                      <span
                        key={name}
                        className="inline-flex max-w-full items-center truncate rounded-lg border border-indigo-100 bg-indigo-50/80 px-2.5 py-1 text-xs font-medium text-indigo-900"
                      >
                        {name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="text-sm font-semibold text-zinc-800">Category prevalence</h3>
                <p className="mt-0.5 text-xs text-zinc-500">Share of documents where each dimension had signal.</p>
                <div className="mt-4 space-y-3">
                  {BUCKET_KEYS.map((k) => {
                    const v = (stats.category_doc_share && stats.category_doc_share[k]) || 0;
                    return (
                      <div key={k}>
                        <div className="mb-1 flex justify-between text-xs font-medium text-zinc-600">
                          <span className="capitalize">{k}</span>
                          <span className="tabular-nums">{(100 * v).toFixed(1)}%</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-zinc-100">
                          <div
                            className="h-full rounded-full bg-indigo-500 transition-all"
                            style={{ width: `${Math.min(100, 100 * v)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-zinc-800">Mean bucket intensity (0–1)</h3>
                <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-5">
                  {BUCKET_KEYS.map((k) => (
                    <div
                      key={k}
                      className="rounded-xl border border-zinc-100 bg-gradient-to-b from-white to-zinc-50 p-3 text-center"
                    >
                      <div className="text-[10px] font-semibold uppercase tracking-wide text-zinc-500">{k}</div>
                      <div className="mt-1 text-lg font-bold tabular-nums text-zinc-900">
                        {(stats.avg_bucket_scores && stats.avg_bucket_scores[k])?.toFixed(2) ?? "0"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-zinc-800">Top keywords</h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {kwEntries.map(([w, c]) => (
                    <span
                      key={w}
                      className="rounded-full border border-amber-100 bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-950"
                    >
                      {w} <span className="tabular-nums text-amber-700/90">({c})</span>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-zinc-800 bg-zinc-900 text-zinc-200 shadow-soft">
          <button
            type="button"
            onClick={() => setShowLog((s) => !s)}
            className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-semibold text-white md:px-6"
          >
            Activity log
            <span className="text-xs font-normal text-zinc-400">{showLog ? "Hide" : "Show"}</span>
          </button>
          {showLog && (
            <div className="max-h-52 overflow-y-auto border-t border-zinc-800 px-4 py-3 font-mono text-xs leading-relaxed text-zinc-300 md:px-6">
              {log.length === 0 ? <p className="text-zinc-500">No events yet.</p> : log.map((l, i) => <div key={i}>{l}</div>)}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
