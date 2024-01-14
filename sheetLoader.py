import pygame

# Sheet format  |  name  ->  (path: str, tile size: (width: int, height: int), sheet size: (width: int, height: int))

sheets = {
    'primary' : ('Tilemap Editor\Tilesheets\primary_sheet.png', (16, 16), (13, 13)),
    'col' : ('Tilemap Editor\Tilesheets\TopToolkitCol.png', (16, 16), (3, 1)),
    'decor': ('Tilemap Editor\Tilesheets\TopToolkitDecor.png', (16, 16), (3, 1)),
    'custom' : ('Tilemap Editor\Tilesheets\TopToolkitCustom.png', (16, 16), (3, 3))
}

def load_sheet(path: str, tile_size: tuple[int, int], dimensions: tuple[int, int]) -> list:
    '''
    Splits a tilesheet into a list of pygame surfaces
    Args:
        path: str
            The relative path of the sheet's image (.png)
        tile_size: (int, int)
            Number of pixels for each tiles width and height
        dimensions: (width, height)
            The width and height of the number of tiles in the sheet
    '''
    sprites = []
    sheet_img = pygame.image.load(path)

    # Loop through tiles
    for y in range(0, dimensions[1]):
        for x in range(0, dimensions[0]):
            # Create empty surface of tile size
            sprite = pygame.Surface((tile_size[0], tile_size[1]), pygame.SRCALPHA)
            sprite.fill((0, 0, 0, 0))
            # Blit desired cutout of the sheet image to the surface
            sprite.blit(sheet_img, (-x * tile_size[0], -y * tile_size[1]))

            sprites.append(sprite)
    
    return sprites