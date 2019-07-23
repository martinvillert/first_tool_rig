import pymel.core as pm

from ..system.deformer import Deformer


class Cluster(Deformer):

    @classmethod
    def create(cls, geometry, influences=None):
        cluster = pm.cluster(geometry)[1]
        return Cluster(cluster)