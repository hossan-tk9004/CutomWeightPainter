# -*- coding: utf-8 -*-
"""CustomWeightPainterのUI関連の処理をまとめたモジュール

Attributes:
    None

Todo:
    ・ジョイントの回転コントロールをもう少し使いやすくする
    ・inflenceLockにキーふぁふられている場合、inflenceリストの南京錠マークを赤くする（したい）
"""
from __future__ import absolute_import, division, generators, print_function
try:
    from future_builtins import *
except:
    pass
import sys
from importlib import reload
sys.dont_write_bytecode = True
# ------------------------------------------------------------------------------
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
from maya.common.ui import LayoutManager

from . import utilityProc
reload(utilityProc)

def createScriptJob(func,event,parentUi,*args,**kwargs):
    """スクリプトジョブを作成する。
    指定された関数をスクリプトジョブとして登録します。
    任意のイベントと、ペアレントするUIを指定することができます。

    Args:
        func (function): 実行する関数
        event (str): イベント
        parentUi (str): ペアレントするUI

    Returns:
        scriptJob (int): 作成されたスクリプトジョブの番号

    """
    scriptJob = cmds.scriptJob(e = [event,func],p=parentUi)
    return scriptJob

def isJapaneseLanguage(*args,**kwargs):
    """Mayaが日本語の言語設定かどうかを判定する
    現在のMayaの言語設定が日本語かどうかを判定します。

    Args:
        None

    Returns:
        bool: 日本語の場合はTrue、それ以外はFalse

    """
    if cmds.about(uiLanguage=True) == 'ja_JP':
        return True
    else:
        return False

class poseActionStateObj(object):
    """ポーズアクションの状態を保持するクラス
    CutomWitghtPainterで対象のインフルエンスジョイントを回転させた後の
    アクションを指定するためのオブジェクト。

    Attributes:
        hold (bool): ポーズアクションを保持するか
        revert (bool): ポーズアクションを元に戻すか
        zero (bool): ポーズアクションをゼロにするか
    """
    hold = True
    revert = False
    zero = False

    def __init__(self,*args,**kwargs):
        pass

    def printValues(self,*args,**kwargs):
        """保持している値を表示する
        """
        print(self.hold,self.revert,self.zero)


class CustomWeightPainterUI(object):
    """CustomWeightPainterのUIを管理するクラス
    このクラスはCustomWeightPainterのUIを管理するためのクラスです。
    MayaのtoolPropertyWindowをウエイトペイントモードToolと一緒に立ちあげて、
    カスタムUIを仕込みます。

    Attributes:
        customUi (str): カスタムUIの名前
        toolName (str): ウエイトペイントモードToolの名前
        attrControlX (str): infulenceのX軸の回転用attrFieldSliderGrpの名前
        attrControlY (str): infulenceのY軸の回転用attrFieldSliderGrpの名前
        attrControlZ (str): infulenceのZ軸の回転用attrFieldSliderGrpの名前
        poseActionState (poseActionStateObj): ポーズアクションの状態を保持するオブジェクト
        targetInflence (str): 対象のインフルエンスジョイント
        preValues (list): 回転前の値

    """

    poseActionState = poseActionStateObj()
    
    preValues = [0.0,0.0,0.0]
    
    def __init__(self):
        self.customUi = 'CustomWeightPainterUI_UserControl'
        self.toolName = False
        pass
    
    def errorPrint(self,errorType = 0,*args,**kwargs):
        """エラーメッセージを表示する
        エラータイプに応じたエラーメッセージを表示します。
        0: Toolの動作が正常でない可能性があります。
        1: カスタムコマンドの格納に失敗しました。
        2: カスタムコマンドの実行に失敗しました。
        3: 対象のジョイントの取得に失敗しました。
        Args:
            errorType (int): エラータイプ

        Returns:
            None
        
        """
        if errorType == 0:
            om.MGlobal.displayWarning('Toolの動作が正常でない可能性があります。')
        elif errorType == 1:
            om.MGlobal.displayWarning('カスタムコマンドの格納に失敗しました。\nToolの動作が正常でない可能性があります。')
        elif errorType == 2:
            om.MGlobal.displayWarning('カスタムコマンドの実行に失敗しました。\nToolの動作が正常でない可能性があります。')
        elif errorType == 3:
            om.MGlobal.displayWarning('対象のジョイントの取得に失敗しました。\nToolの動作が正常でない可能性があります。')
        elif errorType == 4:
            om.MGlobal.displayWarning('カスタムUIの格納に失敗しました。\nToolの動作が正常でない可能性があります。')

    def showWindow(self,*args,**kwargs):
        """ウィンドウを表示する
        ウィンドウを表示します。

        Args:
            None

        Returns:
            None
        """
        self.toolName = mel.eval('artAttrSkinToolScript 3')
        self.attrControlX = None
        self.attrControlY = None
        self.attrControlZ = None
        cmds.evalDeferred(self.createUI)
        cmds.evalDeferred(self.setCustomArtSkinInflListChanged)
        cmds.evalDeferred(self.setTargetJoint)

    # button action
    def poseAction(self,axis='x',*args,**kwargs):
        """ポーズアクションを実行する
        weightPaintToolで選択されているインフルエンスジョイントに対して、
        指定のポーズアクションを実行します。

        Args:
            axis (str): 回転軸

        Returns:
            None
        """
        actionType = False
        if self.poseActionState.hold:
            actionType = 'hold'
        elif self.poseActionState.revert:
            actionType = 'revert'
        elif self.poseActionState.zero:
            actionType = 'zero'

        utilityProc.poseAction(targetNode = self.targetInflence,
                                axis = axis,
                                preValues = self.preValues,
                                actionType = actionType)
    
    def cutKeyInflenceLock(self,all = False,*args,**kwargs):
        """キーをカットする
        インフルエンスのロックを解除してキーをカットします。

        Args:
            all (bool): 全てのインフルエンスのキーをカットするか

        Returns:
            None
        """
        if all:
            skinClusters = cmds.artAttrSkinPaintCtx(self.toolName,q = True,pna = True).split(' ')
            targetIngluences = []
            for skinCluster in skinClusters:
                if cmds.objectType(skinCluster) != 'skinCluster':
                    continue
                influences = cmds.skinCluster(skinCluster,q = True,inf = True)
                targetIngluences.extend(influences)
            influences = list(set(targetIngluences))
            utilityProc.cutKeyInflenceLock(targetIngluences)
        else:
            utilityProc.cutKeyInflenceLock(targetInflence = [self.targetInflence])
        
        # UIを更新
        cmds.evalDeferred(self.showWindow)

    # for ui process
    def deleteUserControl(self,*args,**kwargs):
        """カスタムUIを削除する
        カスタムUIを削除します。

        Args:
            None

        Returns:
            None
        """
        if cmds.paneLayout(self.customUi,ex = True):
            cmds.deleteUI(self.customUi)

    def createCostomUi(self,parent,*args,**kwargs):
        """カスタムUIを作成する
        カスタムUIを作成します。

        Args:
            parent (str): 親UI

        Returns:
            customUi (str): カスタムUIの名前
        """
        selection = cmds.ls(sl = True)
        tmpNode = cmds.createNode('transform')
        with LayoutManager(cmds.paneLayout(self.customUi,configuration='vertical2',ps = (1,20,100),p = parent)) as pane:
            with LayoutManager(cmds.columnLayout(adj = True,p = self.customUi,w = 200)) as col2:
                cmds.separator()

                cmds.text(l = 'Pose action',al = 'left')
                cmds.rowLayout(nc = 3,p = col2)
                cmds.radioCollection()
                cmds.radioButton(l = 'Hold',sl = self.poseActionState.hold,
                                onc = lambda *args:setattr(self.poseActionState,'hold',True),
                                ofc = lambda *args:setattr(self.poseActionState,'hold',False))
                cmds.radioButton(l = 'Revert',sl = self.poseActionState.revert,
                                onc = lambda *args:setattr(self.poseActionState,'revert',True),
                                ofc = lambda *args:setattr(self.poseActionState,'revert',False))
                cmds.radioButton(l = 'Go to Zero',sl = self.poseActionState.zero,
                                onc = lambda *args:setattr(self.poseActionState,'zero',True),
                                ofc = lambda *args:setattr(self.poseActionState,'zero',False))
                cmds.setParent('..')

                cmds.text(l = 'Rotate inflence',al = 'left')
                self.attrControlX = cmds.attrFieldSliderGrp( min=-180, max=180,
                                                            cw = [(1,60),(2,50)],
                                                            p=col2,
                                                            cat = (1,'left',10),
                                                            cc=lambda *args:self.poseAction(axis='x'),
                                                            at='{}.rx'.format(tmpNode))
                self.attrControlY = cmds.attrFieldSliderGrp( min=-180, max=180,
                                                            cw = [(1,60),(2,50)],
                                                            p=col2,
                                                            cat = (1,'left',10),
                                                            cc=lambda *args:self.poseAction(axis='y'),
                                                            at='{}.ry'.format(tmpNode))
                self.attrControlZ = cmds.attrFieldSliderGrp( min=-180, max=180,
                                                            cw = [(1,60),(2,50)],
                                                            p=col2,
                                                            cat = (1,'left',10),
                                                            cc=lambda *args:self.poseAction(axis='z'),
                                                            at='{}.rz'.format(tmpNode))
                
            with LayoutManager(cmds.columnLayout(adj = True,p = pane)) as col1:
                cmds.separator()

                cmds.text(l = 'Utility',al = 'left')
                cmds.rowColumnLayout(nc = 5,p = col1)
                cmds.shelfButton(style='iconAndTextVertical',
                                label='GotoBP',ndp = True,
                                image1='goToBindPose.png',
                                c = utilityProc.gotoBindPose)
                cmds.shelfButton(style='iconAndTextVertical',
                                label='SelObj',ndp = True,
                                image1='polyMesh.png',
                                c = utilityProc.convertSelectionToObj)
                cmds.shelfButton(style='iconAndTextVertical',
                                label='MakeSet',ndp = True,
                                image1='createSelectionSet.png',
                                c = utilityProc.createQuickSelectionSet)
                cmds.shelfButton(style='iconAndTextVertical',
                                iol = 'infLock',
                                label='Del All',ndp = True,
                                image1='unlockGeneric.png',bgc = (0.4,0.2,0.2),
                                c = lambda *args:self.cutKeyInflenceLock(all = True))
                cmds.text(l = '')

                cmds.shelfButton(style='iconAndTextVertical',
                                iol = 'key',
                                label='Set',ndp = True,bgc = (0.2,0.2,0.4),
                                image1='setKeyframe.png',
                                c = lambda *args:utilityProc.setKeyToTargetInflence(self.targetInflence))
                cmds.shelfButton(style='iconAndTextVertical',
                                iol = 'key',
                                label='Del',ndp = True,bgc = (0.4,0.2,0.2),
                                image1='setKeyframe.png',
                                c = lambda *args:utilityProc.cutKeyTotargetInflence(self.targetInflence))
                
        cmds.delete(tmpNode)
        cmds.select(selection)

        return self.customUi
    
    def setTargetJoint(self,*args,**kwargs):
        """対象のジョイントを設定する
        ウエイトペイントモードToolで選択されているインフルエンスジョイントを取得し、
        カスタムUIの回転コントロールに設定します。

        Args:
            None

        Returns:
            None
        """
        if not cmds.artAttrSkinPaintCtx(self.toolName,q = True,ex = True):
            self.errorPrint(errorType = 2)
            self.targetInflence = None

            return
       
        self.targetInflence = cmds.artAttrSkinPaintCtx(self.toolName,q = True,inf = True)

        if cmds.objExists(self.targetInflence):
            self.preValues = cmds.getAttr('{}.r'.format(self.targetInflence))[0]
        else:
            self.errorPrint(errorType = 3)
            self.targetInflence = None
            self.preValues = [0.0,0.0,0.0]

        try:
            cmds.attrFieldSliderGrp(self.attrControlX,e = True,
                                    at = '{}.rx'.format(self.targetInflence))
            cmds.attrFieldSliderGrp(self.attrControlY,e = True,
                                    at = '{}.ry'.format(self.targetInflence))
            cmds.attrFieldSliderGrp(self.attrControlZ,e = True,
                                    at = '{}.rz'.format(self.targetInflence))
        except:
            return
    
    def artSkinInflListChanged(self,*args,**kwargs):
        """artSkinInflListChangedのコールバック関数
        元のmelで定義されているartSkinInflListChangedをラップし、
        Tool側でターゲットのインフルエンスジョイントを取得して、回転可能にします。

        Args:
            None

        Returns:
            None
        """

        mel.eval('artSkinInflListChanged artAttrSkinPaintCtx;')
        self.setTargetJoint()

    def setCustomArtSkinInflListChanged(self,*args,**kwargs):
        """artSkinInflListChangedを設定する
        ウエイトペイントのtreeViewのコマンドをカスタムしたものに置き換えます。

        Args:
            None

        Returns:
            None
        """
        infListUi = mel.eval('$temp=$gArtSkinInfluencesList;')
        if not cmds.treeView(infListUi,q = True,ex = True):
            om.MGlobal.displayWarning('カスタムコマンドの格納に失敗しました。Toolの動作が正常でない可能性があります。')
            return
        
        cmds.treeView(infListUi,e = True,scc = self.artSkinInflListChanged)
    
    def createUI(self,*args,**kwargs):
        """UIを作成する
        toolPropertyWindowのレイアウトを調べ、インフルエンスリストのframeLayoutに
        カスタムUIを挿入します。

        Args:
            None

        Returns:
            None
        """
        MainToolSettingsLayout = cmds.toolPropertyWindow(q = True,loc = True)
        self.deleteUserControl()
        
        val = cmds.tabLayout(MainToolSettingsLayout, q = True, ca = True)
        
        fl = None
        for v in val:
            col = '{}|{}'.format(MainToolSettingsLayout,v)
            if not cmds.columnLayout(col,q = True,ex = True):
                continue

            children = cmds.columnLayout(col,q = True,ca = True) or []
            for ch in children:
                if not cmds.frameLayout(ch,q = True,ex = True):
                    continue
                labelName = cmds.frameLayout(ch,q =True,l = True)
                if isJapaneseLanguage():
                    if not labelName == 'インフルエンス':
                        continue
                elif not labelName == 'Influences':
                    continue
                
                # print(col)
                fl = cmds.frameLayout(ch,q = True,ca=True)[0]
                controls = cmds.formLayout(fl,q = True,ca = True)
                break
        
        if not fl:
            self.errorPrint(errorType = 4)
            return
        self.createCostomUi(parent=fl)
        cmds.formLayout(fl,e = True,ac = [(controls[-1],'bottom',0,self.customUi)],
                                    af = [(self.customUi,'bottom',0),
                                            (self.customUi,'left',0),
                                            (self.customUi,'right',0)])
