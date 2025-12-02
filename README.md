# FastDiff — Minimal A Style Diff Tool

Electron + React + Tailwind CSS 桌面应用，用于以极简柔和的方式查看文本差异。左右同步滚动、行内高亮，支持文件打开与手动粘贴。

## 开发

```bash
npm install
npm start
```

- `npm start`：同时启动 Vite 开发服务器与 Electron。
- 渲染进程端口默认 5173，可在 `vite.config.js` 调整。

## 打包

```bash
npm run build
```

使用 `electron-builder` 输出，Windows 默认目标为 NSIS，可在 `package.json` 的 `build` 字段调整。

## 主要技术
- Electron（主进程 & 预加载）
- React 18 + Vite
- Tailwind CSS
- diff / diff-match-patch（差异计算）
- chardet + iconv-lite（编码侦测与解码）

## 目录
```
FastDiff/
├── main/                # Electron 主进程 & preload
├── renderer/            # React + Tailwind 界面
│   ├── components/      # TopBar / DiffContainer / Panes 等
│   ├── utils/           # diff 封装
│   ├── index.html
│   └── main.jsx
├── tailwind.config.js
├── vite.config.js
└── package.json
```
