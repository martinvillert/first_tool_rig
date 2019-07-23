import guide
reload(guide)
from guide import*

import dataformatting
reload(dataformatting)
from dataformatting import*

import contexts
reload(contexts)
from contexts import*

import part
reload(part)
from part import*

import system.core as system
reload(system)
from system.core import *

import parts.core as parts
reload(parts)
from parts.core import *

import bipedgen
reload(bipedgen)
from bipedgen import*

import maya.cmds as cmds

def reload_scene():
    scene_name = cmds.file(query=True, sceneName=True)
    cmds.file(scene_name, open=True, force=True)
