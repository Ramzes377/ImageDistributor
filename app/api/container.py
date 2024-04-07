import os
from json import JSONDecodeError
from typing import Any, Optional, Callable

from send2trash import send2trash
from pydantic import BaseModel, Field, ValidationError

from app.api.cache import Cache
from app.api.core.lens import Lens


class Container(BaseModel):
    """
    Instance of this class should be used for 2 purposes:
        - Shared variables
        - Saving state of instance as dill dump
    """

    sort_directory: str = os.path.abspath('./')
    transfer_directories: set[str] = Field(default_factory=set)

    cache: Cache = Field(default_factory=Cache)

    current_image: Optional[str] = None
    remove_method: Callable = Field(default=send2trash, exclude=True)

    lens_settings: Lens = Field(default_factory=Lens)

    def add_cache(self, items: list[Any]) -> None:
        self.cache.add(items)
        self.save()

    @classmethod
    @property
    def path(self) -> str:
        return os.path.join(os.getcwd(), 'app_data.json')

    def save(self) -> None:
        os.system(f"attrib -h {self.path}")  # UNHIDE cache  file
        with open(self.path, 'w', encoding="utf-8") as f:
            f.write(self.model_dump_json())
        os.system(f"attrib +h {self.path}")  # HIDE cache  file


def build_container(container_path: str = Container.path) -> Container:
    try:
        with open(container_path, encoding="utf-8") as f:
            data = f.read()
        container_ = Container.parse_raw(data)
        container_.cache.load(container_.sort_directory)
    except (FileNotFoundError, JSONDecodeError, ValidationError) as e:
        container_ = Container()
        container_.save()

    return container_


container = build_container()
