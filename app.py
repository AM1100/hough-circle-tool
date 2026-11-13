"""Local circle detection GUI. Images stay on the local computer."""
import argparse
import base64
import binascii
import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import cv2
from detector import PRESETS, Parameters, detect

ROOT = Path(__file__).resolve().parent
MAX_BODY = 24 * 1024 * 1024


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, content_type='application/json; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/':
            self.reply(200, (ROOT/'web/index.html').read_bytes(), 'text/html; charset=utf-8')
        elif path == '/api/presets':
            self.reply(200, json.dumps({k: asdict(v) for k, v in PRESETS.items()}).encode())
        elif path in ('/examples/coins.jpg', '/examples/cookie-plate.jpg'):
            self.reply(200, (ROOT/path.lstrip('/')).read_bytes(), 'image/jpeg')
        else:
            self.reply(404, b'{}')

    def do_POST(self):
        if self.path != '/api/detect':
            self.reply(404, b'{}'); return
        origin = self.headers.get('Origin')
        if origin and origin != f'http://{self.headers.get("Host")}':
            self.reply(403, b'{"error":"Origin rejected"}'); return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= MAX_BODY:
                raise ValueError('请求图片过大或请求为空（上限 24 MiB）')
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict) or not isinstance(payload.get('image'), str) or not isinstance(payload.get('parameters'), dict):
                raise ValueError('图片或参数格式错误')
            data = base64.b64decode(payload['image'], validate=True)
            png, result = detect(data, Parameters(**payload['parameters']))
            result['image'] = base64.b64encode(png).decode()
            self.reply(200, json.dumps(result).encode())
        except (ValueError, TypeError, binascii.Error, cv2.error) as exc:
            self.reply(400, json.dumps({'error': str(exc)}, ensure_ascii=False).encode())


def main():
    parser = argparse.ArgumentParser(description='本地霍夫圆检测工具')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--input', type=Path, help='命令行模式的输入图片')
    parser.add_argument('--output', type=Path, help='命令行模式的输出 PNG')
    parser.add_argument('--preset', choices=PRESETS, default='coins')
    args = parser.parse_args()
    if args.input:
        if not args.output or args.output.suffix.lower() != '.png':
            parser.error('命令行模式需要 --output，且文件扩展名为 .png')
        try:
            png, result = detect(args.input.read_bytes(), PRESETS[args.preset])
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(png)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except (ValueError, OSError, cv2.error) as exc:
            parser.exit(1, f'错误：{exc}\n')
    else:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
        print(f'请在浏览器打开 http://127.0.0.1:{server.server_port}；Ctrl+C 停止', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == '__main__':
    main()
