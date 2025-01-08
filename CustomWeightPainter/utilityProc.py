# -*- coding: utf-8 -*-
"""Utility Procを集めたモジュール
ウエイトペイント作業においてあったら便利なスクリプトをまとめたモジュールです。

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
import traceback
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om

# wrapper
def AvoidAutoKey(func):
    """autoKeyを回避して指定の関数を実行するためのデコレーター
    処理前にautoKeyFrameの状態を取得し、autoKeyを解除、
    関数を実行したのちに元に戻します。

    Args:
        func (function): デコレータをかける関数

    Returns:
        function: デコレータをかけた関数
    """

    def wrapper(*args,**kwargs):
        autoKeyState = cmds.autoKeyframe(q = True,state = True)
        cmds.autoKeyframe(state = False)
        try:
            func(*args,**kwargs)
        except:
            om.MGlobal.displayError(traceback.format_exc())
        cmds.autoKeyframe(state = autoKeyState)
    return wrapper

# ------------------------------------------------------------------------------
# utility Procs
@AvoidAutoKey
def gotoBindPose(*args,**kwargs):
    """バインドポーズに戻す
    Goto BindPoseを実行します。
    ※今後拡張可能なように、pythonでラップした関数にしました。

    Args:
        None

    Returns:
        None

    """
    mel.eval('GoToBindPose')

# Pose action
@AvoidAutoKey
def poseAction(targetNode,axis = 'x',preValues=[0.0,0.0,0.0],actionType='hold',*args,**kwargs):
    """指定のノードに対してポーズアクションを実行する
    指定のノードに対してポーズアクションを実行します。
    
    actionType = hold: 何もしない
    actionType = revert: 元の値に戻す
    actionType = zero: 0にする

    Args:
        targetNode (str): ポーズアクションを実行するノード
        axis (str): ポーズアクションを実行する軸
        preValues (list): ポーズアクションを実行する前の値
        actionType (str): ポーズアクションの種類

    Returns:
        None

    """
    if not actionType:
        return
    elif actionType == 'hold':
        pass
    elif actionType == 'revert':
        preValue = preValues[0]
        if axis == 'x':
            preValue = preValues[0]
        elif axis == 'y':
            preValue = preValues[1]
        elif axis == 'z':
            preValue = preValues[2]

        cmds.setAttr('{}.r{}'.format(targetNode,axis),preValue)

    elif actionType == 'zero':
        cmds.setAttr('{}.r{}'.format(targetNode,axis),0.0)

# select action
def convertSelectionToObj(*args,**kwargs):
    """選択状態をオブジェクト選択モードに戻す。
    選択状態をオブジェクト選択モードに戻します。
    頂点選択状態を解除する際に便利です。

    Args:
        None
        
    Returns:
        None
        
    """
    selection = cmds.ls(sl = True)
    if not selection:
        return
    
    selObj = []
    for sel in selection:
        selObj.append(sel.split('.')[0])

    selObj = list(set(selObj))
    if not selObj:
        return
    cmds.select(selObj)

def createQuickSelectionSet(*args,**kwargs):
    """クイックセレクションセットを作成する
    クイックセレクションセットを作成します。

    Args:
        None

    Returns:
        None

    """
    selection = cmds.ls(sl = True)
    if not selection:
        return
    mel.eval('CreateQuickSelectSet;')

# animation action
def setKeyToTargetInflence(targetInflence,*args,**kwargs):
    """指定のインフルエンスにキーフレームを打つ
    指定のインフルエンスにキーフレームを打ちます。
    3軸一斉にキーフレームを打ちたい場合に便利です。

    Args:
        targetInflence (str): キーフレームを打つインフルエンス

    Returns:
        None

    """
    if not cmds.objExists(targetInflence):
        return
    
    cmds.setKeyframe(targetInflence,at = 'rx')
    cmds.setKeyframe(targetInflence,at = 'ry')
    cmds.setKeyframe(targetInflence,at = 'rz')

def cutKeyTotargetInflence(targetInflences,*args,**kwargs):
    """指定のインフルエンスのキーフレームを削除する
    指定のインフルエンスのキーフレームを削除します。

    Args:
        targetInflence (str): キーフレームを削除するインフルエンス

    Returns:
        None

    """
    
    cmds.cutKey(targetInflences,at = 'rx')
    cmds.cutKey(targetInflences,at = 'ry')
    cmds.cutKey(targetInflences,at = 'rz')

def cutKeyInflenceLock(targetInflences,*args,**kwargs):
    """指定のインフルエンスのinflenceLockのキーを削除する。
    指定のインフルエンスのinflenceLockのキーを削除し、アンロックします。
    誤ってinflenceLockにキーが振られているケースで便利です。

    Args:
        targetInflences(list): キーフレームを削除するインフルエンス

    Returns:
        None

    """
    cmds.cutKey(targetInflences,at = 'liw')
    for node in targetInflences:
        cmds.setAttr('{}.liw'.format(node),False)