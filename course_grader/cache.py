from rc_django.cache_implementation import TimedCache
from rc_django.cache_implementation.memcache import MemcachedCache
import re

ONE_MINUTE = 60
ONE_HOUR = 60 * 60
ONE_DAY = 60 * 60 * 24


def get_cache_time(service, url):
    if 'sws' == service:
        if re.match(r'^/student/v\d/term/current', url):
            return 10 * ONE_MINUTE
        if re.match(r'^/student/v\d/term/', url):
            return ONE_DAY
        if re.match(r'^/student/v\d/course/', url):
            return 10 * ONE_MINUTE
        if re.match(r'^/student/v\d/section', url):
            return 10 * ONE_MINUTE
        return ONE_MINUTE

    if 'pws' == service:
        return ONE_HOUR


class RestClientsCache(TimedCache):
    def getCache(self, service, url, headers):
        return self._response_from_cache(
            service, url, headers, get_cache_time(service, url))

    def processResponse(self, service, url, response):
        return self._process_response(service, url, response)


class RestClientsMemcachedCache(MemcachedCache):
    def get_cache_expiration_time(self, service, url):
        return get_cache_time(service, url)
