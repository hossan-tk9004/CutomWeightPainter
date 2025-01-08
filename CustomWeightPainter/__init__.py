from __future__ import absolute_import, division, generators, print_function
try:
    from future_builtins import *
except:
    pass
import sys
from importlib import reload
sys.dont_write_bytecode = True
# ------------------------------------------------------------------------------
from . import ui
reload(ui)

def show(*args,**kwargs):
    """Toolの起動
    CostomWeightPainterのUIを起動する
    Args:
        None
    Returns:
        None
    """ 
    tool = ui.CustomWeightPainterUI()
    tool.showWindow()