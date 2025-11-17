import { useState } from "react";

export default function Home() {
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  // In a real app, replace this with real metric data from your dashboard.
  const metricsText =
    "Total users: 12,430 (+8% WoW); Active subscriptions: 3,210 (+3% MoM); Churn rate: 2.1% (-0.4pp MoM); NPS: 47; Avg. response time: 320ms (-10% WoW).";

  const handleSummarize = async () => {
    try {
      setIsSummarizing(true);
      setError(null);
      setShowModal(true);

      const res = await fetch("/api/summarize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ metrics: metricsText }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Failed to summarize metrics.");
      }

      setSummary(data.summary);
    } catch (err: any) {
      setError(err.message || "Unexpected error while summarizing.");
    } finally {
      setIsSummarizing(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-zinc-50 font-sans dark:bg-black">
      <main className="relative flex min-h-screen w-full flex-col gap-8 p-8">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold tracking-tight text-black dark:text-zinc-50">
            Dashboard
          </h1>
          <button
            onClick={handleSummarize}
            disabled={isSummarizing}
            className="rounded-md bg-black px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-zinc-50 dark:text-black dark:hover:bg-zinc-200"
          >
            {isSummarizing ? "Summarizing..." : "Summarize"}
          </button>
        </header>

        {/* Placeholder metrics section */}
        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <h2 className="text-sm font-medium text-zinc-500">Total Users</h2>
            <p className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
              12,430
            </p>
            <p className="mt-1 text-xs text-emerald-600">+8% WoW</p>
          </div>
          <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <h2 className="text-sm font-medium text-zinc-500">
              Active Subscriptions
            </h2>
            <p className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
              3,210
            </p>
            <p className="mt-1 text-xs text-emerald-600">+3% MoM</p>
          </div>
          <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
            <h2 className="text-sm font-medium text-zinc-500">Churn Rate</h2>
            <p className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
              2.1%
            </p>
            <p className="mt-1 text-xs text-emerald-600">-0.4pp MoM</p>
          </div>
        </section>

        {/* Summary Modal */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
            <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-lg dark:bg-zinc-900">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
                  Metrics Summary
                </h2>
                <button
                  className="text-sm text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200"
                  onClick={() => setShowModal(false)}
                >
                  Close
                </button>
              </div>

              {isSummarizing && (
                <p className="text-sm text-zinc-500">
                  Generating summary with gpt-5.1...
                </p>
              )}

              {error && (
                <p className="text-sm text-red-600 dark:text-red-400">
                  {error}
                </p>
              )}

              {summary && !isSummarizing && !error && (
                <div className="mt-2 whitespace-pre-wrap text-sm text-zinc-800 dark:text-zinc-100">
                  {summary}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

