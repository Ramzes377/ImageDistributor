import imagehash
from PIL import Image


def file_id_for_thread(img_path):
    return img_path, file_id(img_path)


def file_id(img_path):
    try:
        return str(imagehash.dhash(Image.open(img_path), 16))
    except OSError:
        pass

def hamming2(s1, s2):
    try:
        return sum(c1 != c2 for c1, c2 in zip(s1, s2))
    except:
        return float('inf')


def get_similar(cur, file_path):
    key = file_id(file_path)
    min_hash_distance_item = sorted(cur.keys(), key=lambda k: hamming2(k, key))[:5]
    similar_imgs = [path for x in min_hash_distance_item if hamming2(x, key) <= 32 for path in cur[x] if path != file_path]
    return similar_imgs