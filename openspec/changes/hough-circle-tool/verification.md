# 实际验收记录
日期：2026-11-13。规格依据：飞书「开发管理」任务三；已将导入、调参、预览、导出和两张照片目标逐条写入 spec.md。实现选择本地浏览器界面，不依赖桌面 GUI 库。

## 实施
- 使用 OpenSpec CLI 初始化项目并创建 hough-circle-tool 变更。
- proposal/specs/design/tasks 先于代码建立，记录本机服务、原图像素单位、预设和导出失效策略。
- detector.py 实现真实 HoughCircles 检测；app.py 提供 CLI 和 HTTP；web/index.html 提供导入、参数编辑、预览、坐标表和导出。

## 自动与命令行验收
- `python app.py --input examples/coins.jpg --output results/coins-annotated.png --preset coins`：输出 count=2；圆心半径为 (193.5,192.5,178.7)、(567.5,191.5,179.0)。
- `python app.py --input examples/cookie-plate.jpg --output results/cookie-plate-annotated.png --preset cookie-plate`：输出 count=1；(262.5,258.5,244.9)。
- `python -m unittest discover -s tests -v`：5 个测试全部通过，包含原图同尺寸 PNG、几何位置、空白图零圆、非法参数、非法图片、HTTP 调用和跨站 Origin 拒绝。
- 两张结果见 results/；JSON 保留实际参数与圆坐标。

## 浏览器验收
- 打开本地界面，硬币样例 → 检测圆：显示 2 个圆，原图与标注图同时呈现，坐标表与 CLI 一致。
- 将 param2 从 35 改成 40：旧标注与导出链接失效，提示重新检测。
- 饼干盘样例 → 检测圆：显示 1 个圆，坐标为 262.5/258.5/244.9；标注沿盘子外缘。
- 界面截图：results/gui-plate.png。

规格与验收参数一并写入 README；样例与标注图保留原始来源署名。

## 独立安装检查
使用 uv 新建 Python 3.12.15 虚拟环境，仅按 requirements.txt 安装 numpy 2.5.4 / opencv-python-headless 4.14.0.94。重新执行全部 5 个测试，全部通过；硬币图的数量与坐标同记录一致。已提供 requirements-lock.txt 记录该环境版本。
