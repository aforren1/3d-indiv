import numpy as np
import pandas as pd
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText, TextNode
from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import (AntialiasAttrib, KeyboardButton, PointLight,
                          PStatClient, Spotlight, TransparencyAttrib)

import timers  # personal module
from machine import IndividuationStateMachine


class Individuation(ShowBase, IndividuationStateMachine):
    def __init__(self, dev, trial_table):
        ShowBase.__init__(self)
        IndividuationStateMachine.__init__(self)
        self.render.setAntialias(AntialiasAttrib.MMultisample)
        self.render.setShaderAuto()  # allows shadows

        self.dev = dev
        self.disableMouse()
        self.countdown_timer = timers.CountdownTimer()

        self.table = pd.read_table(trial_table)  # trial table
        self.setup_lights()
        self.setup_camera()
        self.load_models()
        self.load_audio()

        # add tasks (run every frame)
        taskMgr.add(self.get_user_input, 'move')
        taskMgr.add(self.update_target_color, 'target_color')
        self.setup_state_machine()
        self.accept('escape', self.esc_on)  # toggle a boolean somewhere

    def load_models(self):
        self.axes_model = self.loader.loadModel('axes')
        self.target = self.loader.loadModel('target')
        self.player = self.loader.loadModel('player')

        self.axes_model.reparentTo(self.render)

        self.target.reparentTo(self.render)
        self.target.setPos(-0.1, 0.2, 0)
        self.target.setScale(0.05, 0.05, 0.05)
        self.target.setColorScale(0, 0, 0, 1)
        self.target.setTransparency(TransparencyAttrib.MAlpha)
        self.target.setAlphaScale(0.7)
        # self.target.hide()

        self.player.reparentTo(self.render)
        self.player.setPos(0, 0, 0)
        self.player.setScale(0.03, 0.03, 0.03)

        self.cam2dp.node().getDisplayRegion(0).setSort(-20)
        OnscreenImage(parent=self.cam2dp, image='background.jpg')

        self.text = OnscreenText(text='Press space to start', pos=(-0.8, 0.8),
                                 scale=0.08, fg=(1, 1, 1, 1),
                                 bg=(0, 0, 0, 1), frame=(0.2, 0.2, 0.8, 1),
                                 align=TextNode.ACenter)
        self.text.reparentTo(self.aspect2d)

    def setup_lights(self):
        pl = PointLight('pl')
        pl.setColor((1, 1, 1, 1))
        plNP = self.render.attachNewNode(pl)
        plNP.setPos(-0.5, -0.5, 0.5)
        self.render.setLight(plNP)

        pos = [[[0, 0, 3], [0, 0, -1]],
               [[0, -3, 0], [0, 1, 0]],
               [[-3, 0, 0], [1, 0, 0]]]
        for i in pos:
            dl = Spotlight('dl')
            dl.setColor((1, 1, 1, 1))
            dlNP = self.render.attachNewNode(dl)
            dlNP.setPos(*i[0])
            dlNP.lookAt(*i[1])
            dlNP.node().setShadowCaster(True)
            self.render.setLight(dlNP)

    def setup_camera(self):
        self.cam.setPos(-2, -4, 2)
        self.cam.lookAt(0, 0, 0)

    def load_audio(self):
        self.pop = self.loader.loadSfx('Blop-Mark_DiAngelo-79054334.wav')

    def esc_on(self):
        self.esc = True

    def get_user_input(self, task):
        dt = taskMgr.globalClock.get_dt()
        if dt > 0.018:
            print(dt)
        if self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()
            self.player.setPos(x, y, 0)
        return task.cont

    def update_target_color(self, task):
        dist = np.sqrt((self.player.get_x() - self.target.get_x()) ** 2 + (self.player.get_y() -
                                                                           self.target.get_y()) ** 2 + (self.player.get_z() - self.target.get_z()) ** 2)
        d2 = 1 - dist
        if (dist < 0.05):
            self.text.setText('HOT!')
        else:
            self.text.setText('Cold...')
        self.target.setColorScale(d2, d2, d2, 0.7)
        return task.cont

    def setup_state_machine(self):
        pass

    def update_state(self, task):
        self.state_machine.step()
