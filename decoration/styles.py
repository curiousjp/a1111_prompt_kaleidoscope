import sys
import pathlib
this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

from decoration.common import DecorationNode

decorations_Styles = DecorationNode(
    [
        {'cool': 1},
        {'emo': 1},
        {'formal': 1},
        {'futuristic': 1},
        {'gothic lolita': 1},
        {'gothic': 1},
        {'military': 1, 'camoflage': 1},
        {'punk': 1},
        {'sportswear': 1},
        {'uniform': 1},
        {'victorian': 1},
    ],
    is_default = True,
    root_weight = 1
)
