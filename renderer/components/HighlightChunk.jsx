const backgroundByType = {
  added: 'bg-[#D6F5D6]',
  removed: 'bg-[#FAD6D6]',
  modified: 'bg-[#FFF3C4]',
  context: '',
};

function HighlightChunk({ segments }) {
  return (
    <span className="whitespace-pre-wrap">
      {segments.map((segment, index) => (
        <span
          key={`${segment.text}-${index}`}
          className={`${backgroundByType[segment.type] || ''} rounded-sm`}
        >
          {segment.text}
        </span>
      ))}
    </span>
  );
}

export default HighlightChunk;
