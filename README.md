# Claude — Motion Reel 2026

15秒のモーショングラフィックス・ショーリール。映像も音も、すべてコードで1フレームずつ書いたもの。

- 公開ページ: https://sanny114.github.io/motion-reel/
- `reel.mp4` — 本編（1920×1080 / 60fps / 音声つき）
- `live.html` — Canvas版。ブラウザでリアルタイムに描画（クリックで音つき再生）
- `src/render.mjs` — Playwrightで `live.html` から120fpsの連番PNGを書き出す
- `src/synth.py` — サウンドトラック `reel.wav` をnumpyで合成

書き出し: `ffmpeg -framerate 120 -i frames/f%05d.png -i reel.wav -vf "tmix=frames=2,fps=60,format=yuv420p" -c:v libx264 -crf 22 -c:a aac reel.mp4`

フォント（`fonts/`）: Anton / Space Grotesk / JetBrains Mono / Noto Sans JP（SIL Open Font License）。制作: Claude Code。
