from __future__ import absolute_import, division, generators, print_function
try:
    from future_builtins import *
except:
    pass
import sys
import os

sys.dont_write_bytecode = True
# ------------------------------------------------------------------------------

from maya import cmds
from maya import mel

moduleName = 'CustomWeightPainter'
label = 'CusWP'

def onMayaDroppedPythonFile(*args, **kwargs):
    _create_shelf()

def _create_shelf(*args, **kwargs):
    """Functions to create shelves.

    Function to create a shelf.
    Adds a button to the currently selected shelf.

    Args:
        None

    Returns:
        None

    """
    script_path = os.path.dirname(__file__).replace('\\', '/')

    command = """try:
    from importlib import reload
except:
    pass

import sys
from maya import cmds
if not '{0}' in sys.path:
    sys.path.append('{0}')

import {1}
reload({1})
{1}.show()""".format(script_path, moduleName)
    shelf = mel.eval("$gShelfTopLevel=$gShelfTopLevel")
    parent = cmds.tabLayout(shelf, query=True, selectTab=True)
    try:
        cmds.shelfButton(
            command=command,
            image='paintSkinWeights.png',
            annotation=moduleName,
            iol=label,
            sourceType="Python",
            parent=parent
        )
    except BaseException:
        import traceback
        print(traceback.format_exc())