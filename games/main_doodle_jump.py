# -*- coding: utf-8 -*-
"""
    CopyLeft 2021 Michael Rouves

    This file is part of Pygame-DoodleJump.
    Pygame-DoodleJump is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Pygame-DoodleJump is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Pygame-DoodleJump. If not, see <https://www.gnu.org/licenses/>.
"""

import pygame, sys, os, subprocess
import serial, threading

from games.singleton import Singleton
from games.camera import Camera
from games.player import Player
from games.level import Level
import games.settings as config
from modules.thread_communication import ThreadSettings, arduino_communication

pygame.init()
t_settings = None
class Game(Singleton):
    """
    A class to represent the game.

    used to manage game updates, draw calls and user input events.
    Can be access via Singleton: Game.instance .
    (Check Singleton design pattern for more info)
    """

    # constructor called on new instance: Game()
    def __init__(self) -> None:

        # ============= Initialisation =============
        self.__alive = True
        # Window / Render
        self.window = pygame.display.set_mode(config.DISPLAY,config.FLAGS)
        self.clock = pygame.time.Clock()

        # Instances
        self.camera = Camera()
        self.lvl = Level()
        self.player = Player(
            config.HALF_XWIN - config.PLAYER_SIZE[0]/2,# X POS
            config.HALF_YWIN + config.HALF_YWIN/2,#      Y POS
            *config.PLAYER_SIZE,# SIZE
            config.PLAYER_COLOR#  COLOR
        )

        # User Interface
        self.score = 0
        self.score_txt = config.SMALL_FONT.render("0 m",1,config.GRAY)
        self.score_pos = pygame.math.Vector2(10,10)

        self.gameover_txt = config.SMALL_FONT.render("Game Over",1,config.GRAY)
        self.gameover_rect = self.gameover_txt.get_rect(
            center=(config.HALF_XWIN,config.HALF_YWIN))


    def close(self):
        t_settings.run = False
        self.__alive = False


    def reset(self):
        self.camera.reset()
        self.lvl.reset()
        self.player.reset()


    def _event_loop(self):
        # ---------- User Events ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                if (event.key == pygame.K_RETURN or event.key == pygame.K_RIGHT) and self.player.dead:
                    # print("reset")
                    self.reset()
                elif pygame.K_LEFT and self.player.dead:
                    self.close()

            self.player.handle_event(event)


    def _update_loop(self):
        # ----------- Update -----------
        self.player.update()
        self.lvl.update()

        if not self.player.dead:
            self.camera.update(self.player.rect)
            #calculate score and update UI txt
            self.score=-self.camera.state.y//50
            self.score_txt = config.SMALL_FONT.render(
                str(self.score)+" m", 1, config.GRAY)


    def _render_loop(self):
        # ----------- Display -----------
        self.window.fill(config.WHITE)
        self.lvl.draw(self.window)
        self.player.draw(self.window)

        # User Interface
        if self.player.dead:
            self.window.blit(self.gameover_txt,self.gameover_rect)# gameover txt
        self.window.blit(self.score_txt, self.score_pos)# score txt

        pygame.display.update()# window update
        self.clock.tick(config.FPS)# max loop/s


    def run(self):
        # ============= MAIN GAME LOOP =============
        while self.__alive:
            
            self._update_loop()
            self._render_loop()
            self._event_loop()



# if __name__ == "__main__":
# ============= PROGRAM STARTS HERE =============
def main(threshold):
    global t_settings

    t_settings = ThreadSettings(True, threshold)
    t1 = threading.Thread(target=arduino_communication, args=(pygame.K_LEFT, pygame.K_RIGHT, t_settings, pygame))
    t1.start()
    game = Game()
    game.run()

    t1.join()
    pygame.display.quit()


    # os.chdir("..")
    # subprocess.Popen("python " + "menu.py", shell=True)

