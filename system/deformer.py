class Deformer(object):
    def __init__(self, node):
        self._node = node

    @classmethod
    def create(cls, geometry, influences=None):
        raise Exception("create has not been defined for this deformer")

    def load_data(cls, path=""):
        raise Exception("create has not been defined for this deformer")
