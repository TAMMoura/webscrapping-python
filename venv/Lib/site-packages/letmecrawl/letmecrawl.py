from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from six import with_metaclass


import json
import time
import logging
import threading
import pkg_resources

from .sources import Source
from .models import OrderedTable, Singleton
from random import shuffle

logger = logging.getLogger(__name__)

CURATE_RELOAD_TIME = 5 * 60  # seconds


def letmecrawl():
    for proxy in LMC().pop():
        yield proxy


def stop():
    LMC().stop()


def curate():
    resource_package = __name__
    sources = '/sources.json'
    sources_path = pkg_resources.resource_filename(resource_package, sources)

    with open(sources_path) as f:
        sources = [Source.factory(s, u) for (s, u) in json.load(f).items()]

    table = OrderedTable()

    while table.alive():
        all_sources = []
        for s in sources:
            all_sources.extend(s.list())

        shuffle(all_sources)

        for s in all_sources:
            table.add(s)
        # TODO: parametize sleep time
        logger.debug('Current number of items #{}'.format(table.size()))
        start = time.time()
        while time.time() - start < CURATE_RELOAD_TIME and table.alive():
            time.sleep(1)


class LMC(with_metaclass(Singleton, object)):
    def __init__(self):
        self.table = OrderedTable()
        threading.Thread(target=curate).start()

    def __iter__(self):
        return self

    def pop(self,
            wait_rampup=True,
            raise_exception=False):
        while True:
            try:
                yield self.table.first()
            except:
                if raise_exception: raise
                if wait_rampup: continue
                yield None

    def stop(self):
        self.table.stop()
