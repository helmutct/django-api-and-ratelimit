from django.core.cache import cache
from functools import wraps
from django.http import HttpResponseForbidden

def rate_limit(rate):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, *args, **kwargs):
            ip_address = self.request.META.get('REMOTE_ADDR')
            cache_key = f'ratelimit_{ip_address}'
            
            count = cache.get(cache_key, 0)
            if count >= rate:
                return HttpResponseForbidden("Rate limit exceeded")

            cache.set(cache_key, count + 1, timeout=5)  # Assuming 5 seconds timeout
            return view_func(self, *args, **kwargs)

        return _wrapped_view
    return decorator
