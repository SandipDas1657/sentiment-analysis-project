import { useState } from 'react';

export default function App() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const analyzeSentiment = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch prediction');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('Could not connect to FastAPI backend. Ensure Uvicorn is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (starCount) => {
    return Array.from({ length: 5 }, (_, index) => (
      <svg
        key={index}
        className={`w-8 h-8 transition-all duration-300 ${
          index < starCount
            ? 'text-amber-400 fill-amber-400 drop-shadow-[0_2px_4px_rgba(251,191,36,0.3)]'
            : 'text-slate-200 fill-slate-100 border-none'
        }`}
        viewBox="0 0 24 24"
      >
        <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
      </svg>
    ));
  };

  const getBadgeStyle = (sentiment) => {
    switch (sentiment) {
      case 'Positive':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200/80';
      case 'Negative':
        return 'bg-rose-50 text-rose-700 border-rose-200/80';
      default:
        return 'bg-amber-50 text-amber-700 border-amber-200/80';
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-xl bg-white rounded-3xl border border-slate-200/80 shadow-[0_25px_60px_-15px_rgba(15,23,42,0.08)] p-8 sm:p-10 transition-all">
        
        <div className="space-y-2 mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-600 text-xs font-semibold tracking-wider uppercase">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
            NLP Sentiment Engine
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight font-['Outfit']">
            Customer Feedback Intelligence
          </h1>
          <p className="text-slate-500 text-sm leading-relaxed">
            Real-time rating prediction and sentiment analysis powered by FastAPI & Scikit-Learn.
          </p>
        </div>

        <div className="space-y-5">
          <div className="relative">
            <textarea
              className="w-full h-40 p-5 bg-slate-50/50 border border-slate-200 rounded-2xl focus:bg-white focus:ring-2 focus:ring-slate-900 focus:border-transparent outline-none resize-none text-slate-800 placeholder-slate-400 text-sm sm:text-base font-normal leading-relaxed transition-all duration-200"
              placeholder="Paste or type customer review text here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>

          <button
            onClick={analyzeSentiment}
            disabled={loading || !text.trim()}
            className="w-full py-4 bg-slate-900 hover:bg-black text-white font-semibold rounded-2xl shadow-lg shadow-slate-900/10 hover:shadow-slate-900/20 active:scale-[0.99] transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2 text-sm tracking-wide font-['Outfit']"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Processing Text...
              </span>
            ) : (
              'Analyze Sentiment'
            )}
          </button>
        </div>

        {error && (
          <div className="mt-6 p-4 bg-rose-50 text-rose-700 text-xs font-medium rounded-2xl border border-rose-200/80 leading-relaxed">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-8 p-6 rounded-2xl border border-slate-200/90 bg-slate-50/70 space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="flex flex-col items-center justify-center space-y-2 py-2">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest font-['Outfit']">
                Predicted Rating
              </span>
              <div className="flex items-center gap-1.5">{renderStars(result.stars)}</div>
              <span className="text-xl font-bold text-slate-900 font-['Outfit'] tracking-tight pt-1">
                {result.stars} out of 5 Stars
              </span>
            </div>

            <div className="pt-4 border-t border-slate-200/80 space-y-3.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Sentiment Classification
                </span>
                <span className={`px-3.5 py-1 text-xs font-bold rounded-full border ${getBadgeStyle(result.sentiment)}`}>
                  {result.sentiment}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Confidence Score
                </span>
                <span className="text-sm font-bold text-slate-900 font-['Outfit']">
                  {(result.confidence * 100).toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}