import pymel.core as pm


class HideShapes(object):

    shapes_to_hide = ["locator", "ikHandle", "distanceDimShape"]

    def __enter__(self):
        self.node_tracker = pm.NodeTracker()
        self.node_tracker.startTrack()

    def __exit__(self, one, two, three):
        self.node_tracker.endTrack()
        self.nodes = self.node_tracker.getNodes()
        locators = [x for x in self.nodes if x.type() in self.shapes_to_hide]

        for node in locators:
            if hasattr(node, "visibility"):
                node.visibility.set(False)


class ParentLooseNodes(object):

    def __init__(self, parent_node):
        self.parent_node = parent_node

    def __enter__(self):
        self.node_tracker = pm.NodeTracker()
        self.node_tracker.startTrack()

    def __exit__(self, one, two, three):
        self.node_tracker.endTrack()
        self.nodes = self.node_tracker.getNodes()
        without_parent = []
        for node in self.nodes:
            if hasattr(node, "getParent"):
                if not node.getParent():
                    without_parent.append(node)

        pm.parent(without_parent, self.parent_node)


