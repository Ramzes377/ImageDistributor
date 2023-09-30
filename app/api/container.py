import json
import os
from collections import defaultdict
from dataclasses import dataclass, field

from app.api.cache import Cache
from app.api.utils import Singleton


class EnhancedJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, set):
            return list(o)
        if isinstance(o, defaultdict):
            return {n: v if not isinstance(v, set) else list(v)
                    for n, v in o.items()}
        if isinstance(o, Cache):
            return o.json()

        return super().default(o)


def cache_inner_struct():
    return defaultdict(set)


@dataclass(slots=True)
class Container(metaclass=Singleton):
    """
    Instance of this class should be used for 2 purposes:
        - Shared variables
        - Saving state of instance as dill dump
    """
    run_directory = os.getcwd()

    save_name: str = 'app_data.json'
    directory: str = os.path.abspath('./')

    current_image: str = None

    cache: Cache = field(default_factory=Cache)

    @property
    def path(self) -> str:
        return os.path.join(self.run_directory, self.save_name)

    @property
    def json(self) -> dict:
        dct = {name: getattr(self, name) for name in self.__slots__}
        return json.dumps(dct, cls=EnhancedJSONEncoder)

    def save(self) -> None:
        os.system(f"attrib -h {self.path}")  # UNHIDE cache  file
        with open(self.path, 'w') as f:
            f.write(self.json)
        os.system(f"attrib +h {self.path}")  # HIDE cache  file

    def from_json(self):
        with open(self.path) as f:
            data = json.load(f)

        for key, value in data.items():
            _type = self.__annotations__[key]
            v = value if issubclass(_type, (int, str, list, dict)) \
                else _type.from_json(value)
            setattr(self, key, v)

    def load(self, rm_unexisted=True):
        try:
            self.from_json()
            self.cache.rebuild_reversed_cache(self.directory)

            if rm_unexisted:
                self.cache.remove_unregistered(self.directory)

        except (FileNotFoundError, EOFError, AttributeError):
            self.save()  # create init dump


container = Container()

