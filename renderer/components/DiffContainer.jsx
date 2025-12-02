import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef, useState } from 'react';
import LeftPane from './LeftPane.jsx';
import RightPane from './RightPane.jsx';

const DiffContainer = forwardRef(function DiffContainer(
  { chunks, leftText, rightText, onLeftChange, onRightChange, leftMeta, rightMeta },
  ref
) {
  const leftScrollRef = useRef(null);
  const rightScrollRef = useRef(null);
  const diffRefs = useRef([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const syncLock = useRef(false);

  useEffect(() => {
    diffRefs.current = [];
  }, [chunks]);

  const diffIndices = useMemo(
    () => chunks.map((chunk, index) => (chunk.type === 'context' ? null : index)).filter((i) => i !== null),
    [chunks]
  );

  const scrollToDiff = (index) => {
    if (!diffIndices.length) return;
    const safeIndex = ((index % diffIndices.length) + diffIndices.length) % diffIndices.length;
    const chunkIndex = diffIndices[safeIndex];
    const node = diffRefs.current[chunkIndex];
    if (node && leftScrollRef.current && rightScrollRef.current) {
      const offset = node.offsetTop - 12;
      leftScrollRef.current.scrollTo({ top: offset, behavior: 'smooth' });
      rightScrollRef.current.scrollTo({ top: offset, behavior: 'smooth' });
      setActiveIndex(safeIndex);
    }
  };

  const handleScroll = (source, event) => {
    if (syncLock.current) return;
    syncLock.current = true;
    const otherRef = source === 'left' ? rightScrollRef.current : leftScrollRef.current;
    if (otherRef) {
      otherRef.scrollTop = event.target.scrollTop;
    }
    syncLock.current = false;
  };

  useImperativeHandle(ref, () => ({
    scrollToDiff,
    nextDiff: () => scrollToDiff(activeIndex + 1),
    resetScroll: () => {
      if (leftScrollRef.current && rightScrollRef.current) {
        leftScrollRef.current.scrollTo({ top: 0 });
        rightScrollRef.current.scrollTo({ top: 0 });
      }
      setActiveIndex(0);
    },
  }));

  return (
    <div className="flex-1 grid grid-cols-2 divide-x divide-gray-200 bg-white fade-in">
      <div className="flex flex-col">
        <LeftPane
          chunks={chunks}
          text={leftText}
          onTextChange={onLeftChange}
          scrollRef={leftScrollRef}
          onScroll={(event) => handleScroll('left', event)}
          diffRefs={diffRefs}
          meta={leftMeta}
        />
      </div>
      <div className="flex flex-col">
        <RightPane
          chunks={chunks}
          text={rightText}
          onTextChange={onRightChange}
          scrollRef={rightScrollRef}
          onScroll={(event) => handleScroll('right', event)}
          diffRefs={diffRefs}
          meta={rightMeta}
        />
      </div>
    </div>
  );
});

export default DiffContainer;
