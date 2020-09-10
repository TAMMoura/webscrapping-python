from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

if sys.version_info[0] < 3:
    import httplib
    from urlparse import urlparse
else:
    import http.client as httplib
    from urllib.parse import urlparse

check_endpoint = 'http://ifconfig.co/'


def request(url, method='GET', proxy_ip=None, proxy_port=None, timeout=5):
    parts = urlparse(url)

    connection = httplib.HTTPSConnection if parts[0] == 'https' else httplib.HTTPConnection

    if proxy_ip:
        con = connection(proxy_ip, proxy_port, timeout=timeout)
        path = url
    else:
        con = connection(parts.netloc)
        path = parts.path or '/'
    con.request(method, path)
    return con.getresponse()


def test_proxy(proxy_ip=None, proxy_port=None):
    return proxy_ip in request(
        url=check_endpoint,
        method='GET',
        proxy_ip=proxy_ip,
        proxy_port=proxy_port
    ).read().decode('utf-8')


def read(url):
    # TODO use contextual to close
    con = request(url)
    content = con.read()
    con.close()
    return content.decode('utf-8')
