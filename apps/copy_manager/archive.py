import os
import pickle

from collections import defaultdict

from widgets.filelist import images_names_generator as ING
from apps.copy_manager.cache_filler import UnregisteredFilesLoader, UnregisteredFilesMarker
from .progress_bar import bar
from .auxiliary import file_id, get_similar



class Archive:
    _cache = defaultdict(dict)
    reverse_cache = defaultdict(dict)

    def __init__(self, parent, copy_container):
        self.parent = parent
        self.bar = bar(parent)
        self._container = []
        self._copy_container = copy_container
        self.files_loader = UnregisteredFilesLoader(self.path, self.parent, self.bar, self.transfer_data_to_cache)
        self.files_marker = UnregisteredFilesMarker(self.path, self.parent, self.bar, self._container, self._copy_container)

    def set_mark_methods(self, mark, unmark):
        self.mark = mark
        self.unmark = unmark

        self.files_marker.mark = mark
        self.files_marker.unmark = unmark

    def discard_removed_images(self):
        for id, files in self._cache[self.path].items():
            files_cpy = files.copy()
            for file in files_cpy:
                if not os.path.isfile(file):
                    self._cache[self.path][id].discard(file)

    def get_unregistered_files(self, folders):
        all_files = [os.path.abspath(f'{path}/{img_file}') for path in folders for img_file in ING(path)]
        if self._cache and self._cache.get(self.path):
            unregistered = [f for f in all_files if not self.reverse_cache[self.path].get(f)]
            return unregistered
        return all_files

    def __call__(self, folders):
        if not self._cache:
            self.load()
        self.discard_removed_images()
        self.files_loader.start_hashing(image_list=self.get_unregistered_files(folders))

    def transfer_data_to_cache(self):
        prev_length = len(self._cache[self.path])
        if not self._cache.get(self.path):
            self._cache[self.path] = self.files_loader.tmp_cache
            self.reverse_cache[self.path] = self.files_loader.tmp_r_cache
        else:
            for k, v in self.files_loader.tmp_cache.items():
                self._cache[self.path][k].update(v)
                for file in v:
                    self.reverse_cache[self.path][file] = k

        self.save()

        print(f'Quantity of new records: {len(self._cache[self.path]) - prev_length}')
        # mark copy in UI file list
        self.files_marker.start_marking(self._cache[self.path])

    def marking(self, file, deleting=False, from_filelist=False):
        _, filename = os.path.split(file)
        cached_copies = get_similar(self._cache[self.path], file)
        copies_existed = [f for f in cached_copies if os.path.exists(f)]
        if copies_existed:
            self.mark(filename)
            for copy in copies_existed:  # any copy still exist
                self._copy_container.add((file, copy))

        for f in cached_copies:
            if f in self._container:
                self.mark(filename)
                self._copy_container.add((f, file))

        if from_filelist:
            self.parent.scrollable.fill_set()

    def load(self):
        try:
            with open(os.path.join(os.path.abspath('/'), '.hashed'), 'rb+') as f:
                self._cache = pickle.load(f)

            for path, cache in self._cache.items():
                for id, files in cache.items():
                    for file in files:
                        self.reverse_cache[path][file] = id

        except (FileNotFoundError, EOFError, AttributeError):
            with open(os.path.join(os.path.abspath('/'), '.hashed'), 'wb') as f:
                pickle.dump(self._cache, f)
            self.load()
        finally:
            os.system("attrib +h .hashed")  # HIDE cache  file

    def save(self):
        with open(os.path.join(os.path.abspath('/'), '.hashed'), 'rb+') as f:
            pickle.dump(self._cache, f)

    def edit(self, add_path, remove_path):
        if self._cache:
            if not self._cache.get(self.path):
                self._cache[self.path] = defaultdict(set)
                self.reverse_cache[self.path] = {}

            cache = self._cache[self.path]
            r_cache = self.reverse_cache[self.path]
            if add_path is not None:
                try:
                    key = self.reverse_cache[self.path].get(add_path) or file_id(add_path)
                except AttributeError:
                    return
                cache[key].add(add_path)
                r_cache[add_path] = key
            elif remove_path is not None:
                key = file_id(remove_path)
                cache[key].discard(remove_path)
                r_cache.pop(remove_path)

    @property
    def path(self):
        return self.parent.path
