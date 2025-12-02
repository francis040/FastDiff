# FastDiff

FastDiff 是一款基于 Python + PySide6 的本地桌面文本差异对比工具，采用 Minimal A（苹果风）界面风格。支持自动编码检测、行级和字符级差异高亮、同步滚动以及一键跳转下一处差异。

## 主要功能
- 左右独立加载文件或直接粘贴文本内容，自动检测常见编码（UTF-8/GBK 等）。
- 基于 `difflib` 的行级与字符级差异分析，淡色高亮新增、删除与修改行。
- 左右视图同步滚动，带行号显示，快速跳转到下一处差异。
- 底部状态栏展示当前差异总数。

## 运行
```bash
pip install -r requirements.txt
python main.py
```

## 打包
使用 PyInstaller 生成无控制台窗口的可执行程序：
```bash
pyinstaller --noconsole --windowed --name FastDiff main.py
```

## 项目结构
```
FastDiff/
├── main.py
├── ui/
│   ├── main_window.py
│   ├── diff_view.py
│   └── styles.qss
├── utils/
│   ├── diff_engine.py
│   └── file_loader.py
├── assets/
│   └── icons/
└── requirements.txt
```
