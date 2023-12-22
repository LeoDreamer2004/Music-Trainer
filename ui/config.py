import pickle
import os


class Singleton(type):
    """A singleton metaclass."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Get the singleton instance."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Configuration(metaclass=Singleton):
    """The configuration for the parameters used in the UI."""

    DIR = "rsc/config"
    NAME = "__ui_config__.pkl"
    PATH = os.path.join(DIR, NAME)

    def __init__(self):
        """Default configuration"""
        self.ui = {
            "theme": "auto",
            "themeColor": "#0078D7",
        }
        self.files = {
            "outputFolder": os.getcwd() + "\\midi\\",
            "trainReference": None,
            "parseMidi": None,
        }
        self.trainPrams = {
            "population": 10,
            "mutation": 0.8,
            "iteration": 2000,
            "withCompany": True,
        }
        self.openWhenDone = False

    @staticmethod
    def load() -> "Configuration":
        if not os.path.exists(Configuration.PATH):
            return Configuration()

        with open(Configuration.PATH, "rb") as f:
            config: Configuration = pickle.load(f)
            if config._check_valid():
                return config
            else:
                return Configuration()

    def save(self):
        os.makedirs(Configuration.DIR, exist_ok=True)
        with open(Configuration.PATH, "wb") as f:
            pickle.dump(self, f)

    def _check_valid(self):
        for filename in self.files.values():
            if filename is None:
                continue
            if not os.path.exists(filename):
                return False
        return True


cfg = Configuration.load()
