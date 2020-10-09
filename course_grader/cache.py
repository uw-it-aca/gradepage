from memcached_clients import RestclientPymemcacheClient
import re

ONE_MINUTE = 60
ONE_HOUR = 60 * 60
ONE_DAY = 60 * 60 * 24


class RestClientsMemcachedCache(RestclientPymemcacheClient):
    def get_cache_expiration_time(self, service, url, status=None):
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
