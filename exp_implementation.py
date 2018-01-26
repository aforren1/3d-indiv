import sys

import numpy as np
import pandas as pd
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import (AntialiasAttrib, PointLight, Spotlight, TextNode,
                          TransparencyAttrib)

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
        taskMgr.add(self.update_state, 'update_state')
        self.accept('space', self.space_on)  # toggle a boolean somewhere

        # helpers
        self.space = False
        self.trial_counter = 0
        self.dist = 100
        self.queue = list()

    def load_models(self):
        self.axes_model = self.loader.loadModel('models/axes')
        self.target = self.loader.loadModel('models/target')
        self.player = self.loader.loadModel('models/player')

        self.axes_model.reparentTo(self.render)

        self.target.reparentTo(self.render)
        self.target.setPos(-0.1, 0.2, 0)
        self.target.setScale(0.05, 0.05, 0.05)
        self.target.setColorScale(0, 0, 0, 1)
        self.target.setTransparency(TransparencyAttrib.MAlpha)
        self.target.setAlphaScale(0.7)
        self.target.hide()

        self.player.reparentTo(self.render)
        self.player.setPos(0, 0, 0)
        self.player.setScale(0.03, 0.03, 0.03)

        self.cam2dp.node().getDisplayRegion(0).setSort(-20)
        OnscreenImage(parent=self.cam2dp, image='models/background.jpg')

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

    def space_on(self):
        self.space = True

    def get_user_input(self, task):
        dt = taskMgr.globalClock.get_dt()
        if self.mouseWatcherNode.hasMouse():
            x = self.mouseWatcherNode.getMouseX()
            y = self.mouseWatcherNode.getMouseY()
            self.player.setPos(x, y, 0)
        return task.cont

    def update_target_color(self, task):
        dist = np.sqrt((self.player.get_x() - self.target.get_x()) ** 2 +
                       (self.player.get_y() - self.target.get_y()) ** 2 +
                       (self.player.get_z() - self.target.get_z()) ** 2)
        d2 = 1 - dist
        self.dist = dist
        self.target.setColorScale(d2, d2, d2, 0.7)
        return task.cont

    def update_state(self, task):
        self.step()
        return task.cont

    # state machine functions
    def wait_for_space(self):
        return self.space

    def start_trial_countdown(self):
        self.countdown_timer.reset(10)

    def show_target(self):
        self.target.show()

    def trial_text(self):
        self.text.setText('Move for the target!')

    def close_to_target(self):
        return self.dist < 0.05

    def start_hold_countdown(self):
        self.countdown_timer.reset(2)

    def hold_text(self):
        self.text.setText('HOLD IT')

    def time_elapsed(self):
        return self.countdown_timer.elapsed() < 0

    def hide_target(self):
        self.target.hide()

    def start_post_countdown(self):
        self.countdown_timer.reset(2)

    def queue_distance(self):
        self.queue.append(self.close_to_target())

    def check_distance(self):
        tmp = np.sum(self.queue)/len(self.queue)
        self.queue = list()
        if tmp > 0.5:
            self.pop.play()

    def increment_trial_counter(self):
        self.trial_counter += 1

    def write_trial_data(self):
        pass

    def trial_counter_exceeded(self):
        return self.trial_counter > self.table.shape[0]

    def reset_keyboard_bool(self):
        self.space = False

    def post_text(self):
        self.text.setText('Relax!!!!')

    def kb_text(self):
        self.text.setText('Press space to start')
    
    def clean_up(self):
        sys.exit()
