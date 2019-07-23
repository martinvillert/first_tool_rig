import pymel.core as pm

from ..system.deformer import Deformer

class Lattice(Deformer):
    @classmethod
    def create(cls, geometry, influences=None):
        lattice = pm.lattice(geometry, oc=True)[0]
        return Lattice(lattice)
