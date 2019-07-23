import pymel.core as pm

from . import transform

class Control(object):

    @classmethod
    def make_control(cls, at_node, name, colour=17, parent=None, shape="sixth"):
        """"
        Creat Ctrl After a List or Selection
        Created In Maya Script Editor
        """

        kwargs = {"degree": 3, "sections": 8}  # this makes a circle

        if shape == "square":
            kwargs = {"degree": 1, "sections": 4}
        elif shape == "triangle":
            kwargs = {"degree": 1, "sections": 3}
        elif shape == "circle":
            kwargs = {"degree": 3, "sections": 8}
        elif shape == "sixth":
            kwargs = {"degree": 1, "sections": 6}

        ctrl = pm.circle(name=name, **kwargs)[0]
        if at_node:
            transform.match(at_node, ctrl)
            transform.offset(ctrl)
        ctrl.rotateOrder.set(k=True)

        ctrl.overrideEnabled.set(True)
        ctrl.overrideColor.set(colour)

        self = cls(ctrl)

        if parent:
            self.set_parent(parent)

        return self

    @classmethod
    def create_fk_ctrl(cls, chain, name_template, constrain=True, colour=17):
        """
        Creat Fk Ctrl Using Name Gen Function
        """
        controls = []
        last_control = None

        for number, node in enumerate(chain[:-1], 1):

            name = name_template.format(number=str(number).zfill(2))
            ctrl = cls.make_control(at_node=node, name=name, colour=colour, shape="circle")
            controls.append(ctrl)

            if last_control:
                ctrl.set_parent(last_control)

            if constrain:
                pm.parentConstraint(ctrl, node)

            last_control = ctrl
        return controls

    def __init__(self, control_node):
        self.control_node = control_node
        self.__melobject__ = self.control_node.__melobject__

    def __repr__(self):
        return str(self.control_node.name())

    def __str__(self):
        return str(self.control_node.name())

    def __getattr__(self, item):
        if hasattr(self.control_node, item):
            return getattr(self.control_node, item)
        else:
            raise Exception("Attribute {0} does not exist on control class".format(item))

    def __hash__(self):
        return hash(self.control_node)

    def __unicode__(self):
        return unicode(self.control_node.name())

    def set_parent(self, other_node):
        self.getParent().setParent(other_node)

