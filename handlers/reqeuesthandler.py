import requests
import random
import threading
from handlers import proxyhandler
import logging
import handlers.logger

logger = handlers.logger.setup_logger('request_log', 'log/request_log.log', level=logging.INFO)


def set_proxy():
    if proxyhandler.proxies:
        proxy = random.choice(proxyhandler.proxies)
        proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy
        }
        return proxies, proxy
    else:
        threading.Thread(target=proxyhandler.get_proxies).start()
        return None, None


def reqhandler(url, method, headers=None, data=None, files=None):
    for i in range(0, 5):
        if i < 4:
            proxies, proxy = set_proxy()
        else:
            proxies, proxy = None, None
        try:
            if method == 'get':
                r = requests.get(url=url, headers=headers, proxies=proxies, timeout=5)
            elif method == 'post':
                r = requests.post(url=url, headers=headers, data=data, proxies=proxies, files=files, timeout=5)
            else:
                return None
            logger.info('SUCCESS: Request ' + method + ' ' + url + ' ' + str(proxy))
            return r
        except Exception as e:
            print(e)
            logger.info('FAILED: Request ' + method + ' ' + url + ' ' + str(proxy))
            if proxyhandler.proxies and proxy:
                proxyhandler.proxies.remove(proxy)
    return None
