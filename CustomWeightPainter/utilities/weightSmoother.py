# -*- coding: utf-8 -*-
"""髪の毛のウエイトをスムースする便利機能
対象のメッシュに対し、ウエイトのスムースをかけます。

Attributes:
    * None
Todo:
    * None
"""
from __future__ import absolute_import, division, generators, print_function
try:
    from future_builtins import *
except:
    pass
import sys
sys.dont_write_bytecode = True
# ------------------------------------------------------------------------------
import maya.cmds as cmds
import maya.mel as mel

def floodSelection(value=0, op="smooth",targetInflence = False):
    """ウエイト情報を指定の設定で上書きします。
    元のソースコードは以下より引用しました。
    https://gist.github.com/benmorgantd/019ed6000982b11392b529870422f0a3

    上記に手を加えた点として、ターゲットのインフルエンスを指定できるようにしたことです。

    Args:
        value (int): 上書きする値
        op (str): 上書きするオペレーション
        targetInflence (str): 上書きするインフルエンス
    
    Returns:
        None
    """
    if len(cmds.ls(sl=1)) == 0:
        return

    # if we're not currently in the paint skin weights tool context, get us into it
    if cmds.currentCtx() != "artAttrSkinContext":
        mel.eval("ArtPaintSkinWeightsTool;")
        
    # set targetInflence
    if targetInflence:
        preInf = cmds.artAttrSkinPaintCtx(cmds.currentCtx(),q = True,inf=True)
        mel.eval('artSkinInflListChanging "{}" 0;'.format(preInf))
        mel.eval('artSkinInflListChanging "{}" 1;'.format(targetInflence))
        mel.eval('artSkinInflListChanged artAttrSkinPaintCtx;')
        
    # first get the current settings so that the user doesn't have to switch back
    currOp = cmds.artAttrSkinPaintCtx(cmds.currentCtx(), q=1, selectedattroper=1)
    currValue = cmds.artAttrSkinPaintCtx(cmds.currentCtx(), q=1, value=1)

    # flood the current selection to zero

    # first set our tool to the selected operation
    cmds.artAttrSkinPaintCtx(cmds.currentCtx(), e=1, selectedattroper=op)
    # change the tool value to the selected value
    cmds.artAttrSkinPaintCtx(cmds.currentCtx(), e=1, value=value)
    # flood the tool
    cmds.artAttrSkinPaintCtx(cmds.currentCtx(), e=1, clear=1)

    # set the tools back to the way you found them
    cmds.artAttrSkinPaintCtx(cmds.currentCtx(), e=1, selectedattroper=currOp)
    cmds.artAttrSkinPaintCtx(cmds.currentCtx(), e=1, value=currValue)


def smoothWeight(targetMesh = '',repeat = 10,*args,**kwargs):
    """選択状態のメッシュに対し、ウエイトのスムースをかけます。
    選択状態のメッシュに対し、repeatの回数分ウエイトのスムースをかけます。
    targetMeshからSkinClusterを検索し、インフルエンスのリストを取得します。
    そのインフルエンスリストに対し、階層順を見てスムースします。
    基本的に、直接の親と子の間でスムースさせます。
    ただし、対象になりうるインフルエンスにロックがかかっていた場合には、スキップします。
    また、対象になりうるインフルエンスの親がロックされていた場合にもスキップします。

    Args:
        targetMesh (str): 対象のメッシュ
        repeat (int): スムースの繰り返し回数

    Returns:
        None

    """

    currentCtx = cmds.currentCtx()
    skinCluster = mel.eval('findRelatedSkinCluster "{}";'.format(targetMesh))
    inflenceList = cmds.skinCluster(skinCluster,q = True,inf = True)
    
    ingoreInfList = []
    unlockInfList = []
    for inf in inflenceList:
        if cmds.getAttr('{}.liw'.format(inf)):
            ingoreInfList.append(inf)
        else:
            unlockInfList.append(inf)
            cmds.setAttr('{}.liw'.format(inf),True)
    # print(ingoreInfList)
    
    
    for indx,inf in enumerate(inflenceList):
        if inf in ingoreInfList:
             continue
        parentInf = cmds.listRelatives(inf,p=True)
        
        if parentInf in ingoreInfList:
            continue
            
        preInf = inflenceList[indx-1]
        if indx == 0:
            continue
        elif not preInf in parentInf:
            continue
        preInf = inflenceList[indx-1]
        cmds.setAttr('{}.liw'.format(inf),False)
        cmds.setAttr('{}.liw'.format(preInf),False)
        # print(inf,preInf)
        for cnt in range(repeat):
            nw = cmds.skinCluster(skinCluster, q=True, nw=True)
            cmds.skinCluster(skinCluster, e=True, fnw=True, nw=2)
            floodSelection(value = 1,targetInflence = inf)
            cmds.skinCluster(skinCluster, e=True, fnw=True, nw=nw)
        
        cmds.setAttr('{}.liw'.format(inf),True)
        cmds.setAttr('{}.liw'.format(preInf),True)
    
    for inf in unlockInfList:
        cmds.setAttr('{}.liw'.format(inf),False)
        
    # ツールを元に戻す
    cmds.setToolTo(currentCtx)

def SmoothWeightSelection(repeat = 2,*args,**kwargs):
    """選択状態のメッシュに対し、ウエイトのスムースをかけます。
    選択状態のメッシュに対し、repeatの回数分ウエイトのスムースをかけます。
    もしも頂点が選択されていた場合は、頂点のみを対象にします。
    Args:
        repeat (int): スムースの繰り返し回数

    Returns:
        None

    """
    selection = cmds.ls(sl = True)
    nodeList = []
    if 'vtx[' in selection[0].split('.')[-1]:
        nodeList = [vtx.split('.')[0] for vtx in selection]
        nodeList = list(set(nodeList))
    else:
        nodeList = selection
        
    for node in nodeList:
        # print(node)
        smoothWeight(node,repeat)