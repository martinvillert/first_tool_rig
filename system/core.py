import transform
reload(transform)
from transform import*

import control
reload(control)
from control import*

import chain
reload(chain)
from chain import*

import deformer
reload(deformer)
from deformer import*

import cluster
reload(cluster)
from deformer import*

import lattice
reload(lattice)
from lattice import*

import blendshape
reload(blendshape)
from blendshape import*

import deformerstack
reload(deformerstack)
from deformerstack import*

import nonlinear
reload(nonlinear)
from nonlinear import*

import maya.cmds as cmds


def reload_scene():
    scene_name = cmds.file(query=True, sceneName=True)
    cmds.file(scene_name, open=True, force=True)
