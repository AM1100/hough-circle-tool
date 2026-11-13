"""Hough gradient circle detection shared by the GUI and CLI."""
import math
from dataclasses import asdict, dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class Parameters:
    dp: float = 1.0
    min_dist: float = 250
    param1: float = 100
    param2: float = 35
    min_radius: int = 165
    max_radius: int = 190
    blur: int = 5

    def __post_init__(self):
        for key, value in asdict(self).items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f'{key} 必须是有限数字')
        if not 1 <= self.dp <= 8 or not 1 <= self.min_dist <= 10000:
            raise ValueError('dp 必须在 1–8；最小圆心距离必须在 1–10000')
        if not 1 <= self.param1 <= 1000 or not 1 <= self.param2 <= 1000:
            raise ValueError('阈值必须在 1–1000')
        if any(int(v) != v for v in (self.min_radius, self.max_radius, self.blur)):
            raise ValueError('半径与滤波核必须是整数')
        if not 0 <= self.min_radius < self.max_radius <= 10000:
            raise ValueError('半径需满足 0 ≤ 最小半径 < 最大半径 ≤ 10000')
        if self.blur not in (1, 3, 5, 7, 9, 11):
            raise ValueError('滤波核需为 1、3、5、7、9 或 11')


PRESETS = {
    'coins': Parameters(),
    'cookie-plate': Parameters(min_dist=350, param2=30, min_radius=230, max_radius=265),
}


def detect(data: bytes, parameters: Parameters):
    image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError('无法读取图片，请导入有效的 JPG 或 PNG 文件')
    height, width = image.shape[:2]
    if height * width > 12_000_000:
        raise ValueError('图片超过 1200 万像素，请先缩小图片')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if parameters.blur > 1:
        gray = cv2.medianBlur(gray, int(parameters.blur))
    found = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, parameters.dp, parameters.min_dist,
                            param1=parameters.param1, param2=parameters.param2,
                            minRadius=int(parameters.min_radius), maxRadius=int(parameters.max_radius))
    circles = [] if found is None else sorted(found[0].tolist(), key=lambda c: c[0])
    annotated = image.copy()
    for index, (x, y, radius) in enumerate(circles, 1):
        center = (round(x), round(y))
        cv2.circle(annotated, center, round(radius), (40, 210, 25), 3, cv2.LINE_AA)
        cv2.drawMarker(annotated, center, (20, 50, 240), cv2.MARKER_CROSS, 14, 2)
        cv2.putText(annotated, str(index), (center[0] + 9, center[1] - 9),
                    cv2.FONT_HERSHEY_SIMPLEX, .7, (20, 50, 240), 2, cv2.LINE_AA)
    ok, png = cv2.imencode('.png', annotated)
    if not ok:
        raise ValueError('标注图片编码失败')
    return png.tobytes(), {'width': width, 'height': height, 'count': len(circles),
                          'circles': [{'x': round(x, 2), 'y': round(y, 2), 'radius': round(r, 2)} for x, y, r in circles],
                          'parameters': asdict(parameters)}
