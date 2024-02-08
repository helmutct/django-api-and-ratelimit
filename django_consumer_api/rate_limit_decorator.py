from functools import wraps
from django.http import HttpResponse
from django.core.cache import cache

def rate_limit(rate, key_func=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if the request object has a META attribute
            if hasattr(request, 'META'):
                # Get the key for rate-limiting (default to IP address)
                if key_func:
                    key = key_func(request)
                else:
                    key = request.META.get('REMOTE_ADDR', None)

                if not key:
                    # If unable to determine the key, don't apply rate-limiting
                    return view_func(request, *args, **kwargs)

                # Generate a unique cache key based on the view function and the key
                cache_key = f'rate_limit:{view_func.__name__}:{key}'

                # Check if the cache key exists
                if cache.get(cache_key):
                    # If the cache key exists, return 429 Too Many Requests
                    return HttpResponse(status=429)

                # Set the cache key with a timeout based on the rate limit
                cache.set(cache_key, 'true', rate)

            # Call the actual view function
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
