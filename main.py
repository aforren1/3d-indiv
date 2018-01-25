from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenImage import OnscreenImage
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import (PointLight, Spotlight, AntialiasAttrib, KeyboardButton, TransparencyAttrib)

import sys
import argparse
import numpy as np
import pandas as pd

class Individuation(ShowBase):
    def __init__(self, dev, trial_table):
        ShowBase.__init__(self)
        render.setAntialias(AntialiasAttrib.MMultisample)
        render.setShaderAuto() # allows shadows
        
        self.dev = dev
        self.disableMouse()

        self.table = pd.read_table(trial_table) # trial table
        self.load_models()
        self.setup_lights()
        self.setup_camera()
        taskMgr.add(self.get_user_input, 'move')

    def load_models(self):
        self.axes_model = loader.loadModel('axes')
        self.target = loader.loadModel('target')
        self.player = loader.loadModel('player')
        
        self.axes_model.reparentTo(render)
        
        self.target.reparentTo(render)
        self.target.setPos(-0.1, 0.2, 0)
        self.target.setScale(0.2, 0.2, 0.2)
        self.target.setTransparency(TransparencyAttrib.MAlpha)
        self.target.setAlphaScale(0.7)
        self.target.hide()      

        self.player.reparentTo(render)
        self.player.setPos(0, 0, 0)
        self.player.setScale(0.1, 0.1, 0.1)
        
        self.cam2dp.node().getDisplayRegion(0).setSort(-20)
        OnscreenImage(parent = self.cam2dp, image = 'background.jpg')

    def setup_lights(self):
        pl = PointLight('pl')
        pl.setColor((1, 1, 1, 1))
        plNP = render.attachNewNode(pl)
        plNP.setPos(-0.5, -0.5, 0.5)
        render.setLight(plNP)

        pos = [[[0, 0, 3], [0, 0, -1]],
               [[0, -3, 0], [0, 1, 0]],
               [[-3, 0, 0], [1, 0, 0]]]
        for i in pos:
            dl = Spotlight('dl')
            dl.setColor((1, 1, 1, 1))
            dlNP = render.attachNewNode(dl)
            dlNP.setPos(*i[0])
            dlNP.lookAt(*i[1])
            dlNP.node().setShadowCaster(True)
            render.setLight(dlNP)

    def setup_camera(self):
        self.cam.setPos(-2, -4, 2)
        self.cam.lookAt(0, 0, 0)

    def get_user_input(self, task):
        dt = globalClock.get_dt()
        if dt > 0.018:
            print(dt)
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            self.player.setPos(x, y, 0)
        return task.cont

    def update_state(self, task):
        self.state_machine.step()

states = ['pretrial', 'moving', 'hold_in_target', 'post_trial']  
# pretrial: wait for space press, show text instruction on screen
# moving: show target (`self.target.show()` and set the position),
# wait until user is at least a distance from the center of the target
# hold_in_target: hold force in target for 1 second
# post_trial: save things, wait ~1s before next instruction; also, check for block end

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help='Subject ID', default='007')
    parser.add_argument('--tgt', help='Path to trial table', default='test.txt')
    parser.add_argument('--dev', help='Device to use', default='mouse')
    args = parser.parse_args()
    print(args)
    if args.dev is 'mouse':
        pass
    demo = Individuation(dev=args.dev, trial_table=args.tgt)
    demo.run()
