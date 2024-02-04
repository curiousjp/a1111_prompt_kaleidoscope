import sys
import pathlib
this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

from common import simple_colours
from decoration.common import DecorationNode

decorations_Eyes = DecorationNode(
    [
        DecorationNode(
            [{f'{c} eyes':1} for c in simple_colours], basis_dict = {'lora:眼睛双': 1}
        ),
        DecorationNode(
            [{f'{c} eyes':1} for c in simple_colours]
        )
    ],
    is_default = True,
    root_weight = 1
)
