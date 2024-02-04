class Helper:
    def __init__(self):
        pass

    def safe_get(self, dct, *keys):
        for key in keys:
            try:
                dct = dct.get(key)
            except KeyError:
                return None
        return dct