import base64
import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError

import cv2
import numpy as np
from app import Handler
from detector import PRESETS, Parameters, detect

ROOT = Path(__file__).resolve().parents[1]

class DetectorTests(unittest.TestCase):
    def test_real_photos_and_export(self):
        expected = {'coins': [(193.5,192.5,179),(567.5,191.5,179)], 'cookie-plate': [(262.5,258.5,245)]}
        for name, targets in expected.items():
            with self.subTest(name=name):
                data=(ROOT/'examples'/f'{name}.jpg').read_bytes()
                png,result=detect(data,PRESETS[name])
                self.assertEqual(result['count'],len(targets))
                for circle,(x,y,r) in zip(result['circles'],targets):
                    self.assertAlmostEqual(circle['x'],x,delta=5)
                    self.assertAlmostEqual(circle['y'],y,delta=5)
                    self.assertAlmostEqual(circle['radius'],r,delta=5)
                output=cv2.imdecode(np.frombuffer(png,np.uint8),cv2.IMREAD_COLOR)
                original=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_COLOR)
                self.assertEqual(output.shape,original.shape)
                self.assertFalse(np.array_equal(output,original))

    def test_bad_parameters_and_images(self):
        for values in ({'dp':0},{'blur':4},{'min_radius':300,'max_radius':1},{'dp':float('nan')},{'blur':3.5},{'param2':0}):
            with self.subTest(values=values),self.assertRaises(ValueError):
                Parameters(**values)
        with self.assertRaises(ValueError):
            detect(b'not an image',Parameters())

    def test_no_circles(self):
        _,data=cv2.imencode('.png',np.zeros((100,100,3),np.uint8))
        _,result=detect(data.tobytes(),Parameters(min_radius=10,max_radius=40))
        self.assertEqual(result['count'],0)

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def post(self,payload,origin=None):
        headers={'Content-Type':'application/json'}
        if origin: headers['Origin']=origin
        request=urllib.request.Request(self.url+'/api/detect',json.dumps(payload).encode(),headers)
        return urllib.request.urlopen(request)
    def test_page_and_detection(self):
        with urllib.request.urlopen(self.url) as response:
            self.assertIn('导出标注 PNG',response.read().decode())
        from dataclasses import asdict
        payload={'image':base64.b64encode((ROOT/'examples/coins.jpg').read_bytes()).decode(),'parameters':asdict(PRESETS['coins'])}
        with self.post(payload) as response:
            result=json.load(response);self.assertEqual(result['count'],2)
            self.assertTrue(base64.b64decode(result['image']).startswith(b'\x89PNG'))
    def test_errors_and_service_survives(self):
        with self.assertRaises(HTTPError) as error:
            self.post({'image':'bad','parameters':{}})
        self.assertEqual(error.exception.code,400)
        error.exception.close()
        with self.assertRaises(HTTPError) as error:
            self.post({},origin='https://unrelated.example')
        self.assertEqual(error.exception.code,403)
        error.exception.close()
        with urllib.request.urlopen(self.url+'/api/presets') as response:
            self.assertIn('coins',json.load(response))

if __name__=='__main__': unittest.main()
