# State configs were determined with an external program
states = {14: 1, 62: 2, 56: 3, 248: 16, 224: 29, 227: 28, 131: 27, 143: 14, 255: 15, 254: 4, 191: 5, 251: 17, 239: 18, 7: 14, 28: 2, 138: 15, 193: 28, 30: 1, 31: 1, 15: 1, 120: 3, 124: 3, 60: 3, 240: 29, 241: 29, 225: 29, 195: 27, 199: 27, 135: 27, 207: 14, 159: 14, 126: 2, 63: 2, 249: 16, 252: 16, 231: 28, 243: 28, 223: 14, 127: 2, 253: 16, 247: 28}

# This converts from the tile states (which were derived from external program) to index format of the editor rule tiles
tile_to_rule_index = {
    1 : 0,
    2 : 1,
    3 : 2,
    4 : 3,
    5 : 4,
    14 : 5,
    15 : 6,
    16 : 7,
    17 : 8,
    18 : 9,
    27 : 10,
    28 : 11,
    29 : 12
}

def get_tile_index(map: list, pos: tuple[int, int], rules: list)-> int:
    tile_1 = int(map.get_tile((pos[0] + 1, pos[1] - 1)) in rules and map.get_tile((pos[0] + 1, pos[1] - 1)) != 0)
    tile_2 = int(map.get_tile((pos[0] + 1, pos[1])) in rules and map.get_tile((pos[0] + 1, pos[1])) != 0)
    tile_3 = int(map.get_tile((pos[0] + 1, pos[1] + 1)) in rules and map.get_tile((pos[0] + 1, pos[1] + 1)) != 0)
    tile_4 = int(map.get_tile((pos[0], pos[1] + 1)) in rules and map.get_tile((pos[0], pos[1] + 1)) != 0)
    tile_5 = int(map.get_tile((pos[0] - 1, pos[1] + 1)) in rules and map.get_tile((pos[0] - 1, pos[1] + 1)) != 0)
    tile_6 = int(map.get_tile((pos[0] - 1, pos[1])) in rules and map.get_tile((pos[0] - 1, pos[1])) != 0)
    tile_7 = int(map.get_tile((pos[0] - 1, pos[1] - 1)) in rules and map.get_tile((pos[0] - 1, pos[1] - 1)) != 0)
    tile_8 = int(map.get_tile((pos[0], pos[1] - 1)) in rules and map.get_tile((pos[0], pos[1] - 1)) != 0)

    state = tile_1 + 2 * tile_2 + 4 * tile_3 + 8 * tile_4 + 16 * tile_5 + 32 * tile_6 + 64 * tile_7 + 128 * tile_8

    tile = get_tile_from_state(state)

    return rules[tile_to_rule_index[tile]]

def get_tile_from_state(state):
    if state in states:
        return states[state]
    return 15