import requests
import time
from requests import ReadTimeout
from .logger import get_logger

logger = get_logger(__name__)

class Rest:

    def __init__(self, url):
        self.Headers = {"Content-Type": "application/json"}
        self.Url = url
        self.session = requests.Session()
        self.methods = {
            'GET': self.session.get,
            'POST': self.session.post,
            'PUT': self.session.put,
            'DELETE': self.session.delete
        }

    def http_request(self, method, path, times=5, **kwargs):
        """
        发起请求
        @param method: 方法
        @param path: 目录
        @param times: 失败重试次数
        @param kwargs: 参数
        @return: 成功 True，res.json()，失败 False, res.text
        """
        data = {key: value for key, value in kwargs.items() if value is not None}
        try:
            logger.info(f"url+path {self.Url + path}")
            res = self.methods[method.upper()](self.Url + path, json=data, headers=self.Headers, timeout=60)
        except (ConnectionError, ReadTimeout) as e:
            logger.warning(f'ConnectionError or ReadTimeout: {e}')
            times = times - 1
            if times:
                time.sleep(10)
                return self.http_request(method, path, times=times, **kwargs)
            else:
                time.sleep(300)
                return self.http_request(method, path, times=5, **kwargs)
        except Exception as e:
            logger.error(f'Exception: {e}')
            if times:
                time.sleep(10)
                return self.http_request(method, path, times=times, **kwargs)
            else:
                time.sleep(300)
                return self.http_request(method, path, times=5, **kwargs)

        if res.status_code // 2 == 100:
            return True, res.json()
        else:
            if res.status_code // 4 == 100:
                logger.error(f'[Rest-http_request]StatusCode: {res.status_code}, InvalidResponse: {res.json()}')
            return False, res.json()
