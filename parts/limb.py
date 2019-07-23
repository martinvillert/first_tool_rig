import pymel.core as pm

from ..part import Part
from ..system.chain import Chain
from ..system.control import Control
from ..system import transform


class Limb(Part):
    """
    creat a tri JNT chain from locators with IK / FK switch, stretch and squash, and switch
    base for arms and leggs
    """
    limb_slice = slice(0, 3)
    pv_slice = slice(1, 3)
    ctrl_ik_pos = 0
    lim_range = (0, 2)
    guide_name = "guide_{part}"
    guide_namespace = "guide_{side}_{part}"
    node_part = "{part}"
    node_side = "{side}"

    def define_guides(self):
        self.guide_start_LOC = self.namespace + "start_LOC"
        self.guide_mid_LOC = self.namespace + "mid_LOC"
        self.guide_end_LOC = self.namespace + "end_LOC"

    def update_build_order(self):
        super(Limb, self).update_build_order()
        self.build_order.extend([self.build_joint_chains,
                                 self.build_controls,
                                 self.do_parenting])

    def build_joint_chains(self):
        """
        creat a limb IK FK and switch chain with pole vector
        """
        # joint chains
        self.guides = (self.guide_start_LOC, self.guide_mid_LOC, self.guide_end_LOC)
        self.fk_chain = Chain.make_jnt_chain(self.guides[0:3],
                                             name_template=self.prefix + "Fk_{number}_JNT",
                                             orient=True)
        transform.match(self.fk_chain[0], self.root_grp)
        self.ik_chain = self.fk_chain.duplicate(name_template=self.prefix + "Ik_{number}_JNT")
        self.sw_chain = self.fk_chain.switch_with(self.ik_chain)
        self.ik_handle = self.ik_chain.make_ikh(start=0, end=2, solver="ikRPsolver")
        self.pole_locator = self.ik_chain.add_pole_vector(self.ik_chain[self.pv_slice], self.ik_handle)

    def build_controls(self):
        """
        creat limb ctrls, nodes and connection for switch IK/FK
        """
        self.fk_ctrls = Control.create_fk_ctrl(self.fk_chain,
                                               name_template=self.prefix + "Fk_{number}_CTL",)
        self.ik_ctrl = Control.make_control(self.ik_chain[-1],
                                            name=self.prefix + "Ik_01_CTL",
                                            colour=self.side_colour)
        self.pv_ctrl = Control.make_control(self.pole_locator,
                                            name=self.prefix + "PoleVector_01_CTL",
                                            colour=self.side_colour)
        self.switch = Control.make_control(self.guides[-1],
                                           name=self.prefix + "_switch_{number}_CTRL",
                                           colour=self.side_colour, shape="triangle")
        self.switch.translateZ.set(1)
        self.switch.addAttr("switch", dv=0, keyable=True, min=0, max=1)
        pm.connectAttr(self.switch.switch, self.sw_chain[0].switch)
        self.condition_a = pm.createNode("condition")
        self.condition_b = pm.createNode("condition")
        self.condition_a.colorIfTrueR.set(0)
        self.condition_a.colorIfFalseR.set(1)
        self.condition_b.colorIfTrueR.set(1)
        self.condition_b.colorIfFalseR.set(0)
        pm.connectAttr(self.switch.switch, self.condition_a.firstTerm)
        pm.connectAttr(self.switch.switch, self.condition_b.firstTerm)
        pm.connectAttr(self.condition_a.outColorR, self.fk_ctrls[0].visibility)
        pm.connectAttr(self.condition_b.outColorR, self.ik_ctrl.visibility)
        self.stretch = self.ik_chain.add_stretch(self.ik_ctrl)

    def do_parenting(self):
        """
        parent limb chain with Limb CTRL
        """
        self.ik_handle.setParent(self.ik_ctrl)
        self.pole_locator.setParent(self.pv_ctrl)
        self.fk_ctrls[0].set_parent(self.root_grp)
        self.ik_ctrl.set_parent(self.root_grp)
        self.ik_chain.set_parent(self.root_grp)
        self.fk_chain.set_parent(self.root_grp)
        self.sw_chain.set_parent(self.root_grp)
        self.pv_ctrl.set_parent(self.root_grp)
        self.switch.set_parent(self.sw_chain[-1])
        transform.lock(self.fk_ctrls, rotate=False)
        transform.lock(self.ik_ctrl, translate=False, rotate=False)
        transform.lock(self.switch)