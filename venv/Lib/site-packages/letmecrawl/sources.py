from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import json

from . import request


ip_pattern = '(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\:\d{2,5}'
ip_tag_pattern = '(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)<\/td><td>\d{2,5}'


class ParserNotFoundException(Exception):
    pass


class Source(object):
    def __init__(self, url):
        self.url = url

    @staticmethod
    def factory(name, url):
        if name == 'spy': return Spys(url)
        if name == 'stamparm': return Stamparm(url)
        if name == 'us-proxy': return UsProxy(url)
        if name == 'proxynova': return ProxyNova(url)
        raise ParserNotFoundException


class Proxy(object):
    def __init__(self, url):
        self.ip, port = url.split(':')
        self.port = int(port)


class Spys(Source):
    def list(self):
        content = request.read(self.url)
        ips = re.findall(ip_pattern, content)
        return map(Proxy, ips)


class Stamparm(Source):
    def list(self):
        content = request.read(self.url)
        return [
            Proxy('{}:{}'.format(s.get('ip'), s.get('port')))
            for s in json.loads(content) if s.get('proto', '') == 'http'
            ]


class UsProxy(Source):
    def list(self):
        content = request.read(self.url)
        ips = re.findall(ip_tag_pattern, content)
        return [Proxy(ip.replace('</td><td>', ':')) for ip in ips]


class ProxyNova(Source):
    def list(self):
        content = request.read(self.url)
        pattern = """document.write\('([\d\.]*)'\.substr\((\d)\)\W\+\W'([\d\.]*)'.*\n.*.*\n.*\n.*proxies">(\d*)"""
        ips = re.findall(pattern, content)
        return [Proxy(self._format(ip)) for ip in ips if len(ip) == 4]

    def _format(self, raw):
        return raw[0][int(raw[1]):] + raw[2] + ":" + raw[3]