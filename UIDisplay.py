import pygame
from pygame._sdl2.video import Renderer, Texture
import numpy as np

import sheetLoader
import EntryBox

primary_tile_size = 16
primary_sheet_dims = (13, 13)

icon_tags = {'move': 1, 'pick' : 2, 'rule' : 5}

class UI():
    def __init__(self, renderer: Renderer) -> None:
        self.font = pygame.font.Font('Tilemap Editor\Fonts\PixelDigivolve-mOm9.ttf', 18)

        self.renderer = renderer
        self.left_viewport = .25 # %
        self.top_viewport = 40   # px
        self.bottom_viewport = .3  # %
        self.viewport_drag_buffer = 10 # px
        self.show_rule = False

        rule_template_img = pygame.image.load('Tilemap Editor\Images\RuleTileTemplate.png')
        rule_empty_img = pygame.image.load('Tilemap Editor\Images\RuleTileTemplate.png')
        self.rule_template_texture = Texture.from_surface(self.renderer, rule_template_img)
        self.rule_empty_texture = Texture.from_surface(self.renderer, rule_empty_img)

        self.startx = 0

        self.selected_tiles = [[1]]
        self.selected_rule_position = 0
        self.rule_positions = {}

        self.drag_left = False
        self.drag_bottom = False

        self.tile_divisions = 1
        self.y_scroll = 0
        self.selection = 1

        self.layer_opacity = 150 # alpha (255)
        self.layer_box_height = 30 # px
        self.top_box_width = 150 # px
        self.top_buttons = ['save', 'load', 'rule tile']

        self.tiles = {}
        self.get_tile_textures()
    
    def scroll(self, win_size: tuple[int, int], mousey: int, scroll_value: int) -> None:
        '''
        Scrolls the UI Bar (tile selection)
        Args:
            win_size: (w, h)
                The number of pixels of the width and height of the window
            mousey: int:
                The y of the mouse in the window in pixels
            scroll_value: int
                The magnatiude of the scroll
        '''
        if win_size[1]/2 < mousey < win_size[1]:
            self.y_scroll += scroll_value

    def mouse_down(self, win_size: tuple[int, int], mousex: int, mousey: int):
        if 10 < mousex < win_size[0] * self.left_viewport - 10 and win_size[1]/2 + 10 < mousey < win_size[1] - 10:
           self.startx, self.starty = mousex, mousey
        else:
            self.startx = None
    
    def mouse_held(self, win_size: tuple[int, int], mousex: int, mousey: int):
        if 10 < mousex < win_size[0] * self.left_viewport - 10 and win_size[1]/2 + 10 < mousey < win_size[1] - 10:
           self.endx, self.endy = mousex, mousey

    def mouse_up(self, win_size: tuple[int, int], sheet: str):
        if self.startx:

            sheet_info = sheetLoader.sheets[sheet]
            
            if self.startx > self.endx:
                temp_x = self.endx
                self.endx = self.startx
                self.startx = temp_x
            if self.starty > self.endy:
                temp_y = self.endy
                self.endy = self.starty
                self.starty = temp_y

            start_tile = [int((self.startx - 10) // self.tile_size), int((self.starty - (win_size[1]/2 + 10) - self.tile_size * self.y_scroll) // self.tile_size)]
            end_tile = [int((self.endx - 10) // self.tile_size) + 1, int((self.endy - (win_size[1]/2 + 10) - self.tile_size * self.y_scroll) // self.tile_size) + 1]

            if start_tile[0] < 0: start_tile[0] = 0
            if start_tile[1] < 0: start_tile[1] = 0
            if end_tile[0] >= sheet_info[2][0]: end_tile[0] = sheet_info[2][0]
            if end_tile[1] >= sheet_info[2][1]: end_tile[1] = sheet_info[2][1]

            x_range = np.arange(start_tile[0], end_tile[0]) + 1
            y_range = np.arange(start_tile[1], end_tile[1]) * sheet_info[2][0]
            selection = x_range + y_range[:, None]
            self.startx = None
            self.selected_tiles = selection
            if self.show_rule: self.rule_positions[sheet][self.rule_base_tile][self.selected_rule_position] = selection[0][0]
            return ('tile', selection)
        self.startx = None
        return [-1]

    def click(self, win_size: tuple[int, int], mousex: int, mousey: int, layers: dict, sheet: str) -> int:
        '''
        Click opperation in the UI Bar. Returns the selected operation and corrosponding information, otherwise returns -1
        Args:
            win_size: (w, h)
                The number of pixels of the width and height of the window
            mousex: int:
                The x position of the mouse in the window in pixels
            mousey: int:
                The y position of the mouse in the window in pixels
        '''
        if self.layer_box_height * 2 + self.top_viewport < mousey < self.layer_box_height * (2 + len(layers)) + self.top_viewport:
            item =  list(layers.keys())[(mousey - self.top_viewport) // self.layer_box_height - 2]
            if mousex < win_size[0] * self.left_viewport - self.layer_box_height * 2 - 10 or mousey < self.layer_box_height * 5 + self.top_viewport:
                self.show_rule = False
                return ('layer', item)
            elif mousex < win_size[0] * self.left_viewport - self.layer_box_height - 10:
                local_y = mousey - self.layer_box_height * ((mousey - self.top_viewport) // self.layer_box_height) - self.top_viewport
                if local_y < self.layer_box_height / 2: # Move Up
                    if (mousey - self.top_viewport) // self.layer_box_height - 2 > 3:
                        return ('reorder', item, list(layers.keys())[(mousey - self.top_viewport) // self.layer_box_height - 3])
                else: # Move Down
                    if (mousey - self.top_viewport) // self.layer_box_height - 1 < len(list(layers.keys())):
                        return ('reorder', list(layers.keys())[(mousey - self.top_viewport) // self.layer_box_height - 1], item)
            else:
                EntryBox.entry()
                if EntryBox.entry_value:
                    return ('rename', item, EntryBox.entry_value, EntryBox.drop_value)
        elif 10 < mousex < 10 + self.layer_box_height and self.top_viewport + self.layer_box_height * .5 < mousey < self.top_viewport + self.layer_box_height * .5 + self.layer_box_height:
            EntryBox.entry()
            return ('addlayer', EntryBox.entry_value, EntryBox.drop_value)
        elif 20 + self.layer_box_height < mousex < win_size[0] * self.left_viewport - 10 and self.top_viewport + self.layer_box_height * .5 < mousey < self.top_viewport + self.layer_box_height * .5 + self.layer_box_height:
            self.layer_opacity = ((mousex - self.layer_box_height - 20) / (self.left_viewport * win_size[0] - self.layer_box_height - 30)) * 255
        elif mousey < self.top_viewport:
            if mousex < self.top_box_width:
                EntryBox.save()
                return ('save', EntryBox.entry_value)
            elif self.top_box_width < mousex < self.top_box_width * 2:
                EntryBox.load()
                return ('load', EntryBox.file_name)
            elif self.top_box_width * 2 < mousex < self.top_box_width * 3:
                self.rule_base_tile = self.selected_tiles[0][0]
                if not self.rule_base_tile in self.rule_positions[sheet]: 
                    self.rule_positions[sheet][self.rule_base_tile] = [0 for i in range(13)]
                    self.rule_positions[sheet][self.rule_base_tile][6] = self.selected_tiles[0][0]
                self.show_rule = True
        return -1

    def get_tile_textures(self) -> None:
        '''
        Loads all the tile textures from sheet image(s)
        '''
        for sheet in sheetLoader.sheets:
            self.tiles[sheet] = []
            # Get list of tile surfaces
            tile_surfaces = sheetLoader.load_sheet(sheetLoader.sheets[sheet][0], sheetLoader.sheets[sheet][1], sheetLoader.sheets[sheet][2])
            for tile in tile_surfaces: # Crate a texture for each tile from its surf
                tile_texture = Texture.from_surface(self.renderer, tile)
                self.tiles[sheet].append(tile_texture)

        icon_surfaces = sheetLoader.load_sheet('Tilemap Editor\Images\TopDownToolkitUI.png', (16, 16), (6, 1))
        self.icons = []
        for icon in icon_surfaces:
            icon_texture = Texture.from_surface(self.renderer, icon)
            self.icons.append(icon_texture)

    def draw(self, win_size: tuple[int, int], layers: dict, layer_selection: str, mouse_pos: tuple[int, int], icon: int, sheet: str) -> None:
        '''
        Draws all UI elements
        Args:
            win_size: (w, h)
                The number of pixels of the width and height of the window
        '''
        # Left/World line
        self.renderer.draw_color = (0, 0, 0, 255)
        self.renderer.draw_line((win_size[0] * self.left_viewport, 0), (win_size[0] * self.left_viewport, win_size[1]))

        if not sheet in self.rule_positions:
                self.rule_positions[sheet] = {}

        self.draw_tiles(win_size, sheet) # Tile selection display
        
        # Layer selection display
        self.renderer.draw_color = (24, 24, 24, 255)
        self.renderer.fill_rect((0, 0, win_size[0] * self.left_viewport, win_size[1]/2))
        self.draw_layers(win_size, layers, layer_selection)

        self.draw_top_viewport(win_size)

        if self.show_rule: self.draw_bottom_viewport(win_size, sheet)

        if self.startx:
            self.renderer.draw_color = (255, 255, 255, 150)
            self.renderer.fill_rect((self.startx, self.starty, self.endx - self.startx, self.endy - self.starty))

        if icon != 'draw': self.draw_mouse_icon(mouse_pos, icon)
    
    def draw_mouse_icon(self, mouse_pos: tuple[int, int], icon: int):
        icon_size = 15
        self.icons[icon_tags[icon]].draw(dstrect=(mouse_pos[0] - icon_size, mouse_pos[1] - icon_size, icon_size * 2, icon_size * 2))

    def draw_top_viewport(self, win_size: tuple[int, int]):
        self.renderer.draw_color = (24, 24, 24, 255)
        self.renderer.fill_rect((0, 0, win_size[0], self.top_viewport))
        self.renderer.draw_color = (0, 0, 0, 255)
        self.renderer.draw_line((0, self.top_viewport), (win_size[0], self.top_viewport))

        for i, text in enumerate(self.top_buttons):
            text_surf = self.font.render(text, False, (255, 255, 255, 255))
            text_rect = text_surf.get_rect()
            text_texture = Texture.from_surface(self.renderer, text_surf)
            text_texture.draw(dstrect=((i + 1) * self.top_box_width - text_rect[2] / 2 - self.top_box_width / 2, 9, text_rect[2], text_rect[3]))
            self.renderer.draw_line(((i + 1) * self.top_box_width, 5), ((i + 1) * self.top_box_width, self.top_viewport - 5))

    def draw_bottom_viewport(self, win_size: tuple[int, int], sheet):
        self.renderer.draw_color = (24, 24, 24, 255)
        self.renderer.fill_rect((win_size[0] * self.left_viewport, win_size[1] * (1 - self.bottom_viewport), win_size[0] * (1 - self.left_viewport), win_size[1] * self.bottom_viewport))
        self.renderer.draw_color = (0, 0, 0, 255)
        self.renderer.draw_rect((win_size[0] * self.left_viewport, win_size[1] * (1 - self.bottom_viewport), win_size[0] * (1 - self.left_viewport), win_size[1] * self.bottom_viewport))

        template_height = (win_size[1] * self.bottom_viewport - 20)
        template_width = template_height * (34/20)
        pxl = template_height / 20

        self.rule_empty_texture.draw(dstrect=(win_size[0] * self.left_viewport + 10, win_size[1] * (1 - self.bottom_viewport) + 10, template_width, template_height))
        
        for i in range(13):
            if self.rule_positions[sheet][self.rule_base_tile][i]:
                self.tiles[sheet][self.rule_positions[sheet][self.rule_base_tile][i] - 1].draw(dstrect=(int(i % 5) * (template_width / 5) + (win_size[0] * self.left_viewport + 10) + pxl - 1, (i // 5) * (template_height / 3) + (win_size[1] * (1 - self.bottom_viewport) + 10) + pxl - 1, template_width / 5 - pxl * 3 + 3, template_height / 3 - pxl * 3 + 3))

        self.renderer.draw_color = (255, 255, 255, 100)
        self.renderer.fill_rect((int(self.selected_rule_position % 5) * (template_width / 5) + (win_size[0] * self.left_viewport + 10) + pxl - 1, (self.selected_rule_position // 5) * (template_height / 3) + (win_size[1] * (1 - self.bottom_viewport) + 10) + pxl - 1, template_width / 5 - pxl * 3 + 3, template_height / 3 - pxl * 3 + 3))

        text_surf = self.font.render('save', False, (255, 255, 255, 255))
        text_texture = Texture.from_surface(self.renderer, text_surf)
        text_texture.draw(dstrect=(int(13 % 5) * (template_width / 5) + (win_size[0] * self.left_viewport + 10) + pxl * 2 - 1, (13 // 5) * (template_height / 3) + (win_size[1] * (1 - self.bottom_viewport) + 10) + pxl - 1, template_width / 5 * 2 - pxl * 4.5 + 3, template_height / 3 - pxl * 3 + 3))

    def click_bottom(self, win_size: tuple[int, int], pos: tuple[int, int]):
        template_height = (win_size[1] * self.bottom_viewport - 20)
        template_width = template_height * (34/20)

        local_x = pos[0] - win_size[0] * self.left_viewport - 10
        local_y = pos[1] - win_size[1] * (1 - self.bottom_viewport) - 10

        tile_x, tile_y = local_x // (template_width // 5), local_y // (template_height // 3)
        self.selected_rule_position = int(tile_x + tile_y * 5)
        if self.selected_rule_position > 12 : 
            self.selected_rule_position = 12
            self.show_rule = False

    def draw_layers(self, win_size: tuple[int, int], layers: dict, layer_selection: str) -> None:

        self.icons[0].draw(dstrect=(10, self.top_viewport + self.layer_box_height * .5, self.layer_box_height, self.layer_box_height))
        self.renderer.draw_color = (137, 164, 119, 255)
        self.renderer.fill_rect((self.layer_box_height + 20, self.top_viewport + self.layer_box_height * .5, (self.layer_opacity / 255) * (self.left_viewport * win_size[0] - self.layer_box_height - 30), self.layer_box_height))
        self.renderer.draw_color = (0, 0, 0, 255)
        self.renderer.draw_rect((self.layer_box_height + 20, self.top_viewport + self.layer_box_height * .5, self.left_viewport * win_size[0] - self.layer_box_height - 30, self.layer_box_height))

        for i, layer_name in enumerate(layers):
            if layer_name == layer_selection:
                self.renderer.draw_color = (55, 55, 61, 255)
            else:
                self.renderer.draw_color = (31, 31, 31, 255)

            self.renderer.fill_rect((0, self.layer_box_height * (i + 2) + self.top_viewport, win_size[0] * self.left_viewport, self.layer_box_height))
            text_surf = self.font.render(layer_name, False, (255, 255, 255, 255))
            text_rect = text_surf.get_rect()
            text_texture = Texture.from_surface(self.renderer, text_surf)
            text_texture.draw(dstrect=(10, 4 + self.layer_box_height * (i + 2) + self.top_viewport, text_rect[2], text_rect[3]))

            if i > 2:
                self.icons[3].draw(dstrect=(win_size[0] * self.left_viewport - self.layer_box_height - 10, self.layer_box_height * (i + 2) + self.top_viewport, self.layer_box_height, self.layer_box_height))
                self.icons[4].draw(dstrect=(win_size[0] * self.left_viewport - self.layer_box_height * 2 - 10, self.layer_box_height * (i + 2) + self.top_viewport, self.layer_box_height, self.layer_box_height))

    def draw_tiles(self, win_size: tuple[int, int], sheet: str) -> None:
        '''
        Draws the selection of tiles in the UI bar.
        Args:
            win_size: (w, h)
                The number of pixels of the width and height of the window
        '''
        buffer = 10
        self.renderer.draw_color = (31, 31, 31, 255)
        sheet_info = sheetLoader.sheets[sheet]
        self.renderer.fill_rect((0, win_size[1]/2, win_size[0] * self.left_viewport, win_size[1]/2))
        self.tile_size = (win_size[0] * self.left_viewport - (buffer * 2)) // sheet_info[2][0] * self.tile_divisions
        for tile_y in range(sheet_info[2][1]):
            for tile_x in range(sheet_info[2][0]):
                if tile_x + tile_y * sheet_info[2][0] + 1 in self.selected_tiles:
                    self.renderer.draw_color = (255, 255, 255, 75)
                    self.renderer.draw_blend_mode = 1
                    self.tiles[sheet][tile_x + tile_y * sheet_info[2][0]].draw(dstrect=(buffer + tile_x * self.tile_size,  self.y_scroll * self.tile_size + buffer + win_size[1]/2 + tile_y * self.tile_size, self.tile_size - 1, self.tile_size - 1))
                    self.renderer.fill_rect((buffer + tile_x * self.tile_size,  self.y_scroll * self.tile_size + buffer + win_size[1]/2 + tile_y * self.tile_size, self.tile_size - 1, self.tile_size - 1))
                else:
                    self.tiles[sheet][tile_x + tile_y * sheet_info[2][0]].draw(dstrect=(buffer + tile_x * self.tile_size,  self.y_scroll * self.tile_size + buffer + win_size[1]/2 + tile_y * self.tile_size, self.tile_size - 1, self.tile_size - 1))

                if tile_x + tile_y * sheet_info[2][0] + 1 in self.rule_positions[sheet]:
                    self.icons[5].draw(dstrect=(buffer + tile_x * self.tile_size,  self.y_scroll * self.tile_size + buffer + win_size[1]/2 + tile_y * self.tile_size, self.tile_size - 1, self.tile_size - 1))


    def drag_viewport(self, win_size: tuple[int, int], mouseX: int) -> None:
        '''
        Changes the size of a UI viewport based on the mouse position
        Args:
            win_size: (w, h)
                The number of pixels of the width and height of the window
            mouseX: int
                The x position of the mouse in the window in pixels
        '''
        self.left_viewport = mouseX / win_size[0]
        if self.left_viewport < .15:
            self.left_viewport = .15
    
    def drag_rules_viewport(self, win_size: tuple[int, int], mouseY: int) -> None:
        self.bottom_viewport = 1 - mouseY / win_size[1]
        if self.bottom_viewport < .15:
            self.bottom_viewport = .15

    def debug(self, win_size: tuple[int, int], pos: tuple[int, int], fps: int):
        pos_surf = self.font.render(f'Position: {pos}', False, (255, 255, 255, 255))
        fps_surf = self.font.render(f'FPS: {fps}', False, (255, 255, 255, 255))

        pos_rect = pos_surf.get_rect()
        fps_rect = fps_surf.get_rect()

        pos_texture = Texture.from_surface(self.renderer, pos_surf)
        fps_texture = Texture.from_surface(self.renderer, fps_surf)

        pos_texture.draw(dstrect=(win_size[0] - pos_rect[2], self.top_viewport + 10, pos_rect[2], pos_rect[3]))
        fps_texture.draw(dstrect=(win_size[0] - 100, self.top_viewport + 10 + fps_rect[3] * 1.5, fps_rect[2], fps_rect[3]))