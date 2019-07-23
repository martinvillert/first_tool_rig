import pymel.core as pm

from ..system.deformer import Deformer

class NonLinear(Deformer):
    @classmethod
    def create(cls, geometry, type="bend",influences=None):
        nonlinear = pm.nonLinear(geometry, type=type)[0]
        return NonLinear(nonlinear)