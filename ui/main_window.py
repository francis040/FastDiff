from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ui.diff_view import DiffView
from utils.diff_engine import generate_diff
from utils.file_loader import load_file


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("FastDiff")
        self.resize(1200, 760)

        self.left_text = ""
        self.right_text = ""
        self.diff_rows: List[dict] = []
        self.current_diff_index = -1

        self.diff_view = DiffView()
        self.diff_view.contentChanged.connect(self.update_diff_from_edit)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        toolbar = self._build_toolbar()
        layout.addWidget(toolbar)
        layout.addWidget(self.diff_view)

        self._load_styles()
        self._update_status(0)

    def _build_toolbar(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.open_left_button = QPushButton("打开左文件")
        self.open_right_button = QPushButton("打开右文件")
        self.next_diff_button = QPushButton("下一处差异")

        self.open_left_button.clicked.connect(self.open_left_file)
        self.open_right_button.clicked.connect(self.open_right_file)
        self.next_diff_button.clicked.connect(self.goto_next_diff)

        for btn in (self.open_left_button, self.open_right_button, self.next_diff_button):
            layout.addWidget(btn)

        layout.addStretch()
        return container

    def _load_styles(self) -> None:
        style_path = Path(__file__).resolve().parent / "styles.qss"
        if style_path.exists():
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def open_left_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "选择左侧文件")
        if file_path:
            content, encoding = load_file(file_path)
            self.left_text = content
            self.status_bar.showMessage(f"左侧文件编码：{encoding}")
            self.update_diff()

    def open_right_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "选择右侧文件")
        if file_path:
            content, encoding = load_file(file_path)
            self.right_text = content
            self.status_bar.showMessage(f"右侧文件编码：{encoding}")
            self.update_diff()

    def update_diff_from_edit(self) -> None:
        self.left_text, self.right_text = self.diff_view.get_texts()
        self.update_diff()

    def update_diff(self) -> None:
        self.diff_rows, diff_count = generate_diff(self.left_text, self.right_text)
        self.current_diff_index = -1
        self.diff_view.update_diff(self.diff_rows, self.left_text, self.right_text)
        self._update_status(diff_count)

    def goto_next_diff(self) -> None:
        if not self.diff_rows:
            return
        self.current_diff_index += 1
        self.diff_view.scroll_to_diff(self.current_diff_index)

    def _update_status(self, diff_count: int) -> None:
        self.status_bar.showMessage(f"共 {diff_count} 处差异")
