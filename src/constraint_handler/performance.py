"""
Performance Tracking and Caching Module
"""

import time
from collections import defaultdict
from collections.abc import Iterator
from enum import Enum, auto
from functools import cache, wraps

PERFORMANCE_ACTIVE = True
"""
When False, the route decorator will perform no tracking or caching and will simply return the original function.

So this needs to be True in order for any of the performance tracking or caching features to be applied.
"""
PERFORMANCE_TRACKING = False
"""
When True, detailed performance data will be collected for each decorated function.


This will have a significant overhead, so it should only be enabled during development and debugging!
"""


class CacheMode(Enum):
    """Defines caching strategies for constraint handler functions."""

    NONE = auto()
    """No caching is applied."""

    NATIVE = auto()
    """Leverages Python's built-in functools.cache for fast caching of hashable inputs."""

    MANUAL = auto()
    """Implements a custom caching mechanism that can handle unhashable inputs by using a recursive key generation strategy."""


class Performance:
    """
    Core Performance Tracking Class: Implements the logic for tracking function calls,
    caching behavior, and timing, as well as collecting useful statistics for analysis.
    """

    def __init__(self, active=True, tracking=False):
        """
        Initializes the Performance tracking system.

        Args:
            active (bool): If False, the route decorator will perform no tracking or caching and
              will simply return the original function.
            tracking (bool): If True, detailed performance data will be collected for each decorated function.

        """
        self.active = active
        self.tracking = tracking

        self.stats = defaultdict(
            lambda: {
                "count": 0,
                "cached": 0,
                "repeated": 0,
                "total_time": 0.0,
                "func_time": 0.0,
                "overhead_time": 0.0,
                "seen_args": set(),
                "cache": {},
                "unhashable_args": False,
            }
        )

        self.CONFIG = {
            "cltopy": CacheMode.NATIVE,
            "pythonEnumerateElements": CacheMode.NATIVE,
            "pythonEvalExpr": CacheMode.NATIVE,
            "pythonIsExpr": CacheMode.NATIVE,
            "pythonIsList": CacheMode.NONE,
            "pythonIsString": CacheMode.NATIVE,
            "pythonIsTuple": CacheMode.NATIVE,
            "pythonListElements": CacheMode.NATIVE,
            "pythonListLength": CacheMode.NATIVE,
            "pythonReflect": CacheMode.NONE,
            "pythonReify": CacheMode.NATIVE,
            "pythonScopeToString": CacheMode.NONE,
            "pythonStatementVariables": CacheMode.NATIVE,
            "pythonStringLength": CacheMode.NATIVE,
            "pythonTupleElements": CacheMode.NATIVE,
            "pytocl": CacheMode.MANUAL,
        }

    def route(self, func):
        """
        Unified decorator for routing constraint handler functions through the
        performance tracking and caching system.

        This method routes the given function through the appropriate caching and
        tracking logic based on the configuration specified in self.CONFIG.

        Args:
            func (callable): The function to be decorated and routed through the performance system.
        """
        if not self.active:
            return func

        cache_mode = self.CONFIG.get(func.__name__, CacheMode.NONE)

        match (cache_mode, self.tracking):
            case (CacheMode.NATIVE, False):
                return cache(func)
            case (CacheMode.MANUAL, False):
                return self._manual_cache_wrapper(func)
            case (CacheMode.NATIVE, True) | (CacheMode.MANUAL, True):
                return self._track_and_cache_wrapper(func, use_cache=True)
            case (CacheMode.NONE, True):
                return self._track_and_cache_wrapper(func, use_cache=False)
            case _:
                return func

    def _make_key(self, obj):
        """
        Recursively generates a hashable key for potentially unhashable objects by encoding their type and contents.

        This is used for caching and tracking purposes to identify function inputs.
        """

        obj_type = type(obj)
        if isinstance(obj, (list, tuple, set, frozenset)):
            return (obj_type, tuple(self._make_key(e) for e in obj))
        elif isinstance(obj, dict):
            return (obj_type, frozenset((self._make_key(k), self._make_key(v)) for k, v in obj.items()))
        try:
            hash(obj)
        except TypeError:
            if hasattr(obj, "__dict__"):
                return (obj_type, self._make_key(vars(obj)))
            return (obj_type, repr(obj))
        return (obj_type, obj)

    def _safe_deepcopy(self, obj):
        """
        Deep copies Python collections to prevent cache mutation.
        Materializes one-shot iterators and safely ignores C-extensions like clingo.Symbol.
        """

        if isinstance(obj, (map, Iterator)):
            return [self._safe_deepcopy(e) for e in obj]

        obj_type = type(obj)
        if obj_type is list:
            return [self._safe_deepcopy(e) for e in obj]
        elif obj_type is dict:
            return {self._safe_deepcopy(k): self._safe_deepcopy(v) for k, v in obj.items()}
        elif obj_type is set:
            return {self._safe_deepcopy(e) for e in obj}
        elif obj_type is tuple:
            return tuple(self._safe_deepcopy(e) for e in obj)

        return obj

    def _manual_cache_wrapper(self, func):
        """
        Implements a manual caching mechanism for functions that may receive unhashable inputs.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            stats = self.stats[func.__name__]
            cache_dict = stats["cache"]
            key = (self._make_key(args), self._make_key(kwargs))

            if key in cache_dict:
                stats["cached"] += 1
                return self._safe_deepcopy(cache_dict[key])

            snapshot = self._safe_deepcopy(func(*args, **kwargs))
            cache_dict[key] = snapshot

            return self._safe_deepcopy(snapshot)

        return wrapper

    def _track_and_cache_wrapper(self, func, use_cache):
        """
        Wraps the function to track performance metrics and optionally apply caching based on the specified mode.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()

            name = func.__name__
            stats = self.stats[name]

            if not stats["unhashable_args"]:
                try:
                    hash((args, frozenset(kwargs.items())))
                except TypeError:
                    stats["unhashable_args"] = True

            arg_key = (self._make_key(args), self._make_key(kwargs))

            if arg_key in stats["seen_args"]:
                stats["repeated"] += 1
            else:
                stats["seen_args"].add(arg_key)

            if use_cache and arg_key in stats["cache"]:
                stats["cached"] += 1
                result = self._safe_deepcopy(stats["cache"][arg_key])

                t_end = time.perf_counter()
                overhead_time = t_end - t0
                func_time = 0.0
            else:
                t_pre_func = time.perf_counter()
                result = func(*args, **kwargs)
                t_post_func = time.perf_counter()

                if use_cache:
                    stats["cache"][arg_key] = self._safe_deepcopy(result)

                t_end = time.perf_counter()
                func_time = t_post_func - t_pre_func
                overhead_time = (t_pre_func - t0) + (t_end - t_post_func)

            stats["count"] += 1
            stats["total_time"] += t_end - t0
            stats["func_time"] += func_time
            stats["overhead_time"] += overhead_time

            return result

        return wrapper


performance = Performance(active=PERFORMANCE_ACTIVE, tracking=PERFORMANCE_TRACKING)
