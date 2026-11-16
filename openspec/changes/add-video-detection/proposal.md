# Proposal
## Why
技术选型与原型任务五要求把现有图片霍夫圆工具交给队友，在该基线之上继续添加导入视频的圆检测功能。交接时需要区分已验证图片能力与尚未实现的视频需求。
## What Changes
- 本分支仅完善 README 和交接记录，复跑图片基线，整理视频功能规格、设计和待办；不实现视频代码。
- 拟交给接手人的首版视频需求：本机离线导入 MP4，逐帧复用霍夫检测，保留无圆帧，输出标注视频与逐帧 JSONL，并通过现有浏览器界面导入和下载结果。
- 继续保留原有图片 GUI、CLI、预设和图像导出行为。
## Capabilities
### New Capabilities
- `video-circle-detection`: 本地视频导入、逐帧圆检测和可复核输出。
### Modified Capabilities
无。现有图片规格仍保留在 hough-circle-tool 变更中，不在本次交接重写。
## Impact
本次仅文档和 OpenSpec。后续实施预计涉及 detector.py 的帧接口、app.py 的视频入口、web/index.html 及新的视频读写模块。当前没有视频验收结果，不能将本规划当成已实现功能。
