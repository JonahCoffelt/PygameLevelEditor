import sys
import pygame
from pygame._sdl2.video import Window, Renderer
import numpy as np

import mapRenderer
import UIDisplay

class Editor():
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()

        self.win_size = (800, 800)

        self.win = Window(title="Level Editor", size=self.win_size, resizable=True) # Creates and SDL2 Window
        self.renderer = Renderer(self.win) # Creates renderer from the window

        self.clock = pygame.time.Clock()

    def draw(self) -> None:
        '''
        Handels all rendering to the window
        '''
        self.renderer.draw_color = (31, 31, 31, 255)
        self.renderer.fill_rect((0, 0) + self.win_size)

        self.map_renderer.draw(self.cam, self.win_size, self.UI.layer_opacity) # Draws the map
        if not self.tool != 'draw': self.map_renderer.draw_hover(self.mouse_world_pos, self.cam, self.current_tile - 1) # Draws a silhouette of current tile

        self.UI.draw(self.win_size, self.map_renderer.world, self.map_renderer.layer, (self.mouseX, self.mouseY), self.tool, self.map_renderer.world[self.map_renderer.layer]['sheet']) # Draws UI viewports
        self.UI.debug(self.win_size, self.mouse_world_pos, round(self.clock.get_fps()))

        self.renderer.present() # Similar to the pyame.display.flip() function

    def save(self, name):
        if name:
            with open (f"Tilemap Editor\Saves\{name}.txt", 'w') as file: 
                file.write(str(self.map_renderer.world) + '\n')
                file.write(str(self.UI.rule_positions) + '\n')
    
    def load(self, path):
        if path:
            self.current_tile = np.array([[1]])
            self.UI.selected_tiles = np.array([[1]])
            with open (path, 'r') as file:
                line = file.readline()
                layer_data = eval(line)
                line = file.readline()
                rule_data = eval(line)
                self.map_renderer.load_from_file(layer_data)
                self.UI.rule_positions = rule_data

    def start(self) -> None:
        '''
        Initialize all editor specific variables and start mainloop
        '''
        self.map_renderer = mapRenderer.world_map(self.renderer)
        self.UI = UIDisplay.UI(self.renderer)
        
        self.cam = [0, 0] # World position of view
        self.tile_view_frame = 15 # Number of tiles displayed in the y direction above and below the center
        self.map_renderer.set_tile_size(self.win_size, self.tile_view_frame)

        self.current_tile = np.array([[1]])
        self.tool = 'draw'

        self.run = True
        while self.run: # Mainloop
            self.dt = self.clock.tick() / 1000 # Time passed in milliseconds from the last frame
            self.mouseX, self.mouseY = pygame.mouse.get_pos()
            self.mouse_world_pos = (int((self.mouseX - self.win_size[0]/2 + self.cam[0] * self.map_renderer.tile_size) // self.map_renderer.tile_size), int((self.mouseY - self.win_size[1]/2 - self.cam[1] * self.map_renderer.tile_size) // self.map_renderer.tile_size))
            self.keys = pygame.key.get_pressed()

            if self.keys[pygame.K_SPACE]:
                self.tool = 'move'
            elif self.keys[pygame.K_LALT]:
                self.tool = 'pick'
            elif self.keys[pygame.K_r]:
                self.tool = 'rule'
            else:
                self.tool = 'draw'

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.win.destroy()
                    self.run = False
                    pygame.quit()
                    print("|--- Editor Exited ---|")
                    sys.exit()

                if event.type == pygame.VIDEORESIZE: # Change the window size and variables. Update tiles to window size
                    self.win_size = (event.w, event.h)
                    self.map_renderer.set_tile_size(self.win_size, self.tile_view_frame)
                
                if event.type == pygame.MOUSEWHEEL:
                    if 0 < self.mouseX < self.win_size[0] * self.UI.left_viewport: # UI bar scrolling 
                        self.UI.scroll(self.win_size, self.mouseY, event.y)
                    else: # Zoom in/out world view
                        self.tile_view_frame += event.y
                        if self.tile_view_frame < 2: self.tile_view_frame = 2
                        self.map_renderer.set_tile_size(self.win_size, self.tile_view_frame)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.UI.show_rule and (1 - self.UI.bottom_viewport) * self.win_size[1] - self.UI.viewport_drag_buffer < self.mouseY < (1 - self.UI.bottom_viewport) * self.win_size[1] + self.UI.viewport_drag_buffer:
                        self.UI.drag_bottom = True
                    elif self.mouseY > (1 - self.UI.bottom_viewport) * self.win_size[1] and self.mouseX > self.UI.left_viewport * self.win_size[0]:
                        self.UI.click_bottom(self.win_size, (self.mouseX, self.mouseY))
                    if self.mouseX > self.UI.left_viewport * self.win_size[0] + self.UI.viewport_drag_buffer and self.mouseY > self.UI.top_viewport: # Start drawing stroke
                        if self.tool == 'move':
                            self.drag_move_start = (self.mouseX, self.mouseY, self.cam[0], self.cam[1])
                        elif event.button != 2 and self.tool == 'draw':
                            self.map_renderer.undo_actions.append(['start'])
                    elif self.UI.left_viewport * self.win_size[0] - self.UI.viewport_drag_buffer < self.mouseX < self.UI.left_viewport * self.win_size[0] + self.UI.viewport_drag_buffer:
                        self.UI.drag_left = True
                    else:
                        if event.button == 1:
                            self.UI.mouse_down(self.win_size, self.mouseX, self.mouseY)
                            UI_selection = self.UI.click(self.win_size, self.mouseX, self.mouseY, self.map_renderer.world, self.map_renderer.world[self.map_renderer.layer]['sheet'])
                            if UI_selection != -1:
                                if UI_selection[0] == 'tile': self.current_tile = UI_selection[1]
                                elif UI_selection[0] == 'layer':
                                    self.map_renderer.layer = UI_selection[1]
                                    self.current_tile = np.array([[1]])
                                    self.UI.selected_tiles = np.array([[1]])
                                elif UI_selection[0] == 'addlayer': self.map_renderer.add_layer(UI_selection[1], UI_selection[2])
                                elif UI_selection[0] == 'rename': 
                                    self.map_renderer.rename_layer(UI_selection[1], UI_selection[2], UI_selection[3])
                                    if UI_selection[3]:
                                        self.current_tile = np.array([[1]])
                                        self.UI.selected_tiles = np.array([[1]])
                                elif UI_selection[0] == 'reorder': self.map_renderer.reorder_layers(UI_selection[1], UI_selection[2])
                                elif UI_selection[0] == 'save': self.save(UI_selection[1])
                                elif UI_selection[0] == 'load': self.load(UI_selection[1])
                
                if event.type == pygame.MOUSEBUTTONUP:
                    mouseup = self.UI.mouse_up(self.win_size, self.map_renderer.world[self.map_renderer.layer]['sheet'])
                    if mouseup[0] == 'tile': 
                        self.current_tile = mouseup[1]
                    if self.tool == 'pick':
                        new_selection = self.map_renderer.get_tile(self.mouse_world_pos)
                        if new_selection != -1: 
                            self.current_tile = np.array([[new_selection]])
                            self.UI.selected_tiles = np.array([[new_selection]])
                    self.UI.drag_left = False
                    self.UI.drag_bottom = False
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_z and self.keys[pygame.K_LCTRL]:
                        self.map_renderer.undo()

            if self.UI.drag_left: self.UI.drag_viewport(self.win_size, self.mouseX)
            if self.UI.drag_bottom: self.UI.drag_rules_viewport(self.win_size, self.mouseY)

            if self.mouseX > self.UI.left_viewport * self.win_size[0] + self.UI.viewport_drag_buffer and self.UI.top_viewport < self.mouseY and (self.mouseY < self.win_size[1] * (1 - self.UI.bottom_viewport) or not self.UI.show_rule):
                if pygame.mouse.get_pressed()[0]:
                    if self.tool == 'move':
                        self.cam[0] = self.drag_move_start[2] + (self.drag_move_start[0] - self.mouseX) / self.map_renderer.tile_size
                        self.cam[1] = self.drag_move_start[3] - (self.drag_move_start[1] - self.mouseY) / self.map_renderer.tile_size
                    elif self.tool == 'draw':
                        self.map_renderer.set_tiles(self.mouse_world_pos, self.current_tile)
                    elif self.tool == 'rule':
                        if self.current_tile[0][0] in self.UI.rule_positions[self.map_renderer.world[self.map_renderer.layer]['sheet']]:
                            self.map_renderer.rule_draw(self.mouse_world_pos, self.UI.rule_positions[self.map_renderer.world[self.map_renderer.layer]['sheet']][self.current_tile[0][0]])
                if pygame.mouse.get_pressed()[2] and self.tool == 'draw':
                    self.map_renderer.set_tiles(self.mouse_world_pos, [[0]])
                if pygame.mouse.get_pressed()[1] and self.tool == 'draw':
                    if self.map_renderer.get_tile(self.mouse_world_pos) != self.current_tile[0][0] and len(self.current_tile) == 1 and len(self.current_tile[0]) == 1:
                        self.map_renderer.undo_actions.append(['start'])
                        self.map_renderer.current_fill = 0
                        self.map_renderer.fill_tiles(self.mouse_world_pos, self.current_tile)
            else:
                if pygame.mouse.get_pressed()[0]:
                    self.UI.mouse_held(self.win_size, self.mouseX, self.mouseY)
            self.draw()