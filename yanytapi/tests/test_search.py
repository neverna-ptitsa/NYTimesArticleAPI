from ..search import *
import os
import time
import pytest
import logging

_log = logging.getLogger('yanytapi.search.test')

api_key = os.environ['API_KEY']


def test_search_no_results():
    api = SearchAPI(api_key)
    results = api.search('sadflkjsdf')
    start = time.perf_counter()
    assert len(list(results)) == 0
    assert time.perf_counter()-start < 6


def test_auto_delay():
    api = SearchAPI(api_key)
    results = api.search('trump')
    start = time.perf_counter()

    _log.debug("%s", results.__next__().__str__())
    for i in range(0, 20):
        results.__next__()
    assert time.perf_counter()-start > 6


def test_backoff_exception():
    with pytest.raises(TooManyRequestsException):
        api = SearchAPI(api_key)
        results = api.search('trump', auto_sleep=False)
        for i in range(0, 200):
            results.__next__()
    time.sleep(70)


def test_page_limit():
    api = SearchAPI(api_key)
    results = api.search('trump', page_limit=2, auto_sleep=False)
    assert len(list(results)) == 20
