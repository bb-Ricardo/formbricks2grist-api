import functools
import time
from html.parser import HTMLParser
from io import StringIO


def grab(structure=None, path=None, separator=".", fallback=None):
    """
        get data from a complex object/json structure with a
        "." separated path information. If a part of a path
        is not present then this function returns the
        value of fallback (default: "None").

        example structure:
            data_structure = {
              "rows": [{
                "elements": [{
                  "distance": {
                    "text": "94.6 mi",
                    "value": 152193
                  },
                  "status": "OK"
                }]
              }]
            }
        example path:
            "rows.0.elements.0.distance.value"
        example return value:
            15193

        Parameters
        ----------
        structure: dict, list, object
            structure to extract data from
        path: str
            nested path to extract
        separator: str
            path separator to use. Helpful if a path element
            contains the default (.) separator.
        fallback: dict, list, str, int
            data to return if no match was found

        Returns
        -------
        str, dict, list
            the desired path element if found, otherwise None
    """

    max_recursion_level = 100

    current_level = 0
    levels = len(path.split(separator))

    if structure is None or path is None:
        return fallback

    # noinspection PyBroadException
    def traverse(r_structure, r_path):
        nonlocal current_level
        current_level += 1

        if current_level > max_recursion_level:
            return fallback

        for attribute in r_path.split(separator):
            if isinstance(r_structure, dict):
                r_structure = {k.lower(): v for k, v in r_structure.items()}

            try:
                if isinstance(r_structure, list):
                    data = r_structure[int(attribute)]
                elif isinstance(r_structure, dict):
                    data = r_structure.get(attribute.lower())
                else:
                    data = getattr(r_structure, attribute)

            except Exception:
                return fallback

            if current_level == levels:
                return data if data is not None else fallback
            else:
                return traverse(data, separator.join(r_path.split(separator)[1:]))

    return traverse(structure, path)


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def time_cache(max_age, maxsize=128, typed=False):
    """Least-recently-used cache decorator with time-based cache invalidation.
    Source: https://stackoverflow.com/a/63674816

    Args:
        max_age: Time to live for cached results (in seconds).
        maxsize: Maximum cache size (see `functools.lru_cache`).
        typed: Cache on distinct input types (see `functools.lru_cache`).
    """
    def _decorator(fn):
        @functools.lru_cache(maxsize=maxsize, typed=typed)
        def _new(*args, __time_salt, **kwargs):
            return fn(*args, **kwargs)

        @functools.wraps(fn)
        def _wrapped(*args, **kwargs):
            return _new(*args, **kwargs, __time_salt=int(time.time() / max_age))

        return _wrapped

    return _decorator
