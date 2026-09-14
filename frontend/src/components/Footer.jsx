export default function Footer() {
  return (
    <footer className="w-full bg-[#1c1c1c] border-t border-[#333333] py-6 px-6 sm:px-12 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4 text-xs font-mono text-neutral-400">
        <p>© 2026 FEEDBACKPULSE // BUILT BY SANDIP DAS</p>
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-[#262626] border border-[#333333] text-[10px] text-neutral-300">
            PYTHON 3.11
          </span>
          <span className="px-2 py-1 bg-[#262626] border border-[#333333] text-[10px] text-neutral-300">
            FASTAPI
          </span>
          <span className="px-2 py-1 bg-[#262626] border border-[#333333] text-[10px] text-neutral-300">
            ROBERTA
          </span>
          <span className="px-2 py-1 bg-[#262626] border border-[#333333] text-[10px] text-neutral-300">
            TAILWIND
          </span>
        </div>
      </div>
    </footer>
  );
}