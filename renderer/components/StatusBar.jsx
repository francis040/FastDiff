function StatusBar({ diffCount }) {
  return (
    <div className="h-10 border-t border-gray-200 bg-white flex items-center justify-between px-4 text-xs text-gray-500">
      <span>共找到 {diffCount} 处差异</span>
      <span className="tracking-wide">Minimal · A · Style</span>
    </div>
  );
}

export default StatusBar;
