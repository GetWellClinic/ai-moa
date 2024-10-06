from huey.contrib.djhuey import HUEY
from src.utils.workflow import huey

if __name__ == '__main__':
    huey.start()
