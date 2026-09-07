"use client";

import { FormEvent, useState } from "react";

type Source = {
  title?: string;
  source_type?: string;
  source_id?: string;
  chunk_index?: number;
  similarity?: number;
};

type Retrieval = {
  status?: string;
  best_similarity?: number;
  chunks_retrieved?: number;
};

type AskResponse = {
  answer: string;
  sources: Source[];
  retrieval?: Retrieval;
};

export default function Home() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function askQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const apiUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

      const response = await fetch(`${apiUrl}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail?.message ||
            errorData?.detail ||
            `Request failed with status ${response.status}`
        );
      }

      const data: AskResponse = await response.json();

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Terjadi kesalahan saat menghubungi backend."
      );
    } finally {
      setLoading(false);
    }
  }

  function useExample(text: string) {
    setQuestion(text);
    setResult(null);
    setError("");
  }

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f]">
      <div className="mx-auto min-h-screen max-w-5xl px-5 pb-16 sm:px-8">
        {/* Apple-style header */}
        <header className="pt-10 sm:pt-16">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-[11px] bg-[#1d1d1f] text-sm text-white shadow-sm">
              ✦
            </div>
            <span className="text-sm font-medium text-[#6e6e73]">
              Internal Knowledge
            </span>
          </div>

          <h1 className="mt-8 max-w-3xl text-5xl font-semibold tracking-[-0.055em] sm:text-6xl">
            Knowledge Assistant.
          </h1>

          <p className="mt-5 max-w-2xl text-lg leading-7 tracking-[-0.01em] text-[#6e6e73] sm:text-xl">
            Ask anything about company policies, procedures, and internal
            knowledge. Get clear answers grounded in your knowledge base.
          </p>
        </header>

        {/* Search / Ask */}
        <section className="mt-10 rounded-[30px] border border-black/4 bg-white p-4 shadow-[0_20px_60px_rgba(0,0,0,0.08)] sm:p-6">
          <form onSubmit={askQuestion}>
            <label
              htmlFor="question"
              className="mb-3 block px-1 text-sm font-medium text-[#6e6e73]"
            >
              Ask your question
            </label>

            <div className="rounded-[22px] border border-black/6 bg-[#f5f5f7] transition focus-within:border-[#8e8e93] focus-within:bg-white focus-within:ring-4 focus-within:ring-black/4">
              <textarea
                id="question"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Who approves expenses above $70?"
                rows={4}
                className="w-full resize-none rounded-[22px] bg-transparent px-5 py-4 text-[16px] leading-7 text-[#1d1d1f] outline-none placeholder:text-[#86868b]"
              />

              <div className="flex items-center justify-between px-4 pb-3">
                <span className="text-xs text-[#86868b]">
                  Gemini · Supabase pgvector
                </span>

                <button
                  type="submit"
                  disabled={loading}
                  className="rounded-full bg-[#0071e3] px-5 py-2.5 text-sm font-medium text-white transition hover:bg-[#0077ed] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? "Thinking…" : "Ask"}
                </button>
              </div>
            </div>
          </form>

          {/* Suggested questions */}
          <div className="mt-6">
            <p className="mb-3 px-1 text-xs font-medium uppercase tracking-[0.08em] text-[#86868b]">
              Suggested questions
            </p>

            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => useExample("Who approves expenses above $70?")}
                className="rounded-full border border-black/7 bg-white px-4 py-2.5 text-sm text-[#424245] shadow-sm transition hover:bg-[#f5f5f7]"
              >
                Expense approval
              </button>

              <button
                type="button"
                onClick={() =>
                  useExample(
                    "How long do employees have to submit reimbursement claims?"
                  )
                }
                className="rounded-full border border-black/7 bg-white px-4 py-2.5 text-sm text-[#424245] shadow-sm transition hover:bg-[#f5f5f7]"
              >
                Reimbursement
              </button>

              <button
                type="button"
                onClick={() => useExample("Who approves expenses above $2,000?")}
                className="rounded-full border border-black/7 bg-white px-4 py-2.5 text-sm text-[#424245] shadow-sm transition hover:bg-[#f5f5f7]"
              >
                Unknown information
              </button>

              <button
                type="button"
                onClick={() =>
                  useExample("What is the company's maternity leave policy?")
                }
                className="rounded-full border border-black/7 bg-white px-4 py-2.5 text-sm text-[#424245] shadow-sm transition hover:bg-[#f5f5f7]"
              >
                Maternity leave
              </button>
            </div>
          </div>
        </section>

        {/* Error */}
        {error && (
          <section className="mt-6 rounded-3xl border border-red-500/10 bg-[#fff2f2] p-5">
            <h2 className="font-semibold text-[#d70015]">Request Error</h2>
            <p className="mt-1.5 text-sm leading-6 text-[#8e1b1b]">{error}</p>
          </section>
        )}

        {/* Result */}
        {result && (
          <section className="mt-8 space-y-5">
            {/* Answer */}
            <div className="rounded-[30px] border border-black/4 bg-white p-6 shadow-[0_12px_40px_rgba(0,0,0,0.05)] sm:p-8">
              <div className="flex items-start justify-between gap-5">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.08em] text-[#86868b]">
                    Response
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold racking-tight-[-0.025em]">
                    Answer
                  </h2>
                </div>

                {result.retrieval?.status && (
                  <span
                    className={`rounded-full px-3 py-1.5 text-xs font-medium capitalize ${
                      result.retrieval.status === "high_confidence"
                        ? "bg-[#e8f8ed] text-[#248a3d]"
                        : result.retrieval.status === "medium_confidence"
                        ? "bg-[#fff4d6] text-[#9a6700]"
                        : "bg-[#f2f2f7] text-[#6e6e73]"
                    }`}
                  >
                    {result.retrieval.status.replaceAll("_", " ")}
                  </span>
                )}
              </div>

              <div className="mt-6 h-px bg-black/6" />

              <p className="mt-6 whitespace-pre-wrap text-[17px] leading-8 tracking-[-0.01em] text-[#3a3a3c]">
                {result.answer}
              </p>
            </div>

            {/* Metrics */}
            {result.retrieval && (
              <div className="grid overflow-hidden rounded-[26px] border border-black/4 bg-white sm:grid-cols-3">
                <div className="p-5 sm:p-6">
                  <p className="text-xs font-medium text-[#86868b]">
                    Retrieval Status
                  </p>
                  <p className="mt-2 text-lg font-semibold capitalize tracking-[-0.02em]">
                    {result.retrieval.status?.replaceAll("_", " ") || "-"}
                  </p>
                </div>

                <div className="border-t border-black/6 p-5 sm:border-l sm:border-t-0 sm:p-6">
                  <p className="text-xs font-medium text-[#86868b]">
                    Best Similarity
                  </p>
                  <p className="mt-2 text-lg font-semibold tracking-[-0.02em]">
                    {result.retrieval.best_similarity !== undefined &&
                    result.retrieval.best_similarity !== null
                      ? result.retrieval.best_similarity.toFixed(4)
                      : "-"}
                  </p>
                </div>

                <div className="border-t border-black/6 p-5 sm:border-l sm:border-t-0 sm:p-6">
                  <p className="text-xs font-medium text-[#86868b]">
                    Chunks Retrieved
                  </p>
                  <p className="mt-2 text-lg font-semibold tracking-[-0.02em]">
                    {result.retrieval.chunks_retrieved ?? 0}
                  </p>
                </div>
              </div>
            )}

            {/* Sources */}
            <div className="rounded-[30px] border border-black/4 bg-white p-6 sm:p-8">
              <div className="flex items-end justify-between gap-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.08em] text-[#86868b]">
                    References
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold racking-tight-[-0.025em]">
                    Sources
                  </h2>
                </div>

                <span className="text-sm text-[#86868b]">
                  {result.sources.length} source
                  {result.sources.length !== 1 ? "s" : ""}
                </span>
              </div>

              <div className="mt-6 h-px bg-black/6" />

              {result.sources.length === 0 ? (
                <p className="pt-6 text-sm text-[#86868b]">
                  No supporting sources were retrieved.
                </p>
              ) : (
                <div className="mt-5 divide-y divide-black/6">
                  {result.sources.map((source, index) => (
                    <div
                      key={`${source.source_id || "source"}-${index}`}
                      className="py-5 first:pt-0 last:pb-0"
                    >
                      <div className="flex items-start justify-between gap-5">
                        <div className="min-w-0">
                          <h3 className="font-medium text-[#1d1d1f]">
                            {source.title || "Untitled document"}
                          </h3>

                          <div className="mt-2 flex flex-wrap gap-2 text-xs text-[#86868b]">
                            {source.source_type && (
                              <span>{source.source_type}</span>
                            )}

                            {source.chunk_index !== undefined && (
                              <>
                                <span>·</span>
                                <span>Chunk {source.chunk_index}</span>
                              </>
                            )}
                          </div>
                        </div>

                        {source.similarity !== undefined && (
                          <span className="shrink-0 rounded-full bg-[#f5f5f7] px-3 py-1.5 text-xs font-medium text-[#6e6e73]">
                            {source.similarity.toFixed(4)}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}

        {/* Footer */}
        <footer className="mt-12 flex flex-col items-center gap-2 text-center text-xs text-[#86868b]">
          <span>AI Internal Knowledge Base</span>
          <span>FastAPI · Supabase pgvector · Gemini · Next.js</span>
        </footer>
      </div>
    </main>
  )

}