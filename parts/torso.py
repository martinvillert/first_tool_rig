import pymel.core as pm

from ..parts.spline import Spline
from ..system.chain import Chain
from ..system.control import Control
from ..system import transform


class Torso(Spline):

    guide_name = "guide_biped_torso"
    default_namespace = "guide_C_biped_Torso"
    mirror = False
    node_part = "torso"
    node_side = "C"

    def define_guides(self):

        self.guide_end_LOC = self.namespace + "chest_LOC"
        self.guide_start_LOC = self.namespace + "hips_LOC"


    def update_build_order(self):
        super(Torso, self).update_build_order()
        self.build_order.extend([self.upper_part,])

    def upper_part(self):
        """
        creat a torso from an ik spline chain
        """
        self.chain_torso = Chain.make_jnt_chain(self.controls[-3:-1],
                                                name_template=self.prefix + "_IK_top_spine_{number}_JNT",
                                                parent=self.spline_chain[-1])
        transform.match(self.controls[-1], self.chain_torso[0])
        pm.pointConstraint(self.spline_chain[-1], self.chain_torso[0])
        pm.orientConstraint(self.controls[-1], self.chain_torso[0])

        self.main_ctrl = Control.make_control(self.controls[0],
                                              name=self.prefix + "main_ctrl_spine_{number}_CTRL",
                                              parent=self.root_grp)
        pm.move(self.main_ctrl.getShape().cv, 1, 0, 0, relative=True)
        [ctl.set_parent(self.main_ctrl) for ctl in self.controls[::1]]

        self.fk_spline_chain = self.spline_chain.duplicate(name_template=self.prefix + "_FK_torso_{number}_JNT")
        self.fk_spline_chain.set_parent(self.root_grp)

        for jnt_torso, fk_ctrl in zip(self.fk_spline_chain, self.spine_fk_ctrl):
            pm.parentConstraint(fk_ctrl, jnt_torso)

        pm.connectAttr(self.root_grp.scale, self.null_chain[0].scale)
        pm.connectAttr(self.root_grp.scale, self.spine_fk_ctrl[0].getParent().scale)


