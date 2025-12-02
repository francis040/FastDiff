import { useEffect, useMemo, useRef, useState } from 'react';
import DiffContainer from './components/DiffContainer.jsx';
import StatusBar from './components/StatusBar.jsx';
import TopBar from './components/TopBar.jsx';
import { buildDiff } from './utils/diff.js';

const initialSampleLeft = 'The quick brown fox\nJumps over the lazy dog\nLines can be edited or replaced';
const initialSampleRight = 'The quick brown fox\nleaps over the lazy cat\nLines can be edited or replaced\nwith new content';

function App() {
  const [leftText, setLeftText] = useState(initialSampleLeft);
  const [rightText, setRightText] = useState(initialSampleRight);
  const [leftMeta, setLeftMeta] = useState(null);
  const [rightMeta, setRightMeta] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const diffRef = useRef(null);

  const { chunks, diffCount } = useMemo(
    () => buildDiff(leftText, rightText, searchQuery),
    [leftText, rightText, searchQuery]
  );

  useEffect(() => {
    setTimeout(() => {
      if (diffRef.current) {
        diffRef.current.scrollToDiff(0);
      }
    }, 120);
  }, []);

  const handleOpenFile = async (side) => {
    if (!window.api?.openFile) return;
    const result = await window.api.openFile();
    if (result?.canceled) return;
    if (side === 'left') {
      setLeftText(result.content);
      setLeftMeta({ path: result.path, encoding: result.encoding });
    } else {
      setRightText(result.content);
      setRightMeta({ path: result.path, encoding: result.encoding });
    }
  };

  const handleRefresh = () => {
    const updated = buildDiff(leftText, rightText, searchQuery);
    if (diffRef.current) {
      diffRef.current.resetScroll();
    }
    return updated;
  };

  const handleNextDiff = () => {
    if (diffRef.current) {
      diffRef.current.nextDiff();
    }
  };

  return (
    <div className="h-screen flex flex-col bg-white text-slate-900">
      <TopBar
        onOpenLeft={() => handleOpenFile('left')}
        onOpenRight={() => handleOpenFile('right')}
        onRefresh={handleRefresh}
        onNextDiff={handleNextDiff}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />
      <DiffContainer
        ref={diffRef}
        chunks={chunks}
        leftText={leftText}
        rightText={rightText}
        onLeftChange={setLeftText}
        onRightChange={setRightText}
        leftMeta={leftMeta}
        rightMeta={rightMeta}
      />
      <StatusBar diffCount={diffCount} />
    </div>
  );
}

export default App;
