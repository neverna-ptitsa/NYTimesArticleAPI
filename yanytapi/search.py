import requests
import time
import json
import logging

_log = logging.getLogger('yanytapi.search')

API_ROOT = 'http://api.nytimes.com/svc/search/v2/articlesearch.'

API_SIGNUP_PAGE = 'http://developer.nytimes.com/docs/reference/keys'


class NoAPIKeyException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnauthorizedException(Exception):
    pass


class TooManyRequestsException(Exception):
    pass


class UnknownException(Exception):
    pass


class Meta:
    def __init__(self, args):
        self.hits = None
        self.offset = None
        self.time = None
        self.__dict__.update(args)

    def __str__(self):
        return json.dumps(self.__dict__, default=lambda x: x.__dict__)


class Doc:
    def __init__(self, args, meta):
        self._id = None
        self.blog = None
        self.byline = None
        self.document_type = None
        self.headline = None
        self.keywords = None
        self.lead_paragraph = None
        self.meta = None
        self.multimedia = None
        self.news_desk = None
        self.pub_date = None
        self.score = None
        self.section_name = None
        self.snippet = None
        self.source = None
        self.subsectoinName = None
        self.type_of_material = None
        self.uri = None
        self.web_url = None
        self.word_count = None
        self.__dict__.update(args)
        self.meta = meta

    def __str__(self):
        return json.dumps(self.__dict__, default=lambda x: x.__dict__)


class Results:
    def __init__(self, query, key, auto_sleep, sleep_period, response_format, page_limit):
        self.query = query
        self.key = key
        self._cursor = 0
        self._page = 0
        self._hits = 0
        self._current_page = None
        self.auto_sleep = auto_sleep
        self.sleep_period = sleep_period
        self.response_format = response_format
        self.page_limit = page_limit

    def __iter__(self):
        return self

    def __next__(self):
        if self._needs_next_page():
            _log.debug("Getting next page")
            self._get_next_page()
            self._cursor = 0
            self._page += 1
        if self._cursor >= len(self._current_page['response']['docs']):
            _log.debug("Cursor reached %s of %s docs in page %s", self._cursor,
                       len(self._current_page['response']['docs']), self._page)
            raise StopIteration
        result = Doc(self._current_page['response']['docs'][self._cursor], self._meta)
        self._cursor += 1
        return result

    def _needs_next_page(self):
        paged_cursor = self._page * 10 + self._cursor
        no_current_page = self._current_page is None
        no_page_passed = self._query_has_no_page()
        cursor_at_limit = self._cursor >= 10
        hits_remaining = paged_cursor < self._hits
        below_page_limit = self._page < self.page_limit
        return no_current_page or (no_page_passed and cursor_at_limit and hits_remaining and below_page_limit)

    def _query_has_no_page(self):
        return 'page' not in self.query

    def _get_next_page(self):
        paginated_options = self.query.copy()
        if self._query_has_no_page():
            paginated_options['page'] = self._page
        url = '%s%s?%sapi-key=%s' % (
            API_ROOT, self.response_format, _options(paginated_options), self.key
        )
        if self.auto_sleep and self._current_page is not None:
            time.sleep(self.sleep_period)
        req = None
        try:
            req = requests.get(url)
            if req.status_code == 200:
                self._current_page = req.json()
                self._meta = Meta(self._current_page['response']['meta'])
                self._hits = self._meta.hits
                return
            elif req.status_code == 429:
                raise TooManyRequestsException
            elif req.status_code == 401:
                raise UnauthorizedException
            else:
                raise UnknownException
        finally:
            req.close()


def _bool_encode(d):
    """
    Converts boolean values to lowercase strings

    """
    for k, v in d.items():
        if isinstance(v, bool):
            d[k] = str(v).lower()

    return d


def _format_fq(d):
    for k, v in d.items():
        if isinstance(v, list):
            d[k] = ' '.join(map(lambda x: '"' + x + '"', v))
        else:
            d[k] = '"' + v + '"'
    values = []
    for k, v in d.items():
        value = '%s:(%s)' % (k, v)
        values.append(value)
    values = ' AND '.join(values)
    return values


def _options(kwargs):
    """
    Formats search parameters/values for use with API

    :param kwargs: search parameters/values

    """
    kwargs = _bool_encode(kwargs)
    values = ''
    for k, v in kwargs.items():
        if k is 'fq' and isinstance(v, dict):
            v = _format_fq(v)
        elif isinstance(v, list):
            v = ','.join(v)
        values += '%s=%s&' % (k, v)
    return values


class SearchAPI(object):
    def __init__(self, key=None):
        """
        Initializes the articleAPI class with a developer key. Raises an exception if a key is not given.

        Request a key at http://developer.nytimes.com/docs/reference/keys

        :param key: New York Times Developer Key

        """
        self.key = key
        if self.key is None:
            raise NoAPIKeyException(
                'Warning: Missing API Key. Please visit ' + API_SIGNUP_PAGE + ' to register for a key.')

    def search(self, query, response_format='json', key=None, auto_sleep=True, sleep_period=6,
               page_limit=100, **kwargs):
        """
        Calls the API and returns a dictionary of the search results

        :param query: the query to run, will automatically be added to the kwargs argument as the value for key q
        :param auto_sleep: whether or not to pause after each page, avoiding rate limiting exceptions
        :param sleep_period: the duration to pause after each page
        :param response_format: the format that the API uses for its response, either 'json' or 'jsonp'.
        :param key: a developer key. Defaults to key given when the SearchAPI class was initialized.
        :param page_limit: the number of pages to allow. NYT-enforced max is 100.

        """
        if key is None:
            key = self.key
        kwargs['q'] = query
        return Results(kwargs, key, auto_sleep, sleep_period, response_format, page_limit)
