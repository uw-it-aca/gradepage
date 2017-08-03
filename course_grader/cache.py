from rc_django.cache_implementation import TimedCache
from rc_django.models import CacheEntryTimed
import re


class RestClientsCache(TimedCache):
    """ A custom cache implementation for GradePage """

    url_policies = {}
    url_policies["sws"] = (
        (re.compile(r"^/student/v\d/term/current"), 60 * 60),
        (re.compile(r"^/student/v\d/term/"), 60 * 60 * 10),
        (re.compile(r"^/student/v\d/course/"), 60 * 15),
        (re.compile(r"^/student/v\d/section"), 60 * 15),
    )
    url_policies["pws"] = (
        (re.compile(r"^/identity/v\d/person/"), 60 * 60 * 10),
        (re.compile(r"^/identity/v\d/entity/"), 60 * 60 * 10)
    )
    url_policies["gws"] = (
        (re.compile(r"^/group_sws/v\d/group/"), 60 * 2),
    )

    def getCache(self, service, url, headers):
        cache_time = self.getCacheTime(service, url)
        if cache_time is not None:
            return self._response_from_cache(service, url, headers, cache_time)
        else:
            return None

    def deleteCache(self, service, url):
        try:
            entry = CacheEntryTimed.objects.get(service=service, url=url)
            entry.delete()
        except CacheEntryTimed.DoesNotExist:
            return

    def processResponse(self, service, url, response):
        if self.getCacheTime(service, url) is not None:
            return self._process_response(service, url, response)
        else:
            return

    def getCacheTime(self, service, url):
        if service in RestClientsCache.url_policies:
            service_policies = RestClientsCache.url_policies[service]

            for policy in service_policies:
                pattern = policy[0]
                policy_cache_time = policy[1]

                if pattern.match(url):
                    return policy_cache_time
        return
