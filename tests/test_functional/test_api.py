import os

from app.api.utils import directory_images_gen, ImageHash


def test_images_list(prepare_data):
    res = list(directory_images_gen('./tests/data'))
    assert len(res) == 7


def test_container(container):

    assert container.current_image is None
    assert isinstance(container.directory, str)

    container.current_image = 'abc'
    container.save()

    container.from_json()
    assert container.current_image == 'abc'

    os.remove(os.path.join(os.getcwd(), container.save_name))


def test_cache(container):

    base = os.path.join(os.getcwd(), 'tests\\data')
    cache = container.cache

    cat_path = os.path.join(base, 'cat.jpg')
    cache.add([ImageHash(cat_path, "0000000000")])
    folder_cache = cache.cache[base]

    img_hash: str = next(iter(folder_cache))
    assert cat_path in folder_cache[img_hash]

    # add 3 images: 2 not existed, and copy of already cached
    cache.add(ImageHash(os.path.join(base, name), "0000000001")
              for name in ('./1', './2'))
    cat_copy = os.path.join(base, 'cat-copy.jpg')
    cache.add([ImageHash(cat_copy, '0000000000')])

    # not existed files don't save to cache
    assert cat_copy in folder_cache[img_hash] and len(folder_cache[img_hash]) == 2




