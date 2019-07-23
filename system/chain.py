import pymel.core as pm

import transform


class Chain(list):
    """
    As you are using this class, self refers back to the list_of_joitns passed into the __init__(...)
    """

    @classmethod
    def add_pole_vector(cls, three_joints, ik_handle):
        """
        create pole vector from a temp loc parented to start and end JNT chn and movnig it forward
        """
        name = "_".join(three_joints[0].split("_")[:2] + ["poleVector_LOC"])
        temp_locator, pole_locator = pm.spaceLocator(), pm.spaceLocator(name=name)
        pm.pointConstraint([three_joints[0], three_joints[-1]], temp_locator)
        pm.delete(pm.aimConstraint(three_joints[1], temp_locator))
        transform.match(temp_locator, pole_locator)
        pm.move(pole_locator, 5, 0, 0, r=True, os=True)
        pm.poleVectorConstraint(pole_locator, ik_handle)
        pm.delete(temp_locator)

        return pole_locator

    @classmethod
    def make_jnt_chain(cls, guides, name_template="default_{number}_JNT", orient=False, parent=None):
        """
        Creat a Jnt Chain Using Match an Freeze Function and Parenting Function
        """
        joints = []
        last_joint = None

        for number, guide in enumerate(guides, 1):
            name = name_template.format(number=str(number).zfill(3))
            joint = pm.createNode("joint", name=name)
            transform.match(guide, joint)

            if last_joint:
                joint.setParent(last_joint)

            pm.makeIdentity(joint, rotate=True, apply=True)
            joints.append(joint)

        self = Chain(joints)

        transform.parenting(self)

        if orient:
            self.orient_chain()

        if parent:
            self.set_parent(parent)

        return self

    @classmethod
    def make_type_chain(cls, guides, node_type="transform", name_template="default_{number}_JNT", orient=False):
        """
        make a chain of node (transform by default)
        """
        temp_chain = cls.make_jnt_chain(guides=guides, name_template="temp_{number}_JNT", orient=orient)
        this_chain = []
        for temp_node in temp_chain:
            this_node = pm.createNode(node_type)
            transform.match(temp_node, this_node)
            this_chain.append(this_node)
            if len(this_chain) > 1:
                this_chain[-1].setParent(this_chain[-2])
        return cls(this_chain)

    @classmethod
    def make_switch_chain(cls, ik_chain, fk_chain):
        """
        creat a chain with blend node for switching between two chain
        """
        name = "_".join(ik_chain[0].split("_")[:2] + ["sw_{number}_JNT"])
        sw_chain = cls.make_jnt_chain(ik_chain, name_template=name).list_of_joints

        sw_chain[0].addAttr("switch", min=0, max=1, dv=0, keyable=True)

        for ik_jnt, fk_jnt, sw_jnt, in zip(ik_chain, fk_chain, sw_chain):
            trans_blend = pm.createNode("blendColors")
            rotate_blend = pm.createNode("blendColors")
            scale_blend = pm.createNode("blendColors")

            pm.connectAttr(ik_jnt.translate, trans_blend.color1)
            pm.connectAttr(fk_jnt.translate, trans_blend.color2)
            pm.connectAttr(trans_blend.output, sw_jnt.translate)
            pm.connectAttr(sw_chain[0].switch, trans_blend.blender)

            pm.connectAttr(ik_jnt.rotate, rotate_blend.color1)
            pm.connectAttr(fk_jnt.rotate, rotate_blend.color2)
            pm.connectAttr(rotate_blend.output, sw_jnt.rotate)
            pm.connectAttr(sw_chain[0].switch, rotate_blend.blender)

            pm.connectAttr(ik_jnt.scale, scale_blend.color1)
            pm.connectAttr(fk_jnt.scale, scale_blend.color2)
            pm.connectAttr(scale_blend.output, sw_jnt.scale)
            pm.connectAttr(sw_chain[0].switch, scale_blend.blender)
        return Chain(sw_chain)

    @classmethod
    def make_chain_between(cls, guides):
        """
        creat a chain between two locator from a temporary chain used for lenght
        """
        guide_01 = pm.PyNode(guides[0])
        amount = pm.getAttr(guide_01.joints)
        temp_chain = Chain.make_jnt_chain(guides)
        temp_chain.orient_chain()
        distance = temp_chain.get_length()
        value = distance / (amount - 1)
        locators = []
        for number in xrange(int(amount)):
            loc = pm.spaceLocator()
            loc.setParent(temp_chain[0], relative=True)
            loc.tx.set(value * number)
            loc.setParent(world=True)
            locators.append(loc)
        temp_chain.delete()
        self = Chain.make_jnt_chain(locators)
        pm.delete(locators)
        return self

    @classmethod
    def make_chain_surface(cls, spans=10):
        count = 1
        nurbs = pm.nurbsPlane(u=1, v=spans, lr=5, n="surface")
        geo = pm.PyNode(nurbs[0])
        fols = []
        fol_shapes = []
        while count < spans:
            fol = pm.createNode('transform', n='follicle1', ss=True)
            fol_shape = pm.createNode('follicle', name="folicle_shape", p=fol, ss=True)
            pm.connectAttr(geo.local, fol_shape.inputSurface)
            pm.connectAttr(geo.worldMatrix[0], fol_shape.inputWorldMatrix)
            pm.connectAttr(fol_shape.outRotate, fol.rotate)
            pm.connectAttr(fol_shape.outTranslate, fol.translate)
            fol.inheritsTransform.set(False)
            fol_shape.parameterU.set(0.5)
            fol_shape.parameterV.set(0.1*count)
            fols.append(fol)
            fol_shapes.append(fol_shapes)
            count += 1

        nurbs_jnts = Chain.make_jnt_chain(fols, name_template="_surface_{number}_JNT")
        for nurbs_JNT, fol in zip(nurbs_jnts[0:], fols[:-1]):
            nurbs_JNT.setParent(fol)

        drivers = []
        driver_a_jnt = pm.duplicate(nurbs_jnts[0], name="driver_A")
        driver_b_jnt = pm.duplicate(nurbs_jnts[(spans/2)-1], name="driver_B")
        driver_c_jnt = pm.duplicate(nurbs_jnts[-1], name="driver_C")
        drivers.append(driver_a_jnt)
        drivers.append(driver_b_jnt)
        drivers.append(driver_c_jnt)
        pm.parent(drivers, w=True)
        for driver in drivers:
            pm.setAttr(driver[0]+".radius", 1.5)
        pm.bindSkin(nurbs, drivers)

    def __init__(self, list_of_joints):
        self.list_of_joints = list_of_joints

        super(Chain, self).__init__(self.list_of_joints)

        # super

    def duplicate(self, name_template=None):
        return self.make_jnt_chain(self, name_template=name_template)

    def orient_chain(self):
        """
        aim parent to get right orientation of Locs
        """

        pm.parent(*self, world=True)
        constraints = []
        for node_a, node_b in zip(self[1:], self[:-1]):

            # ainConstrain with UP orientation after node_a list
            cnst = pm.aimConstraint(node_a,
                                    node_b,
                                    worldUpObject=node_a,
                                    worldUpType="objectrotation",
                                    worldUpVector=(0, 1, 0))
            constraints.append(cnst)

        cnst = pm.orientConstraint(self[-2], self.list_of_joints[-1])
        constraints.append(cnst)

        pm.delete(constraints)

        pm.makeIdentity(self, rotate=True, apply=True)

        transform.parenting(self)

    def make_ikh(self, solver="ikRPsolver", start=0, end=-1, name=None, num_spans=5):
        """
        makes IKH
        """
        ending = "solver_IKH"
        if name:
            ending = name

        name = "_".join(self[0].split("_")[:2] + [ending])

        kwargs = {"solver": solver, "startJoint": self[start], "endEffector": self[end], "name": name}

        if solver == "ikSplineSolver":
            kwargs.update({"numSpans": num_spans-3})

        ikh = pm.ikHandle(**kwargs)
        handle = ikh[0]
        return handle

    def switch_with(self, another_chain):
        return self.make_switch_chain(self, another_chain.list_of_joints)

    def set_parent(self, other_node):
        self[0].setParent(other_node)

    def add_stretch(self, control):
        """
        creat stretch from distance node using a clamp to keep the limbe Shape and allow to control stretch strenght
        """
        dist, node_a_loc, node_b_loc = transform.distance_node(self[0], control)
        mv = pm.createNode("multiplyDivide")
        mv.operation.set(2)
        clmp = pm.createNode("clamp")
        pm.connectAttr(dist.distance, mv.input1X)
        pm.connectAttr(mv.outputX, clmp.inputR)
        mv.input2X.set(dist.distance.get())

        for joint in self:
            pm.connectAttr(clmp.outputR, joint.scaleX)

        control.addAttr("Stretch", dv=1, keyable=True)
        control.addAttr("Squash", dv=1, keyable=True)
        pm.connectAttr(control.Stretch, clmp.maxR)
        pm.connectAttr(control.Squash, clmp.minR)
        pm.pointConstraint(self[0], node_a_loc)
        pm.pointConstraint(control, node_b_loc)
        return dist

    def get_length(self):
        return sum([joint.tx.get() for joint in self[1:]])

    def delete(self):
        pm.delete(self)
