import http.client
import json
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import threading
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from serve_app import AppHandler

class LocalHttpBoundary(unittest.TestCase):
    def setUp(self):
        self.server=ThreadingHTTPServer(('127.0.0.1',0),AppHandler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
    def request(self,headers):
        connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=2)
        connection.request('POST','/api/generate',body=b'{}',headers=headers)
        response=connection.getresponse();status=response.status;response.read();connection.close();return status
    def test_cross_origin_and_forged_host_rejected(self):
        self.assertEqual(self.request({'Origin':'https://untrusted.example'}),403)
        self.assertEqual(self.request({'Host':'untrusted.example'}),403)
    def test_negative_and_oversized_content_length_rejected(self):
        self.assertEqual(self.request({'Content-Length':'-1'}),400)
        self.assertEqual(self.request({'Content-Length':'1000001'}),400)

    def project_request(self, payload, headers=None):
        connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=2)
        connection.request('POST','/api/project/validate',body=json.dumps(payload).encode(),headers=headers or {})
        response=connection.getresponse();status=response.status;body=json.loads(response.read())
        connection.close();return status,body

    def test_project_validation_roundtrip_and_body_limit(self):
        data=dict(title='原创草稿',task='revision',brief='',character='',scene='月亮升起来了。',notes='')
        status,body=self.project_request(data)
        self.assertEqual(status,200)
        self.assertEqual(body['project']['scene'],data['scene'])
        self.assertEqual(body['project']['schema_version'],'1.0')
        self.assertEqual(self.project_request(data,{'Content-Length':'8000001'})[0],400)
        self.assertEqual(self.project_request(data,{'Origin':'https://untrusted.example'})[0],403)
        self.assertEqual(self.project_request({**data,'task':'invalid'})[0],400)
