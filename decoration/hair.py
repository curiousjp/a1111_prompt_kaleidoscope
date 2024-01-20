import sys
import pathlib
this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

from common import simple_colours
from decoration.common import DecorationNode

decorations_Hair = DecorationNode(
    [
        DecorationNode([
            {'absurdly long hair': 1},
            ({'bald': 1}, 0.1),
            {'braids': 1},
            {'buzz cut': 1},
            {'hair over eye': 1},
            {'long hair': 1},
            {'pixie cut': 1},
            {'short hair': 1},
            {'twintails': 1},
            {'very long hair': 1},
            {'very short hair': 1}
        ])
    ],
    is_default = True,
    root_weight = 1
)
