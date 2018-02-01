class Config:
    def __init__(self, **entries):
        self.entries = entries

    def __add__(self, other):
        entries = (self.entries.items() + 
                    other.entries.items())
        return Config(**entries)
default_config = Config(color=False, port=8080)
config = default_config + Config(color=True)