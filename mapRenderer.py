import pygame
from pygame._sdl2.video import Texture

import sheetLoader
import ruleTiles

with open('Tilemap Editor\Data\config.txt', 'r') as file:
    data = file.readline()
    info = eval(data)

class world_map():
    def __init__(self, renderer) -> None:
        self.renderer = renderer

        self.tile_sheets = {}

        self.world = {}
        self.chunk_surfaces_cache = {}
        self.chunk_textures_cache = {}

        self.layer = 'Collisions'
        self.max_fill = 3900
        self.current_fill = 0
        self.updated_chunks = []

        self.num_tiles = 0

        self.undo_actions = [[0, [0, 0], 'Ground']]

        for layer in info['standard_layers']:
            self.add_layer(layer, info['standard_layers'][layer])
        self.get_tile_textures()

    def add_layer(self, name: str, sheet='primary') -> None:
        '''
        Add a blank layer to the world dictionary
        Args:
            name: str
                The display and lookup name of the layer
            sheet: str
                The lookup name of the tilesheet referenced by the layer
        '''
        if not name in self.world:
            if not sheet: sheet = 'primary'
            self.world[name] = {'sheet' : sheet}
            self.chunk_surfaces_cache[name] = {}
            self.chunk_textures_cache[name] = {}

    
    def rename_layer(self, old_name: str, new_name: str, sheet='') -> None:
        '''
        Change the name of a layer while retaining the order.
        This may also change th sheet of a layer if provided
        '''
        if not new_name in self.world:
            new_world_dict = {}
            new_cache_dict = {}
            new_texture_dict = {}
            for layer in self.world:
                if layer is old_name: 
                    new_world_dict[new_name] = self.world[old_name]
                    new_cache_dict[new_name] = self.chunk_surfaces_cache[old_name]
                    new_texture_dict[new_name] = self.chunk_textures_cache[old_name]
                else: 
                    new_world_dict[layer] = self.world[layer]
                    new_cache_dict[layer] = self.chunk_surfaces_cache[layer]
                    new_texture_dict[layer] = self.chunk_textures_cache[layer]
            self.world = new_world_dict
            self.chunk_surfaces_cache = new_cache_dict
            self.chunk_textures_cache = new_texture_dict
            self.layer = new_name

            if sheet: self.world[new_name]['sheet'] = sheet
    
    def reorder_layers(self, first: str, second: str) -> None:
        '''
        Swaps the order of two layers
        '''
        new_world_dict = {}
        new_cache_dict = {}
        new_texture_dict = {}
        for layer in self.world:
            if layer is second: 
                new_world_dict[first] = self.world[first]
                new_cache_dict[first] = self.chunk_surfaces_cache[first]
                new_texture_dict[first] = self.chunk_textures_cache[first]
            elif layer is first:
                new_world_dict[second] = self.world[second]
                new_cache_dict[second] = self.chunk_surfaces_cache[second]
                new_texture_dict[second] = self.chunk_textures_cache[second]
            else: 
                new_world_dict[layer] = self.world[layer]
                new_cache_dict[layer] = self.chunk_surfaces_cache[layer]
                new_texture_dict[layer] = self.chunk_textures_cache[layer]
        self.world = new_world_dict
        self.chunk_surfaces_cache = new_cache_dict
        self.chunk_textures_cache = new_texture_dict

    
    def get_tile_textures(self) -> None:
        '''
        Loads all the tile textures from sheet image(s)
        '''
        self.transparent_surf = pygame.Surface((info['tile_sheets']['primary'][1][0], info['tile_sheets']['primary'][1][0]), pygame.SRCALPHA)
        self.transparent_surf.fill((1, 1, 1))
        for sheet in sheetLoader.sheets:
            self.tile_sheets[sheet] = []
            tile_surfaces = sheetLoader.load_sheet(sheetLoader.sheets[sheet][0], sheetLoader.sheets[sheet][1], sheetLoader.sheets[sheet][2]) # Get list of tile surfaces
            for tile in tile_surfaces:
                self.tile_sheets[sheet].append(tile)

    def load_from_file(self, world_data) -> None:
        '''
        Processes and saves data from a save file. This will delete all existing data. This will load chunck texture cache.
        '''

        self.world = world_data
        self.chunk_surfaces_cache = {}

        for layer in self.world:
            self.chunk_surfaces_cache[layer] = {}
            self.chunk_textures_cache[layer] = {}
            for chunk in self.world[layer]:
                if chunk != 'sheet':
                    self.chunk_surfaces_cache[layer][chunk] = pygame.Surface((info['chunksize'] * info['tile_sheets']['primary'][1][0], info['chunksize'] * info['tile_sheets']['primary'][1][0]), pygame.SRCALPHA)
                    for tile_y in range(info['chunksize']):
                        for tile_x in range(info['chunksize']):
                            tile = self.world[layer][chunk][tile_x][tile_y]
                            if tile: self.chunk_surfaces_cache[layer][chunk].blit(self.tile_sheets[self.world[layer]['sheet']][tile - 1], (tile_x * info['tile_sheets']['primary'][1][0], tile_y * info['tile_sheets']['primary'][1][0]))
                    self.chunk_textures_cache[layer][chunk] = Texture.from_surface(self.renderer, self.chunk_surfaces_cache[layer][chunk])
        self.layer = list(self.world.keys())[0]

    def set_tile_size(self, win_size: tuple[int, int], tile_view_frame: int) -> None:
        '''
        Sets the number of pixels per tile for drawing to the screen
        Args:
            win_size: (w, h)
                The width and height of the window/screen in pixels
            tile_view_frame: int
                Number of tiles displayed in the y direction above and below the center
        '''
        self.tile_size = win_size[1] / 2 // tile_view_frame
        self.win_size = win_size

    def draw(self, pos: tuple[int, int], win_size: tuple[int, int], bg_alpha: int) -> None:
        for chunk in self.updated_chunks:
            self.chunk_surfaces_cache[chunk[0]][chunk[1]].set_colorkey((1, 1, 1))
            new_chunk_surf = pygame.Surface((info['chunksize'] * info['tile_sheets']['primary'][1][0], info['chunksize'] * info['tile_sheets']['primary'][1][0]), pygame.SRCALPHA)
            new_chunk_surf.blit(self.chunk_surfaces_cache[chunk[0]][chunk[1]], (0, 0))
            self.chunk_surfaces_cache[chunk[0]][chunk[1]] = new_chunk_surf

            self.chunk_textures_cache[chunk[0]][chunk[1]] = Texture.from_surface(self.renderer, self.chunk_surfaces_cache[chunk[0]][chunk[1]])


        self.updated_chunks = []

        chunk_limit_x = win_size[0] / 2 / self.tile_size / info['chunksize'] + 1
        chunk_limit_y = win_size[1] / 2 / self.tile_size / info['chunksize'] + 1

        layers_list = list(self.chunk_textures_cache.values())
        layers_list.reverse()
        for i, layer in enumerate(layers_list):
            if i < len(layers_list) - 3 or layer is self.chunk_textures_cache[self.layer]:
                alpha = bg_alpha
                if layer is self.chunk_textures_cache[self.layer]:
                    alpha = 255
                for chunk_name in layer:
                    chunk_x, chunk_y = chunk_name.split(';')
                    chunk_x, chunk_y = int(chunk_x), int(chunk_y)
                    if pos[0] // info['chunksize'] - chunk_limit_x < chunk_x < pos[0] // info['chunksize'] + chunk_limit_x and -pos[1] // info['chunksize'] - chunk_limit_y < chunk_y < -pos[1] // info['chunksize'] + chunk_limit_y:
                        chunk_texture = layer[chunk_name]
                        chunk_texture.alpha = alpha
                        chunk_texture.draw(dstrect=((-pos[0] + chunk_x * info['chunksize']) * self.tile_size + self.win_size[0] / 2, (pos[1] + chunk_y * info['chunksize']) * self.tile_size + self.win_size[1] / 2, self.tile_size * info['chunksize'], self.tile_size * info['chunksize']))


    def draw_hover(self, mouse_pos: tuple[int, int], cam: tuple[int, int], tiles: int) -> None:
        '''
        Displays the current drawing tile at the mouse world position.
        Args:
            mouse_pos: (x, y)
                The world position of the mouse
            cam: (x, y)
                The world position of the user
            tile: int
                The ID of the current tile
        '''
        self.renderer.draw_color = (255, 255, 255, 255)
        tile_x, tile_y = mouse_pos[0] % info['chunksize'], mouse_pos[1] % info['chunksize']
        chunk_x, chunk_y = mouse_pos[0] // info['chunksize'], mouse_pos[1] // info['chunksize']
        for rel_y, y in enumerate(tiles):
            for rel_x, x in enumerate(y):
                tile = x
                tile_texture = Texture.from_surface(self.renderer, self.tile_sheets[self.world[self.layer]['sheet']][tile])
                tile_texture.alpha = 175
                tile_texture.draw(dstrect=((-cam[0] + rel_x + tile_x + chunk_x * info['chunksize']) * self.tile_size + self.win_size[0] / 2, (cam[1] + tile_y + rel_y + chunk_y * info['chunksize']) * self.tile_size + self.win_size[1] / 2, self.tile_size, self.tile_size))

    def get_tile(self, pos: tuple[int, int]) -> int:
        '''
        Returns the id of a tile at a position
        Args:
            pos: (int, int)
                World point of the tile
        '''
        chunk_x, chunk_y = pos[0]//info['chunksize'], pos[1]//info['chunksize'] # Converts world position to chunk position
        chunk_key = str(chunk_x) + ';' + str(chunk_y)
        if chunk_key in self.world[self.layer]:
            tile_x, tile_y = pos[0] % info['chunksize'], pos[1] % info['chunksize']
            return self.world[self.layer][chunk_key][tile_x][tile_y]
        return -1
    
    def set_tile(self, pos: tuple[int, int], tile: int) -> None:
        '''
        Sets the ID of a single specific tile
        Args:
            pos: (int, int)
                World point of the tile
            tile: int
                ID of tile
        '''
        chunk_x, chunk_y = pos[0]//info['chunksize'], pos[1]//info['chunksize'] # Converts world position to chunk position
        chunk_key = str(chunk_x) + ';' + str(chunk_y)

        if not chunk_key in self.world[self.layer]: # Creates empty chunk if none exists
            self.world[self.layer][chunk_key] = [[0 for x in range(info['chunksize'])] for y in range(info['chunksize'])]

        tile_x, tile_y = pos[0] % info['chunksize'], pos[1] % info['chunksize']

        if self.world[self.layer][chunk_key][tile_x][tile_y] != tile:
            if self.undo_actions[-1] != ('set', (pos, self.world[self.layer][chunk_key][tile_x][tile_y])):
                self.undo_actions.append(('set', (pos, self.world[self.layer][chunk_key][tile_x][tile_y]), self.layer))
            
            self.world[self.layer][chunk_key][tile_x][tile_y] = tile

            self.num_tiles += 1

            self.draw_chunk(chunk_key, tile, tile_x, tile_y)

    def set_tiles(self, pos: tuple[int, int], tiles: list) -> None:
        for rel_y, y in enumerate(tiles):
            for rel_x, x in enumerate(y):
                tile = x
                tile_pos = (pos[0] + rel_x, pos[1] + rel_y)
                chunk_x, chunk_y = tile_pos[0]//info['chunksize'], tile_pos[1]//info['chunksize'] # Converts world position to chunk position
                chunk_key = str(chunk_x) + ';' + str(chunk_y)

                if not chunk_key in self.world[self.layer]: # Creates empty chunk if none exists
                    self.world[self.layer][chunk_key] = [[0 for x in range(info['chunksize'])] for y in range(info['chunksize'])]

                tile_x, tile_y = tile_pos[0] % info['chunksize'], tile_pos[1] % info['chunksize']

                if self.world[self.layer][chunk_key][tile_x][tile_y] != tile:
                    if self.undo_actions[-1] != ('set', (tile_pos, self.world[self.layer][chunk_key][tile_x][tile_y])):
                        self.undo_actions.append(('set', (tile_pos, self.world[self.layer][chunk_key][tile_x][tile_y]), self.layer))
                    
                    self.world[self.layer][chunk_key][tile_x][tile_y] = tile

                    self.num_tiles += 1

                    self.draw_chunk(chunk_key, tile, tile_x, tile_y)

    def draw_chunk(self, chunk: str, tile: int, tile_x: int, tile_y: int):
        if not chunk in self.chunk_surfaces_cache[self.layer]:
            self.chunk_surfaces_cache[self.layer][chunk] = pygame.Surface((info['chunksize'] * info['tile_sheets']['primary'][1][0], info['chunksize'] * info['tile_sheets']['primary'][1][0]), pygame.SRCALPHA)
        
        self.chunk_surfaces_cache[self.layer][chunk].blit(self.transparent_surf, (tile_x * info['tile_sheets']['primary'][1][0], tile_y * info['tile_sheets']['primary'][1][0]))
        if tile:
            self.chunk_surfaces_cache[self.layer][chunk].blit(self.tile_sheets[self.world[self.layer]['sheet']][tile - 1], (tile_x * info['tile_sheets']['primary'][1][0], tile_y * info['tile_sheets']['primary'][1][0]))

        if not (self.layer, chunk) in self.updated_chunks:
            self.updated_chunks.append((self.layer, chunk))

    def fill_tiles(self, pos: tuple[int, int], tile: int) -> None:
        '''
        Flood fill of a closed area of tiles. Has a maximum fill of 3900 tiles.
        Args:
            pos: (int, int)
                The starting world point of the fill
            tile: int
                ID of tile to fill space
        '''
        orig_tile = self.get_tile(pos)
        self.set_tiles(pos, tile)
        self.current_fill += 4
        if self.current_fill < self.max_fill:
            if self.get_tile((pos[0], pos[1] + 1)) == orig_tile: self.fill_tiles((pos[0], pos[1] + 1), tile)
            if self.get_tile((pos[0], pos[1] - 1)) == orig_tile: self.fill_tiles((pos[0], pos[1] - 1), tile)
            if self.get_tile((pos[0] + 1, pos[1])) == orig_tile: self.fill_tiles((pos[0] + 1, pos[1]), tile)
            if self.get_tile((pos[0] - 1, pos[1])) == orig_tile: self.fill_tiles((pos[0] - 1, pos[1]), tile)
    
    def rule_draw(self, pos: tuple[int, int], positions: list, propogate=True):
        tile = ruleTiles.get_tile_index(self, pos, positions)

        self.set_tile(pos, tile)

        if propogate:
            if self.get_tile((pos[0] + 1, pos[1] + 1)) in positions: self.rule_draw((pos[0] + 1, pos[1] + 1), positions, False)
            if self.get_tile((pos[0] + 1, pos[1])) in positions: self.rule_draw((pos[0] + 1, pos[1]), positions, False)
            if self.get_tile((pos[0] + 1, pos[1] - 1)) in positions: self.rule_draw((pos[0] + 1, pos[1] - 1), positions, False)
            if self.get_tile((pos[0] - 1, pos[1] + 1)) in positions: self.rule_draw((pos[0] - 1, pos[1] + 1), positions, False)
            if self.get_tile((pos[0] - 1, pos[1])) in positions: self.rule_draw((pos[0] - 1, pos[1]), positions, False)
            if self.get_tile((pos[0] - 1, pos[1] - 1)) in positions: self.rule_draw((pos[0] - 1, pos[1] - 1), positions, False)
            if self.get_tile((pos[0], pos[1] + 1)) in positions: self.rule_draw((pos[0], pos[1] + 1), positions, False)
            if self.get_tile((pos[0], pos[1] - 1)) in positions: self.rule_draw((pos[0], pos[1] - 1), positions, False)

    def undo(self) -> None:
        '''
        Will undo the latest bath of saved actions
        '''
        if len(self.undo_actions) > 1:
            while self.undo_actions[-1][0] != 'start' and len(self.undo_actions) > 1 and self.undo_actions[-2][0] != 'end':
                if self.undo_actions[-1][2] in self.world:
                    self.layer = self.undo_actions[-1][2]
                    self.set_tile(self.undo_actions[-1][1][0], self.undo_actions[-1][1][1])
                    del self.undo_actions[-1]
                else:
                    self.undo_actions = [[0, [0, 0]]]
                    break
            del self.undo_actions[-1]
        
        if len(self.undo_actions) == 0: self.undo_actions = [[0, [0, 0]]]