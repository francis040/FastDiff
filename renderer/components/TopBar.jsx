import { Search, SkipForward, RefreshCcw, Upload } from 'lucide-react';

function TopBar({ onOpenLeft, onOpenRight, onRefresh, onNextDiff, searchQuery, onSearchChange }) {
  return (
    <div className="h-12 border-b border-gray-200 bg-white flex items-center px-4 gap-2 sticky top-0 z-10">
      <div className="flex items-center gap-2 text-sm text-slate-700">
        <button
          onClick={onOpenLeft}
          className="inline-flex items-center gap-1 px-3 py-2 rounded-md bg-gray-100 hover:bg-gray-200 transition"
        >
          <Upload size={16} />
          左文件
        </button>
        <button
          onClick={onOpenRight}
          className="inline-flex items-center gap-1 px-3 py-2 rounded-md bg-gray-100 hover:bg-gray-200 transition"
        >
          <Upload size={16} />
          右文件
        </button>
        <div className="h-6 w-px bg-gray-300 mx-2" />
        <button
          onClick={onRefresh}
          className="inline-flex items-center gap-1 px-3 py-2 rounded-md bg-gray-100 hover:bg-gray-200 transition"
        >
          <RefreshCcw size={16} />
          刷新
        </button>
        <button
          onClick={onNextDiff}
          className="inline-flex items-center gap-1 px-3 py-2 rounded-md bg-gray-100 hover:bg-gray-200 transition"
        >
          <SkipForward size={16} />
          下一处
        </button>
      </div>
      <div className="flex-1 flex justify-end">
        <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-md text-sm text-slate-600 min-w-[220px]">
          <Search size={16} className="text-gray-500" />
          <input
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="搜索关键字 (可选)"
            className="bg-transparent outline-none text-slate-700 placeholder:text-gray-400 flex-1"
          />
        </div>
      </div>
    </div>
  );
}

export default TopBar;
