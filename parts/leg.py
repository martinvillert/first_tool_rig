import pymel.core as pm

from ..parts.limb import Limb
from ..system.chain import Chain
from ..system.control import Control
from ..system import transform

class Leg(Limb):
    """
    creat a legg from limb class
    """
    guide_name = "guide_biped_leg"
    default_namespace = "guide_L_biped_Leg"
    node_part = "biped_leg"
    node_side = "L"
    pv_slice = slice(0, 3)
    ankle_start_end = (2, 3)
    ball_start_end = (3, 4)
    side_colour = 6

    def define_guides(self):
        super(Leg, self).define_guides()
        self.guide_ankle_LOC = self.namespace + "end_LOC"
        self.guide_toe_LOC = self.namespace + "toe_LOC"
        self.guide_foot_LOC = self.namespace + "foot_LOC"

    def update_build_order(self):
        super(Leg, self).update_build_order()
        self.build_order.extend([
                                self.build_revers_foot,
                                ])

    def fk_foot(self):
        """
        creat a 3 FK JNT foot
        """
        self.guides = [self.guide_ankle_LOC, self.guide_foot_LOC, self.guide_toe_LOC]
        self.fk_foot_chain = Chain.make_jnt_chain(self.guides[0:3],
                                                  name_template=self.prefix + "_FK_foot_{number}_JNT")
        self.fk_foot_ctrl = Control.create_fk_ctrl(self.fk_foot_chain,
                                                   name_template=self.prefix + "_FK_foot_{number}_CTRL")
        self.fk_foot_ctrl[0].set_parent(self.fk_ctrls[-1])
        self.fk_foot_chain.set_parent(self.fk_chain[-1])

    def revers_foot(self):
        """
        creat a second JNT chain with IKH and GRPS for revers foot with CTRLS
        """
        reverse_foot_guides=(self.guide_ankle_LOC, self.guide_foot_LOC,self.guide_toe_LOC,)
        self.revers_chain = Chain.make_jnt_chain(reverse_foot_guides[0:3],
                                                 name_template=self.prefix + "_revers_foot_{number}_JNT")
        self.heel_pivot = Control.make_control(self.revers_chain[0],
                                               name=self.prefix + "heel_pivot",
                                               colour=self.side_colour)
        self.heel_pivot_offset = self.heel_pivot.getParent()

        self.offset_heel_grp = pm.group(self.heel_pivot_offset, name="offset_heel_grp")

        pm.move(-0, self.heel_pivot_offset, a=True, ws=True, moveY=True)

        self.stand_tip = Control.make_control(self.revers_chain[-1],
                                              name=self.prefix + "stand_tip",
                                              colour=self.side_colour)
        self.peel_heel = Control.make_control(self.revers_chain[-2],
                                              name=self.prefix + "peel_heel",
                                              colour=self.side_colour)
        self.toe_ik = self.revers_chain.make_ikh(start=0, end=1,
                                                 solver="ikSCsolver",
                                                 name="toe_IKH")
        self.grp_toe_ik = transform.offset(self.toe_ik)
        self.toe_tap = Control.make_control(self.revers_chain[-2],
                                            name=self.prefix + "toe_tap",
                                            colour=self.side_colour)
        self.ball_ik = self.revers_chain.make_ikh(start=1,
                                                  end=2,
                                                  solver="ikSCsolver",
                                                  name="ball_IKH")
        self.grp_ball_ik = transform.offset(self.ball_ik)
        self.grp_foot_ik = transform.offset(self.ik_handle)
        self.offset_heel_grp.setParent(self.ik_ctrl)
        self.stand_tip.set_parent(self.heel_pivot)
        self.peel_heel.set_parent(self.grp_toe_ik)
        self.toe_tap.set_parent(self.stand_tip)
        self.grp_ball_ik.setParent(self.toe_tap)
        self.grp_toe_ik.setParent(self.toe_tap)
        self.grp_foot_ik.setParent(self.peel_heel)
        self.revers_chain.set_parent(self.ik_chain[2])

    def creat_switch_chain(self):
        """
        add a switch chain to foot
        """
        self.sw_foot_chain = self.fk_foot_chain.switch_with(self.revers_chain)
        self.sw_foot_chain.set_parent(self.sw_chain[-1])
        pm.connectAttr(self.switch.switch, self.sw_foot_chain[0].switch)
        self.switch.set_parent(self.sw_foot_chain[-1])

    def parent_revers(self):
        """
        connect GRP between them to get the revers foot
        """
        pass
        # self.heel_pivot.set_parent(self.offset_heel_grp)
        # self.stand_tip.set_parent(self.heel_pivot)
        # self.peel_heel.set_parent(self.grp_toe_ik)
        # self.toe_tap.set_parent(self.stand_tip)
        # self.grp_ball_ik.setParent(self.toe_tap)
        # self.grp_toe_ik.setParent(self.toe_tap)
        # self.grp_foot_ik.setParent(self.peel_heel)
        # self.revers_chain.set_parent(self.ik_chain[2])

    def build_revers_ctrl(self):
        """
        creat attribute who allow to control the foot roll from the ik ctrl
        """
        self.ik_ctrl.addAttr("Peel_Heel", dv=0, keyable=True)
        self.ik_ctrl.addAttr("Toe_Tap", dv=0, keyable=True)
        self.ik_ctrl.addAttr("Stand_Tip", dv=0, keyable=True)
        self.ik_ctrl.addAttr("Heel", dv=0, keyable=True)

        peel_heel_offset = self.peel_heel.getParent()
        pm.connectAttr(self.ik_ctrl.Peel_Heel, peel_heel_offset.rotateX)

        toe_tap_offset = self.toe_tap.getParent()
        pm.connectAttr(self.ik_ctrl.Toe_Tap, toe_tap_offset.rotateX)

        stand_tip_offset = self.stand_tip.getParent()
        pm.connectAttr(self.ik_ctrl.Stand_Tip, stand_tip_offset.rotateX)

        pm.connectAttr(self.ik_ctrl.Heel, self.heel_pivot_offset.rotateX)

    def build_revers_foot(self):
        self.revers_foot()
        self.parent_revers()
        self.build_revers_ctrl()
        self.fk_foot()
        self.creat_switch_chain()
        transform.lock(self.fk_foot_ctrl, rotate=False)


