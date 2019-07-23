import pymel.core as pm

import contexts
import guide

class Part(object):
    guide_name = "DEFAULT_GUIDE"
    default_namespace = "DEFAULT_PART_NAMESPACE"
    mirror = False
    side_colour = 17

    def __init__(self, side, description, namespace=None):
        self.namespace = namespace if namespace else self.default_namespace

        if not self.namespace.endswith(":"):
            self.namespace += ":"

        self.prefix = "{side}_{description}".format(side=side, description=description)
        self.part_grp, self.root_grp, self.meta_grp = None, None, None
        self.build_order = []
        self.update_build_order()

        if side == "L":
            self.side_colour = 6

        elif side == "R":
            self.side_colour = 12

    def update_build_order(self):
        pass

    def build(self):
        """
        pass Context for hidding unwanted nodes and placing unparented nodes in meta GRP
        """
        self.build_structure()
        with contexts.ParentLooseNodes(parent_node=self.meta_grp):
            with contexts.HideShapes():
                for method in self.build_order:
                    method()
        # [pm.PyNode(locator).visibility.set(False) for locator in self.guide_locators]

    def build_structure(self):
        """
        creat and parent grp for structure
        """
        self.part_grp = pm.createNode("transform", name=self.prefix + "_part_GRP")
        self.root_grp = pm.createNode("transform", name=self.prefix + "_root_GRP")
        self.meta_grp = pm.createNode("transform", name=self.prefix + "_meta_GRP")
        pm.parent([self.root_grp, self.meta_grp], self.part_grp)

    def define_guides(self):
        raise Exception("Define guides has not been overloaded")

    @classmethod
    def fetch_guide(cls, namespace=None):
        if namespace is None:
            namespace = cls.default_namespace

        guide.Guides.fetch_guide(cls.guide_name, namespace=namespace)

    @classmethod
    def edit_guide(cls):
        guide.Guides.edit_guide(cls.guide_name)


    @classmethod
    def build_from_namespace(cls, namespace, side, description):
        self = cls(side=side, description=description, namespace=namespace)
        self.define_guides()
        self.build()

    @classmethod
    def build_from_selection(cls, side, description):
        selection = pm.ls(sl=True)[-1]
        namespace = selection.namespace()[:-1]
        self = cls(side=side, description=description, namespace=namespace)
        self.define_guides()
        self.build()










