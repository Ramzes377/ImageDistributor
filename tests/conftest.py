import os

from pytest import fixture

from app.api import Container, IMAGE_FORMATS


@fixture(scope="function")
def prepare_data():
    """Generates all provided image formats as temp data"""

    path = os.path.join(os.getcwd(), 'tests/data')

    created_files = []
    for ext in IMAGE_FORMATS:
        filepath = os.path.join(path, f'img.{ext}')
        with open(filepath, 'w') as f:
            f.write('')
        created_files.append(filepath)

    yield

    for file in created_files:
        os.remove(file)


@fixture(scope="function")
def container():
    """Creates a container and delete after test execution"""

    container = Container()
    container.save_name = 'test.json'

    yield container
