'use client';

interface HeaderProps {
    sessionId: string;
    onResetSession: () => void;
}


export const Header = ({ sessionId, onResetSession }: HeaderProps) => {
    return (
        <header className="w-full bg-zinc-900 border-b border-zinc-800 px-6 py-4 flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white text-base">
                    ∫
                </div>
                <div>
                    <h1 className="text-base font-semibold text-zinc-100 leading-tight">
                        Math Proof Coach
                    </h1>
                    <p className="text-xs text-zinc-400">
                        Socratic AI Assistant For Qualifying Exam Prep
                    </p>
                </div>
            </div>

            <div className="flex items-center space-x-4">
                <div className="hidden sm:flex items-center space-x-2 bg-zinc-800 border border-zinc-700/60 px-3 py-1 rounded-full text-sm text-zinc-400">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                    <span> Session: </span>
                    <span className="font-mono text-zinc-300">
                        {sessionId ? `${sessionId.slice(0, 8)}...` : 'Initializing'}
                    </span>
                </div>
                <button
                    onClick={onResetSession}
                    type="button"
                    className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 text-xs font-medium px-3 py-1.5 rounded-lg transition-colors cursor-pointer flex items-center space-x-1.5">
                    <svg
                        className="w-3.5 h-3.5 text-zinc-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                        />
                    </svg>
                    <span>New Session</span>
                </button>

            </div>
        </header>
    )
}