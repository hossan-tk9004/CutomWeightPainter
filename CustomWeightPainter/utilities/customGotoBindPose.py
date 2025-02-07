# -*- coding: utf-8 -*-
"""選択状態のメッシュに対し、バインドポーズに戻します。
選択状態のメッシュに対し、バインドポーズに戻します。
Mayaの通常のBindPose機能に追加処理を施したものです。

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
import maya.api.OpenMaya as om

def safetyDone(func,*args,**kwargs):
    """エラー処理デコレータ
    エラーが発生した場合に、エラー内容を出力します。
    また、エラーが発生した場合に、アンドゥを実行します。

    Args:
        func (function): デコレートする関数
        *args: デコレートする関数の引数
        **kwargs: デコレートする関数のキーワード引数

    Returns:
        function: デコレートされた関数

    """
    def wrapper(*args,**kwargs):
        result = None
        try:
            result = func(*args,**kwargs)
        
        except Exception as e:
            om.MGlobal.displayError(e)
            cmds.undo()
        return result

    return wrapper

@safetyDone
def customGotoBindPose(*args,**kwargs):
    """選択状態のメッシュに対し、バインドポーズに戻します。
    選択状態のメッシュに対し、バインドポーズに戻します。
    対象のメッシュからスキンクラスタを検索し、インフルエンスのリストを取得します。
    そのインフルエンスリストに対し、接続をチェックし、
    接続がある場合には接続を解除し、バインドポーズに戻します。
    その後、接続を再接続します。

    無視する接続ノードリストは以下の通りです。
    ・アニメーションカーブ
    ・コンストレイント

    Args:
        None

    Returns:
        None

    """

    selection = cmds.ls(sl = True)
    if not selection:
        return

    skinClusters = []
    if cmds.objectType(selection[0]) == 'joint':
        skinClusters = cmds.listConnections(selection[0],s = False,d = True,
                                            type = 'skinCluster')
    else:
        skinClusters = [mel.eval('findRelatedSkinCluster "{}"'.format(selection[0]))]

    allJointList = []
    for skinCluster in skinClusters:
        infList = cmds.skinCluster(skinCluster,q = True,inf = True)
        infList = cmds.ls(infList,l = True)
        topNodes = [inf.split('|')[1] for inf in infList]
        topNodes = list(set(topNodes))
        allJoints = cmds.ls(topNodes,dag = True,type = 'joint',l = True)
        allJointList.extend(allJoints)

    allJointList = list(set(allJointList))
    # checkConnections

    bindPoseList = []
    ignoreJntList = []
    restoreConnectionList = []

    for jnt in allJointList:
        if jnt in ignoreJntList:
            continue
            
        checkBindPose = cmds.dagPose(jnt,q = True,bp = True)
        if not checkBindPose:
            ingoreJntList.append(jnt)
            continue
        else:
            for bindPose in checkBindPose:
                if bindPose in bindPoseList:
                    continue
                bindPoseList.append(bindPose)
            
        for attr in ['t','r','s','tx','ty','tz','rx','ry','rz','sx','sy','sz']:
            connections = cmds.listConnections('{}.{}'.format(jnt,attr),
                            s = True,d = False)
            if not connections:
                continue
            checkInput = False
            for input in connections:
                if input in cmds.ls(type = 'animCurve'):
                    continue
                elif input in cmds.ls(type = 'constraint'):
                    continue
                else:
                    checkInput = True
                    break
                    
            if checkInput:
                ignoreJntList.append(jnt)
                connectPlugs = cmds.listConnections('{}.message'.format(jnt),s = False,
                                                    d = True,type = 'dagPose',p = True)
                connectAttrs = [p for p in connectPlugs if p.split('.')[0] == checkBindPose[0]]
                restoreConnection = ['{}.message'.format(jnt),connectAttrs[0]]
                restoreConnectionList.append(restoreConnection)

                cmds.disconnectAttr('{}.message'.format(jnt),connectAttrs[0])

                break
    cmds.dagPose(bindPoseList[0],r = True,g = True)
    
    # restoreConnections
    for scs,tgt in restoreConnectionList:
        cmds.connectAttr(scs,tgt)
