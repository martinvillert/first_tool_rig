import pymel.core as pm

from ..system.deformer import Deformer

class BlendShape(Deformer):
    @classmethod
    def create(cls, geometry, influences=None):
        bsn = pm.blendShape(geometry, foc=True)[0]
        return BlendShape(bsn)