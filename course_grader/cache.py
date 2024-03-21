# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from memcached_clients import RestclientPymemcacheClient
import re

ONE_MINUTE = 60
ONE_HOUR = 60 * 60
ONE_DAY = 60 * 60 * 24


class RestClientsCache(RestclientPymemcacheClient):
    def get_cache_expiration_time(self, service, url, status=None):
        if 'sws' == service:
            if re.match(r'^/student/v\d/term/\d{4}', url):
                return ONE_DAY
            if re.match(r'^/student/v\d/graderoster', url):
                return None
            return ONE_MINUTE * 10

        if 'pws' == service:
            return ONE_HOUR
