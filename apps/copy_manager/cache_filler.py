import os
from collections import defaultdict
from workstuff.basethread import BaseThread
from multiprocessing.dummy import Pool as ThreadPool
from .auxiliary import file_id_for_thread, get_similar


def hashing_handler(gen, q):
    pool = ThreadPool(24)
    for tpl in pool.imap_unordered(file_id_for_thread, gen):
        if tpl is not None:
            q.put(tpl)
    pool.close()
    pool.join()
    print('Caching thread ends hard work!')

class UnregisteredFilesLoader:
    filling_cache_thread = BaseThread(None, lambda x: None, [], lambda: None, lambda: None)

    def __init__(self, path, parent, bar, final_work):
        self._parent_parent = parent
        self.bar = bar
        self.path = path
        self.final_work = final_work

    def start_hashing(self, image_list):
        self.bar(len(image_list))

        self.tmp_cache = defaultdict(set)
        self.tmp_r_cache = {}
        self._counter = 0

        # starting filling cache thread
        self.filling_cache_thread = BaseThread(self._parent_parent,
                                               thread_handler=hashing_handler,
                                               thread_args=[image_list],
                                               q_handler=self.get_cache_data,
                                               final_handler=self.final_work)

    def get_cache_data(self, args, with_report = True):
        path, id = args
        self.tmp_cache[id].add(path)
        self.tmp_r_cache[path] = id
        if with_report and self._counter % 10 == 0:
            if self._parent_parent._is_hidden:
                self._parent_parent.root.update()
            else:
                self.bar.set(self._counter)
        self._counter += 1



def prepare_files_to_mark(files, cache, q):
    for file in files:
        _, filename = os.path.split(file)
        file_copyies = get_similar(cache, file)
        copys = [f for f in file_copyies if os.path.exists(f)]
        if copys:
            q.put(('m', filename))
            for copy in copys:  # any copy still exist
                q.put(('a', (file, copy)))

        for f in file_copyies:
            if f in files:
                q.put(('m', filename))
                q.put(('a', (f, file)))

class UnregisteredFilesMarker:
    mark = lambda: None
    umark = lambda: None

    def __init__(self, path, parent, bar, archive_container, copy_containter):
        self._parent_parent = parent
        self.path = path
        self.bar = bar
        self._archive_container = archive_container
        self._copy_container = copy_containter


    def start_marking(self, cache):
        self.link_operations()
        self.marking_thread = BaseThread(self._parent_parent, thread_handler=prepare_files_to_mark,
                                         q_handler=self.marking_handler,
                                         final_handler=self.marking_ending,
                                         thread_args=(self._archive_container, cache))

    def link_operations(self):
        if not hasattr(self, 'operations'):
            self.operations = {'m': self.__dict__['mark'],
                               'u': self.__dict__['unmark'],
                               'a': self._copy_container.add}

    def marking_handler(self, args):
        operation, file = args
        self.operations[operation](file)


    def marking_ending(self):
        self.bar.set_percent(100)
        self._parent_parent.scrollable.fill_set()
        self._parent_parent.autochoose['state'] = 'normal'
        self._parent_parent.deletechoosen['state'] = 'normal'
