from dataclasses import dataclass


@dataclass
class Constants:
    lesser_resolution: str = 'У изображения {0} меньше разрешение!'
    in_sort_directory: str = 'Изображение {0} находится в сортировочной дирректории!'
    is_copy_name: str = 'Изображение {0} предположительно является копией!'
    equal_imgs: str = 'Предположительно изображения идентичны почти полностью.'


constants = Constants()
