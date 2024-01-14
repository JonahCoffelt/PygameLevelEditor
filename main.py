import editor

'''
Add Sheet
    To add a tilesheet, add the path and data to both the sheetLoader sheets dictionary and the first line of Data/config.txt.
    The sheet will be able to be chosen when making a new layer or renaming an existing layer.

---------------------------------------------------------------

SDL2 Pygame Rendering Explanation (Because I will forget):

Old method (Per Tile Rendering):
    The sheetLoader.load_sheet() function converts all of the tiles into normal pygame surfaces
    The world_map.get_tiles() fucntion converts all the tile surfs into pygame SDL2 textures
    To render a tile, use texture.draw(dstrect=(x, y, w, h))
Old method2 (Using Caching): 
    The sheetLoader.load_sheet() function converts all of the tiles into normal pygame surfaces
    The draw_chunk() function creates a surface for an entire chunk
    The draw_cached_chunks() function converts the chunk surfaces to textures
    To render a chunk, use texture.draw(dstrect=(x, y, w, h))

New method (Using Texture Caching): 
    The sheetLoader.load_sheet() function converts all of the tiles into normal pygame surfaces
    The draw_chunk() function creates a surface for an entire chunk
    This surface is converted to a texture, both of which are cached for later reading/writing
    To render a chunk, use texture.draw(dstrect=(x, y, w, h))

The biggest boost in preformace resulted from the use of cached textures.
The action of converting a surface to a texture simply took too long.
The surfaces are only stored as a means to write the updates to chunks easily. 
The major drawback here is memory usage (About 2 GB RAM for 1 million tiles).

---------------------------------------------------------------

World File Format:
    The world is stored in a dictionary of layers.
    The layers contain a dictionary of chunks. Chunks names are in the format 'x;y'.
    Each chunk is a 2d array of tile IDs as well as the tilesheet which is referenced.

world = {
    'Layer1' : {
        'sheet' : 'primary',
        '1;1' : [[1, 2], [0, 1]],
        '1;2' : [...]
    },
    'Layer2' : {...}
}

world['layer']['1;1'][x][y]

---------------------------------------------------------------

Undo Actions Format:
    A list of lists containing information about calls of the set_tile() function

undo_actions = [[ID, [x, y], 'layer'], [...]]

'''

app = editor.Editor()
app.start()