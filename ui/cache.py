import pickle
import os


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Cache(metaclass=SingletonMeta):
    DIR = os.getcwd() + "\\ui\\cache"
    NAME = "__ui_cache__.pkl"
    PATH = os.path.join(DIR, NAME)

    def __init__(self):
        self.files = {
            "trainReference": None,
            "parseMidi": None,
        }

        self.trainPrams = {
            "population": 10,
            "mutation": 0.8,
            "iteration": 1000,
            "withCompany": True,
        }

    @staticmethod
    def load() -> "Cache":
        try:
            os.makedirs(Cache.DIR, exist_ok=True)
            with open(Cache.PATH, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return Cache()

    def save(self):
        os.makedirs(Cache.DIR, exist_ok=True)
        with open(Cache.PATH, "wb") as f:
            pickle.dump(self, f)
