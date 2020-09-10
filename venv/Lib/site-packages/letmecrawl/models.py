from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from six import with_metaclass

import sys
import time
import logging
import threading

from .request import test_proxy
from operator import attrgetter

if sys.version_info[0] < 3:
    from sys import maxint
else:
    from sys import maxsize as maxint

logger = logging.getLogger(__name__)

THREAD_RELOAD_TIME = 60   # seconds

MINIMUM_ELAPSED = 5


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class OrderedTableItem(threading.Thread):
    def __init__(self, proxy):
        self.callback = None
        self.proxy = proxy
        self.elapsed = maxint
        self.keep_alive = True
        super(OrderedTableItem, self).__init__()

    def __str__(self):
        return '{}:{} {}'.format(self.proxy.ip, self.proxy.port, self.elapsed)

    def set_callback(self, callback):
        self.remove_callback = callback

    def run(self):
        while self.keep_alive:
            try:
                # TODO add timeout
                start = time.time()
                self.keep_alive = test_proxy(self.proxy.ip, self.proxy.port)
                self.elapsed = time.time() - start
                logger.debug('Elapsed time {}'.format(self.elapsed))
                while time.time() - start + self.elapsed < THREAD_RELOAD_TIME \
                        and self.keep_alive:
                    time.sleep(1)
            except Exception as exp:
                # TODO catch connection exceptions
                # TODO if timeout exception keep alive
                self.keep_alive = False
                logger.debug('Disabling item {}. {}'.format(self, exp))
        self.remove_callback(self)

    def stop(self):
        self.keep_alive = False


class EmptyTableException(Exception):
    pass


class ProxyRequest(object):
    def __init__(self, proxy):
        self.ip = proxy.ip
        self.port = proxy.port

    def __str__(self):
        return '{}:{}'.format(self.ip, self.port)


class OrderedTable(with_metaclass(Singleton, object)):

    def __init__(self):
        self.keep_alive = True
        self.table = []

    def add(self, source):
        if not self.exists(source):
            item = OrderedTableItem(source)
            item.daemon = True
            item.set_callback(self.remove)
            self.table.append(item)
            item.start()

    def exists(self, source):
        for item in self.table:
            if (
                item.proxy.ip == source.ip and
                item.proxy.port == source.port
            ):
                return True
        return False

    def remove(self, item):
        try:
            self.table.remove(item)
            logger.debug('Removed {}'.format(item))
        except ValueError:
            logger.debug('Tried to remove {}'.format(item))

    def get_sorted_table(self):
        return sorted(
            filter(lambda x: x.elapsed < MINIMUM_ELAPSED, self.table),
            key=attrgetter('elapsed')
        )

    def first(self):
        if self.size() == 0:
            raise EmptyTableException()
        item = self.get_sorted_table()[0]
        proxy = ProxyRequest(item.proxy)
        self.remove(item)
        return proxy

    def size(self):
        return len(self.table)

    def stop(self):
        logger.debug('Stopping all tasks')
        self.keep_alive = False
        for item in self.table:
            item.stop()

    def alive(self):
        return self.keep_alive
