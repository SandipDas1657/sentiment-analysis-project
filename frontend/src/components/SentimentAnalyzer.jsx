import { useState } from 'react';

export default function SentimentAnalyzer() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async (textToAnalyze = text) => {
    if (!textToAnalyze.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToAnalyze }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Analysis request failed.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-16">
      {/* Editorial Hero Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-end border-b border-[#333333] pb-12">
        <div className="lg:col-span-8">
          <p className="text-xs font-mono uppercase tracking-widest text-neutral-400 mb-3">
            FOR APP TEAMS & PRODUCT MANAGERS
          </p>
          <h1 className="text-4xl sm:text-6xl font-black text-white tracking-tight uppercase leading-none font-sans">
            REVIEW INTELLIGENCE THAT MOVES PRODUCTS FORWARD
          </h1>
        </div>
        <div className="lg:col-span-4">
          <p className="text-neutral-400 text-sm leading-relaxed">
            Real-time rating prediction, implicit sarcasm detection, and numerical fallback parsing powered by FastAPI, Scikit-Learn, and RoBERTa models.
          </p>
        </div>
      </div>

      {/* Main Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Input Form */}
        <div className="lg:col-span-7 bg-[#262626] border border-[#333333] p-6 sm:p-8 flex flex-col justify-between min-h-100">
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-400">
                01 // RAW INPUT TEXT
              </h3>
              <span className="text-xs font-mono text-neutral-400">{text.length} CHARS</span>
            </div>

            <div className="relative mb-6">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste customer review here to evaluate sentiment..."
                rows={8}
                className="w-full bg-[#1c1c1c] border border-[#3a3a3a] p-4 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-white transition-colors font-sans resize-none"
              />
              {text && (
                <button
                  onClick={() => { setText(''); setResult(null); }}
                  className="absolute top-3 right-3 text-xs text-neutral-400 hover:text-white font-mono uppercase transition-colors"
                >
                  Clear
                </button>
              )}
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-950/40 border border-red-800 text-red-400 text-xs font-mono">
                ERR // {error}
              </div>
            )}
          </div>

          <button
            disabled={loading || !text.trim()}
            onClick={() => handleAnalyze()}
            className="w-full py-4 bg-white hover:bg-neutral-200 text-black font-black uppercase tracking-wider text-sm transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {loading ? 'RUNNING ENGINE...' : 'ANALYZE SENTIMENT →'}
          </button>
        </div>

        {/* Right Column: Prediction Output */}
        <div className="lg:col-span-5 bg-[#262626] border border-[#333333] p-6 sm:p-8 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-400">
                02 // ANALYSIS OUTPUT
              </h3>
              {result && (
                <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono px-2 py-0.5 uppercase tracking-wider">
                  MATCHED
                </span>
              )}
            </div>

            {result ? (
              <div className="space-y-8">
                {/* Rating Card */}
                <div className="bg-[#1c1c1c] border border-[#3a3a3a] p-6 text-center space-y-3">
                  <div className="flex justify-center gap-2 text-2xl">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <span
                        key={star}
                        className={star <= result.stars ? 'text-white' : 'text-neutral-600'}
                      >
                        ★
                      </span>
                    ))}
                  </div>
                  <div>
                    <span className="text-4xl font-black text-white">{result.stars}</span>
                    <span className="text-sm font-mono text-neutral-400"> / 5 STARS</span>
                  </div>
                </div>

                {/* Metrics List */}
                <div className="space-y-6">
                  <div className="flex justify-between items-center border-b border-[#333333] pb-3">
                    <span className="text-xs font-mono text-neutral-400 uppercase">CLASSIFICATION</span>
                    <span
                      className={`text-xs font-bold uppercase tracking-wider px-3 py-1 border ${
                        result.sentiment === 'Positive'
                          ? 'bg-emerald-950/40 text-emerald-400 border-emerald-800'
                          : result.sentiment === 'Neutral'
                          ? 'bg-amber-950/40 text-amber-400 border-amber-800'
                          : 'bg-red-950/40 text-red-400 border-red-800'
                      }`}
                    >
                      {result.sentiment}
                    </span>
                  </div>

                  <div className="space-y-2 border-b border-[#333333] pb-4">
                    <div className="flex justify-between text-xs font-mono text-neutral-400">
                      <span>CONFIDENCE METRIC</span>
                      <span className="text-white font-bold">{(result.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-[#1c1c1c] h-1.5 border border-[#333333]">
                      <div
                        className="bg-white h-full transition-all duration-500"
                        style={{ width: `${(result.confidence * 100).toFixed(1)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-center border border-dashed border-[#3a3a3a] p-6 text-neutral-500">
                <span className="font-mono text-xs uppercase mb-2">// STANDBY MODE</span>
                <p className="text-xs text-neutral-400 max-w-xs">
                  Submit input text to generate live rating predictions and confidence telemetry.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Capabilities Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6 border-t border-[#333333]">
        <div className="border border-[#333333] bg-[#262626] p-6 space-y-2">
          <span className="font-mono text-xs text-neutral-400">[01] ENGINE</span>
          <h4 className="font-extrabold text-white text-sm uppercase tracking-wider">HYBRID ML PIPELINE</h4>
          <p className="text-neutral-400 text-xs leading-relaxed">
            Combines sublinear TF-IDF (1-3 n-grams) with VADER polarity feature unions for precise scoring.
          </p>
        </div>

        <div className="border border-[#333333] bg-[#262626] p-6 space-y-2">
          <span className="font-mono text-xs text-neutral-400">[02] GUARDRAIL</span>
          <h4 className="font-extrabold text-white text-sm uppercase tracking-wider">ROBERTA IRONY CHECK</h4>
          <p className="text-neutral-400 text-xs leading-relaxed">
            Intercepts sarcastic reviews and maps implicit irony cleanly to 1-star sentiment predictions.
          </p>
        </div>

        <div className="border border-[#333333] bg-[#262626] p-6 space-y-2">
          <span className="font-mono text-xs text-neutral-400">[03] PARSER</span>
          <h4 className="font-extrabold text-white text-sm uppercase tracking-wider">NUMERIC RATING ENGINE</h4>
          <p className="text-neutral-400 text-xs leading-relaxed">
            Distinguishes explicit user ratings ("giving 2 stars") from hypothetical statements.
          </p>
        </div>
      </div>
    </div>
  );
}