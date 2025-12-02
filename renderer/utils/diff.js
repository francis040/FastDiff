import { diffLines, diffWords } from 'diff';

const sanitizeLines = (text = '') => {
  const lines = text.split('\n');
  if (lines.length && lines[lines.length - 1] === '') {
    lines.pop();
  }
  return lines;
};

const inlineSegments = (leftLine = '', rightLine = '') => {
  const wordDiff = diffWords(leftLine, rightLine, { newlineIsToken: true });
  const leftSegments = [];
  const rightSegments = [];

  wordDiff.forEach((part) => {
    if (part.added) {
      rightSegments.push({ text: part.value, type: 'added' });
    } else if (part.removed) {
      leftSegments.push({ text: part.value, type: 'removed' });
    } else {
      leftSegments.push({ text: part.value, type: 'context' });
      rightSegments.push({ text: part.value, type: 'context' });
    }
  });

  return { leftSegments, rightSegments };
};

export const buildDiff = (leftText, rightText, searchQuery = '') => {
  const lineDiff = diffLines(leftText, rightText);
  let leftLineNumber = 1;
  let rightLineNumber = 1;
  const chunks = [];
  let diffCount = 0;

  for (let i = 0; i < lineDiff.length; i += 1) {
    const part = lineDiff[i];

    if (part.removed && lineDiff[i + 1]?.added) {
      const removed = sanitizeLines(part.value);
      const added = sanitizeLines(lineDiff[i + 1].value);
      const maxLines = Math.max(removed.length, added.length);

      for (let j = 0; j < maxLines; j += 1) {
        const leftLine = removed[j] ?? '';
        const rightLine = added[j] ?? '';
        const { leftSegments, rightSegments } = inlineSegments(leftLine, rightLine);
        chunks.push({
          type: 'modified',
          leftText: leftLine,
          rightText: rightLine,
          leftSegments,
          rightSegments,
          leftLineNumber: leftLine ? leftLineNumber : '',
          rightLineNumber: rightLine ? rightLineNumber : '',
        });
        if (leftLine) leftLineNumber += 1;
        if (rightLine) rightLineNumber += 1;
        diffCount += 1;
      }
      i += 1;
      continue;
    }

    if (part.added) {
      const lines = sanitizeLines(part.value);
      lines.forEach((line) => {
        chunks.push({
          type: 'added',
          rightText: line,
          rightSegments: [{ text: line, type: 'added' }],
          rightLineNumber,
          leftText: '',
          leftSegments: [],
          leftLineNumber: '',
        });
        rightLineNumber += 1;
        diffCount += 1;
      });
      continue;
    }

    if (part.removed) {
      const lines = sanitizeLines(part.value);
      lines.forEach((line) => {
        chunks.push({
          type: 'removed',
          leftText: line,
          leftSegments: [{ text: line, type: 'removed' }],
          leftLineNumber,
          rightText: '',
          rightSegments: [],
          rightLineNumber: '',
        });
        leftLineNumber += 1;
        diffCount += 1;
      });
      continue;
    }

    const lines = sanitizeLines(part.value);
    lines.forEach((line) => {
      const matchesSearch = searchQuery && line.toLowerCase().includes(searchQuery.toLowerCase());
      const searchSegments = matchesSearch
        ? [
            { text: line, type: 'modified' },
          ]
        : [{ text: line, type: 'context' }];
      chunks.push({
        type: matchesSearch ? 'modified' : 'context',
        leftText: line,
        rightText: line,
        leftSegments: searchSegments,
        rightSegments: searchSegments,
        leftLineNumber,
        rightLineNumber,
      });
      leftLineNumber += 1;
      rightLineNumber += 1;
    });
  }

  return { chunks, diffCount };
};
