import sys
import pathlib
this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

from decoration.common import DecorationNode

decorations_Glasses = DecorationNode(
    [
        {'black-framed eyewear': 1}, 
        {'blue-framed eyewear': 1},
        {'eyewear on head': 1}, 
        {'heart-shaped eyewear': 1}, 
        {'opaque glasses': 1}, 
        {'red-framed eyewear': 1}, 
        {'rimless eyewear': 1}, 
        {'round eyewear': 1}, 
        {'semi-rimless eyewear': 1},
        {'sunglasses': 1},
        {'under-rim eyewear': 1}, 
    ],
    basis_dict = {'glasses': 1}
)

decorations_MiscEyewear = DecorationNode(
    [
        {'covered eyes': 1},
        {'goggles': 1},
        {'head-mounted display': 1},
        {'mask': 1},
        {'visor': 1},
    ]
)

decorations_Eyewear = DecorationNode(
    [
        (decorations_Glasses, 4),
        (decorations_MiscEyewear, 1),
    ],
    root_weight = 1
)
