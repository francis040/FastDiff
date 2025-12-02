from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QTextCursor, QTextFormat
from PySide6.QtWidgets import QHBoxLayout, QPlainTextEdit, QSizePolicy, QSplitter, QWidget


class LineNumberArea(QWidget):
    def __init__(self, editor: "DiffEditor") -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        self.editor.line_number_area_paint_event(event)


class DiffEditor(QPlainTextEdit):
    userEdited = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._updating = False
        self._line_metadata: Dict[int, Dict[str, object]] = {}
        self._line_number_area = LineNumberArea(self)

        font = QFont("SF Mono")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(12)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(" "))

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.textChanged.connect(self._on_text_changed)

        self.update_line_number_area_width(0)

    def line_number_area_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        margin = 12
        return self.fontMetrics().horizontalAdvance("9") * digits + margin

    def update_line_number_area_width(self, _: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy) -> None:  # type: ignore[override]
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(0, cr.top(), self.line_number_area_width(), cr.height())

    def line_number_area_paint_event(self, event) -> None:
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor("#F8F8F8"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        number_color = QColor("#A7A7A7")
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(number_color)
                painter.drawText(0, top, self._line_number_area.width() - 4, self.fontMetrics().height(), Qt.AlignRight, number)
            block = block.next()
            block_number += 1
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())

    def _on_text_changed(self) -> None:
        if self._updating:
            return
        self.userEdited.emit()

    def set_content(self, text: str) -> None:
        self._updating = True
        try:
            self.setPlainText(text)
        finally:
            self._updating = False

    def set_line_metadata(self, metadata: Dict[int, Dict[str, object]]) -> None:
        self._line_metadata = metadata
        self.apply_highlighting()

    def apply_highlighting(self) -> None:
        selections = []
        doc = self.document()
        block = doc.begin()
        while block.isValid():
            block_index = block.blockNumber()
            meta = self._line_metadata.get(block_index, {"status": "context", "char_changes": []})
            status = meta.get("status", "context")
            char_changes: List[tuple[int, int]] = meta.get("char_changes", [])  # type: ignore[assignment]

            background = ColorPalette.background_for(status)
            selections.append(QTextEditExtraSelectionFactory.block(block, background))

            for start, end in char_changes:
                selections.append(
                    QTextEditExtraSelectionFactory.range(
                        block, start, end, ColorPalette.CHAR_HIGHLIGHT
                    )
                )
            block = block.next()

        self.setExtraSelections(selections)

    def scroll_to_line(self, line_index: int) -> None:
        if self.blockCount() == 0:
            return
        clamped_index = min(max(0, line_index), self.blockCount() - 1)
        cursor = QTextCursor(self.document().findBlockByNumber(clamped_index))
        self.setTextCursor(cursor)
        self.centerCursor()


class ColorPalette:
    ADDED = QColor("#E8FCE8")
    DELETED = QColor("#FBE8E8")
    MODIFIED = QColor("#FFF7D6")
    CONTEXT = QColor("#FFFFFF")
    CHAR_HIGHLIGHT = QColor("#FFE8A3")

    @staticmethod
    def background_for(status: object) -> QColor:
        if status == "added":
            return ColorPalette.ADDED
        if status == "deleted":
            return ColorPalette.DELETED
        if status == "modified":
            return ColorPalette.MODIFIED
        return ColorPalette.CONTEXT


class QTextEditExtraSelectionFactory:
    @staticmethod
    def block(block, background: QColor):
        from PySide6.QtWidgets import QTextEdit

        selection = QTextEdit.ExtraSelection()
        selection.cursor = QTextCursor(block)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.format.setBackground(background)
        return selection

    @staticmethod
    def range(block, start: int, end: int, background: QColor):
        from PySide6.QtWidgets import QTextEdit

        selection = QTextEdit.ExtraSelection()
        cursor = QTextCursor(block)
        cursor.setPosition(block.position() + start)
        cursor.setPosition(block.position() + end, QTextCursor.KeepAnchor)
        selection.cursor = cursor
        selection.format.setBackground(background)
        return selection


class DiffView(QWidget):
    contentChanged = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.left_editor = DiffEditor()
        self.right_editor = DiffEditor()
        self._syncing_scroll = False
        self._diff_positions: List[Tuple[Optional[int], Optional[int]]] = []

        splitter = QSplitter()
        splitter.addWidget(self.left_editor)
        splitter.addWidget(self.right_editor)
        splitter.setSizes([1, 1])

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        self.left_editor.verticalScrollBar().valueChanged.connect(self._sync_from_left)
        self.right_editor.verticalScrollBar().valueChanged.connect(self._sync_from_right)
        self.left_editor.userEdited.connect(self.contentChanged.emit)
        self.right_editor.userEdited.connect(self.contentChanged.emit)

    def _sync_from_left(self, value: int) -> None:
        if self._syncing_scroll:
            return
        self._syncing_scroll = True
        self.right_editor.verticalScrollBar().setValue(value)
        self._syncing_scroll = False

    def _sync_from_right(self, value: int) -> None:
        if self._syncing_scroll:
            return
        self._syncing_scroll = True
        self.left_editor.verticalScrollBar().setValue(value)
        self._syncing_scroll = False

    def set_texts(self, left_text: str, right_text: str) -> None:
        self.left_editor.set_content(left_text)
        self.right_editor.set_content(right_text)

    def update_diff(self, rows: List[Dict[str, object]], left_text: str, right_text: str) -> None:
        self.set_texts(left_text, right_text)
        self._diff_positions = [
            (row.get("left", {}).get("number"), row.get("right", {}).get("number"))
            for row in rows
            if row.get("tag") != "equal"
        ]

        left_meta = self._build_metadata(rows, "left")
        right_meta = self._build_metadata(rows, "right")

        self.left_editor.set_line_metadata(left_meta)
        self.right_editor.set_line_metadata(right_meta)

    def _build_metadata(self, rows: List[Dict[str, object]], side: str) -> Dict[int, Dict[str, object]]:
        metadata: Dict[int, Dict[str, object]] = {}
        for row in rows:
            line_info = row.get(side, {})
            number = line_info.get("number")
            if number is None:
                continue
            metadata[number - 1] = {
                "status": line_info.get("status", "context"),
                "char_changes": line_info.get("char_changes", []),
            }
        return metadata

    def scroll_to_diff(self, index: int) -> None:
        if not self._diff_positions:
            return
        target_left, target_right = self._diff_positions[index % len(self._diff_positions)]
        left_line = target_left - 1 if target_left is not None else 0
        right_line = target_right - 1 if target_right is not None else 0
        self.left_editor.scroll_to_line(max(0, left_line))
        self.right_editor.scroll_to_line(max(0, right_line))

    def get_texts(self) -> tuple[str, str]:
        return self.left_editor.toPlainText(), self.right_editor.toPlainText()
