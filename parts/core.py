
import limb
reload(limb)
from limb import*

import leg
reload(leg)
from leg import*

import arm
reload(arm)
from arm import*

import spline
reload(spline)
from spline import*

import torso
reload(torso)
from torso import*

import head
reload(head)
from head import*

# import contexts
# reload(contexts)
# from contexts import*

# import system.core as system
# reload(system)
# from system.core import*

import maya.cmds as cmds


def reload_scene():
    scene_name = cmds.file(query=True, sceneName=True)
    cmds.file(scene_name, open=True, force=True)
