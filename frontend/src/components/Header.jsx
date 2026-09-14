export default function Header({ apiStatus }) {
  return (
    <header className="w-full bg-[#1c1c1c] border-b border-[#333333] py-4 px-6 sm:px-12">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span className="text-xl font-black tracking-tighter text-white uppercase font-sans">
            FEEDBACKPULSE
          </span>
          <span className="bg-indigo-600 text-white text-[10px] font-bold px-2 py-0.5 rounded tracking-wider uppercase">
            NLP Engine
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-[#262626] border border-[#333333] px-3 py-1.5 rounded-full text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                apiStatus === 'online'
                  ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]'
                  : apiStatus === 'offline'
                  ? 'bg-red-500'
                  : 'bg-amber-500 animate-pulse'
              }`}
            />
            <span className="text-neutral-300 font-mono uppercase text-[11px] tracking-wider">
              {apiStatus === 'online'
                ? 'API v4.1 Connected'
                : apiStatus === 'offline'
                ? 'API Offline'
                : 'Connecting...'}
            </span>
          </div>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-1 bg-white hover:bg-neutral-200 text-black font-semibold text-xs px-4 py-2 rounded-full transition-colors uppercase tracking-wider"
          >
            API Docs <span className="text-sm">→</span>
          </a>
        </div>
      </div>
    </header>
  );
}