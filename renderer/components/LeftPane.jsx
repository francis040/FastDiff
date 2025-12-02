import HighlightChunk from './HighlightChunk.jsx';

const lineBackground = {
  added: 'bg-[#D6F5D6]',
  removed: 'bg-[#FAD6D6]',
  modified: 'bg-[#FFF3C4]',
  context: 'bg-white',
};

function LeftPane({ chunks, text, onTextChange, scrollRef, onScroll, diffRefs, meta }) {
  return (
    <div className="h-full flex flex-col">
      <div className="px-6 py-4 border-b border-gray-200 bg-white">
        <div className="text-xs text-gray-500 mb-2">
          {meta?.path ? `左侧：${meta.path}` : '左侧：粘贴或打开文本'}
        </div>
        <textarea
          value={text}
          onChange={(e) => onTextChange(e.target.value)}
          placeholder="在此粘贴内容..."
          className="w-full h-28 rounded-lg border border-gray-200 bg-[#fafafa] px-3 py-2 text-sm text-slate-800 outline-none focus:border-gray-400 transition"
        />
      </div>
      <div
        ref={scrollRef}
        onScroll={onScroll}
        className="flex-1 overflow-auto diff-pane px-6 py-4 space-y-2"
      >
        {chunks.map((chunk, index) => (
          <div
            key={`${chunk.type}-${index}-left`}
            ref={(node) => {
              diffRefs.current[index] = node;
            }}
            className={`rounded-md border border-gray-100 px-4 py-3 shadow-[0_1px_2px_rgba(15,23,42,0.04)] ${
              chunk.type !== 'context' ? 'ring-1 ring-gray-100' : ''
            } ${lineBackground[chunk.type]}`}
          >
            <div className="flex gap-3 text-sm leading-relaxed">
              <div className="w-12 text-right text-gray-400 select-none pr-1">
                {chunk.leftLineNumber ?? ''}
              </div>
              <div className="flex-1 text-slate-800">
                {chunk.leftSegments?.length ? (
                  <HighlightChunk segments={chunk.leftSegments} />
                ) : (
                  <span className="text-gray-400">{chunk.leftText ? chunk.leftText : ' '}</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default LeftPane;
