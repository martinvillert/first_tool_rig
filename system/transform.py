import pymel.core as pm

from .. import dataformatting

def distance_node(node_a, node_b, keep_history=True):
    node_a_loc = pm.spaceLocator(name=node_a.name() + "_distance_tracker_LOC")
    node_b_loc = pm.spaceLocator(name=node_b.name() + "_distance_tracker_LOC")
    match(node_a, node_a_loc)
    match(node_b, node_b_loc)
    dist = pm.createNode("distanceDimShape")
    pm.connectAttr(node_a_loc.worldPosition, dist.startPoint)
    pm.connectAttr(node_b_loc.worldPosition, dist.endPoint)
    if keep_history:
        return [dist, node_a_loc, node_b_loc]
    else:
        distance = dist.distance.get()
        pm.delete(node_a_loc, node_b_loc, dist.getParent())
        return distance

def which_is_more_interesting(node):
    tr = pm.xform(node, query=True, translation=True, worldSpace=True)
    rp = pm.xform(node, query=True, rotatePivot=True, worldSpace=True)
    if all([x == 0 for x in tr]):
        return rp
    else:
        return tr

def match(nodes_a, nodes_b, translate=True, rotate=True):
        """
        Matching two nodes toghther
        """
        # make sure we can iterate through nodes_b
        nodes_b = dataformatting.as_list(nodes_b)
        # get the value to move nodes to
        trans_val = which_is_more_interesting(nodes_a)
        rot_val = pm.xform(nodes_a, query=True, rotation=True, worldSpace=True)

        # iterate through nodes_b
        for node_b in nodes_b:

            # if translate and/or rotate are true, match
            if translate:
                pm.xform(node_b, translation=trans_val, worldSpace=True)

            if rotate:
                pm.xform(node_b, rotation=rot_val, worldSpace=True)


def parenting(nodes):
        """
        parent a chain
        """
        # list right using ZIP and "[1:][:-1]"
        for node_a, node_b in zip(nodes[1:], nodes[:-1]):
            node_a.setParent(node_b)


def offset(node):
        """
        Creat an offset GRP for CTRL to snap
        """
        grp = pm.createNode("transform", name=node.name()+"_offset_GRP")
        grp.setMatrix(node.getMatrix())
        node.setParent(grp)

        return grp


def lock(nodes, translate=True, rotate=True, k=False):
    """
    lock and hide attribute from channel box
    """
    axis = ['X', 'Y', 'Z']
    attrs = ['t', 'r', 's']
    nodes = dataformatting.as_list(nodes)
    if translate:
        for node in nodes:
            for axi in axis:
                pm.setAttr(node.translate+axi, lock=1, k=k)
    if rotate:
        for node in nodes:
            for axi in axis:
                pm.setAttr(node.rotate+axi, lock=1, k=k)

    scale = True
    if scale:
        for node in nodes:
            for axi in axis:
                pm.setAttr(node.scale+axi, lock=1, k=k)
            pm.setAttr(node.visibility, lock=1)