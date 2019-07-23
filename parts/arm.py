import pymel.core as pm

from ..system.chain import Chain
from ..system.control import Control
from ..parts.limb import Limb
from ..system import transform

class Arm(Limb):

    pv_slice = slice(0, 3)
    limb_slice = slice(1, 4)
    guide_name = "guide_biped_arm"
    default_namespace = "guide_L_biped_Arm"
    node_part = "leg"
    node_side = "L"

    def define_guides(self):
        super(Arm, self).define_guides()
        self.guide_clav_LOC = self.namespace + "clav_LOC"
        self.guide_start_LOC = self.namespace + "start_LOC"
        self.guide_hand_LOC = self.namespace + "hand_LOC"

    def update_build_order(self):
        super(Arm, self).update_build_order()
        self.build_order.extend([
            self.main_ik_ctrl,
            self.clav_fk_build,
            self.clav_ik_build,
            self.clav_build,
        ])

    def main_ik_ctrl(self):
        pm.orientConstraint(self.ik_ctrl, self.ik_chain[-1])

    def clav_fk_build(self):
        self.guide_clav = (self.guide_clav_LOC, self.guide_start_LOC)
        self.fk_clav_chain = Chain.make_jnt_chain(self.guide_clav[0:2],
                                                  name_template=self.prefix + "_FK_clav_{number}_JNT")
        self.clav_grp = pm.createNode("transform", name=self.prefix + "_clav_GRP")
        transform.match(self.fk_clav_chain[0], self.clav_grp)
        self.fk_clav_ctrl = Control.create_fk_ctrl(self.fk_clav_chain,
                                                   name_template=self.prefix + "_FK_clav_{number}_CTRL",
                                                   colour=self.side_colour)

    def clav_ik_build(self):
        self.clav_ik_chain = Chain.make_jnt_chain(self.guide_clav[0:2],
                                                  name_template=self.prefix + "_IK_clav_{number}_JNT")
        self.clav_ik = self.clav_ik_chain.make_ikh(start=0, end=1,
                                                   solver="ikSCsolver",
                                                   name="clav_IKH")
        self.clav_ik_ctrl = Control.make_control(self.clav_ik, name=self.prefix + "clav_ik_CTRL",
                                                 colour=self.side_colour)

    def clav_build(self):
        offset_clav_ik_ctrl = self.clav_ik_ctrl.getParent()
        offset_clav_fk_ctrl = self.fk_clav_ctrl[0].getParent()

        offset_clav_fk_ctrl.setParent(self.clav_ik_chain[-1])
        self.fk_clav_chain.set_parent(self.fk_clav_ctrl[-1])
        pm.parentConstraint(self.fk_clav_ctrl[-1], self.root_grp, mo=True)
        pm.parent(self.clav_ik, self.clav_ik_ctrl)
        offset_ik_ctrl = self.ik_ctrl.getParent()
        offset_ik_ctrl.setParent(self.clav_grp)
        pm.pointConstraint(self.clav_ik_ctrl, offset_ik_ctrl, mo=True)
        offset_clav_ik_ctrl.setParent(self.clav_grp)
        self.clav_ik_chain.set_parent(self.clav_grp)
        self.arm_root = pm.createNode("transform", name=self.prefix + "_arm_root_GRP")
        transform.match(self.fk_clav_chain[0], self.arm_root)
        self.root_grp.setParent(self.arm_root)
        self.clav_grp.setParent(self.arm_root)
        self.arm_root.setParent(self.part_grp)
        transform.lock(self.clav_ik_ctrl, translate=False, rotate=False)
        transform.lock(self.fk_clav_ctrl, translate=False, rotate=False)
