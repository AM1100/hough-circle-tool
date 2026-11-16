# 交接状态与实际验收

日期：2026-11-16。分支：feat/5-video-handoff。图片基线：dc37779。交出准备完成；视频实施任务尚未开始，tasks.md 中第2、3组保持未勾选。

## 当前已完成
- 当前可运行代码：图片GUI、图片CLI、参数预设、PNG标注和坐标结果。
- 当前入口：app.py main/Handler；detect(data, parameters) 在 detector.py 完成图片解码、灰度、中值滤波、霍夫检测与标注；web/index.html 仅有图片文件导入。
- 原 hough-circle-tool 变更及其历史验收记录完整保留。

## 本次重新复现的基线
环境：Python 3.12.15、NumPy 2.5.4、opencv-python-headless 4.14.0.94；与 requirements-lock.txt 一致。

```bash
python -m unittest discover -s tests -v
python app.py --input examples/coins.jpg --output /tmp/hough-handoff-coins.png --preset coins
python app.py --input examples/cookie-plate.jpg --output /tmp/hough-handoff-plate.png --preset cookie-plate
```

实际结果：5项测试全部通过；硬币2圆，(193.5,192.5,178.7)、(567.5,191.5,179.0)，输出760×385；盘沿1圆，(262.5,258.5,244.9)，输出520×520。参数与README表格一致。测试包含HTTP接口，但本次未重验浏览器完整点击/下载流程，不把CLI成功替代浏览器端到端验证。

## 尚未实现或验证
- 没有视频入口、视频读写模块、视频UI或视频测试；现有 --input 仍仅用于图片，不能用于MP4。
- 视频代表样例与参数尚未选定，不能声称两组图片参数对视频通用。
- 视频编解码器、时间戳/FPS、帧数完整性、零圆/多圆输出、性能/内存、并发和失败清理均待实测。
- 首版规划为本机离线短视频；实时流、音频和跨场景精度不在当前计划范围。

## 接手入口
1. 克隆本分支，按README的锁定依赖命令和图片验收命令先复现基线；不通过则先排查环境。
2. 阅读本变更的 proposal.md、specs/video-circle-detection/spec.md、design.md、tasks.md；确认本次交接范围。
3. 从 tasks.md 的2.1开始，先选真实短视频并保存元数据和代表帧，再改检测核心；不要从重写图片界面开始。
4. 若使用OpenSpec CLI，运行 `openspec status --change add-video-detection --json` 与 `openspec instructions apply --change add-video-detection --json`；如使用Codex，接手后可明确请求 `$openspec-apply-change add-video-detection`。本次没有执行这些实施任务。
