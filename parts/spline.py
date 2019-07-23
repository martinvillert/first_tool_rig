import pymel.core as pm

from ..part import Part
from ..system.chain import Chain
from ..system.control import Control
from ..system import transform


class Spline(Part):

    guide_name = "guide_{part}"
    guide_namespace = "guide_{side}_{part}"
    node_part = "{part}"
    node_side = "{side}"

    def define_guides(self):

        self.guide_start_LOC = self.namespace + "start_LOC"
        self.guide_end_LOC = self.namespace + "end_LOC"

    def update_build_order(self):
        super(Spline, self).update_build_order()
        self.build_order.extend([
                                self.create_chains_loc_drive,
                                ])

    def create_chains_loc_drive(self):
        """
        Create an IK spline chain, cv of curve driven by loc driven by CTRL with a following FK feature
        """
        self.guides = (self.guide_start_LOC, self.guide_end_LOC)
        self.spline_chain = Chain.make_chain_between(self.guides)
        transform.match(self.spline_chain[0], self.root_grp)
        self.spline_chain.set_parent(self.root_grp)

        ikh_spline = self.spline_chain.make_ikh(solver="ikSplineSolver", num_spans=7)
        curve = ikh_spline.inCurve.listConnections()[0]
        curve.setParent(self.meta_grp)
        self.controls = []

        for cv in curve.cv:
            loc = pm.spaceLocator()
            transform.match(cv, loc)
            pm.connectAttr(loc.worldPosition, cv)
            control = Control.make_control(loc, name=self.prefix + "_ctrl_spine_{number}_CTRL", parent=self.root_grp)
            self.controls.append(control)
            loc.setParent(control)

        self.controls[1].set_parent(self.controls[0])
        self.controls[-2].set_parent(self.controls[-1])

        self.null_chain = Chain.make_type_chain(self.spline_chain,
                                                name_template=self.prefix + "_FK_spine_{number}_transform")

        self.spine_fk_ctrl = Control.create_fk_ctrl(self.null_chain,
                                                    name_template=self.prefix + "_FK_spine_{number}_CTRL",
                                                    constrain=False,)

        for null, spine in zip(self.null_chain[0:], self.spline_chain[:-1]):
            pm.parentConstraint(spine, null)
        for null_grp, fk_ctl in zip(self.null_chain, self.spine_fk_ctrl):
            fk_grp = fk_ctl.getParent()
            pm.connectAttr(null_grp.translate, fk_grp.translate)
            pm.connectAttr(null_grp.rotate, fk_grp.rotate)
        transform.lock(self.controls, translate=False, rotate=False)
        transform.lock(self.spine_fk_ctrl, translate=False, rotate=False)
        return self.spline_chain