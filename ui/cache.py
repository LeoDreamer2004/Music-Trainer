import pickle


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Cache(metaclass=SingletonMeta):
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
            with open("__ui_cache__.pkl", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return Cache()

    def save(self):
        with open("__ui_cache__.pkl", "wb") as f:
            pickle.dump(self, f)
