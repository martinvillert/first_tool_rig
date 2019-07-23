import pymel.core as pm

from ..part import Part
from ..system.chain import Chain
from ..system.control import Control

class Head(Part):
    guide_name = "guide_biped_head"
    default_namespace = "guide_C_bipedHead"
    node_part = "biped_head"
    node_side = "C"

    def define_guides(self):

        self.guide_end_LOC = self.namespace + "end_LOC"
        self.guide_start_LOC = self.namespace + "start_LOC"

    def update_build_order(self):
        super(Head, self).update_build_order()
        self.build_order.extend([self.chain,
                                 self.ctrl])

    def chain(self):
        guides = (self.guide_start_LOC, self.guide_end_LOC)
        self.basic_fk=Chain.make_jnt_chain(guides)

    def ctrl(self):
        Control.create_fk_ctrl(chain=self.basic_fk, name_template=self.prefix + "Fk_{number}_CTL")

