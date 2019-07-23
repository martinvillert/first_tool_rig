import pymel.core as pm

from ..system.cluster import Cluster
from ..system.lattice import Lattice
from ..system.blendshape import BlendShape

class DeformerStack(object):
    deformer_dict = {"cluster": Cluster, "ffd": Lattice, "blendShape": BlendShape}

    @classmethod
    def get(cls, geometry):
        full_stack = pm.PyNode(geometry).listHistory()
        return [x.type() for x in full_stack if x.type() in cls.deformer_dict][::-1]

    @classmethod
    def apply(cls, geometry, deformer_list=[]):
        for deformer_type in deformer_list:
            cls.deformer_dict[deformer_type].create(geometry)



# stack = DeformerStack.get("")
# DeformerStack.apply("", deformer_list=stack)