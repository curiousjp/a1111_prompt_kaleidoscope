import sys
import pathlib
this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

import decoration
from common import roll

def landscape_scenario(opo):
    opo['width'] = 640
    opo['height'] = 360

    opo = decoration.decorateByName(opo, 'decorations_Light', multiplier = 1)
    opo = decoration.decorateByName(opo, 'decorations_Settings', multiplier = 1.5)
    opo = decoration.decorateByName(opo, 'decorations_Settings', multiplier = 0.5)

    opo['prompt'].merge({'beautiful landscape': 1, 'no humans': 1})

    if 'flags' not in opo:
        opo['flags'] = {'receive_default_decorations': False}
    else:
        opo['flags']['receive_default_decorations'] = False

    if roll(5):
        opo['prompt'].merge({'night': 1, 'moon': 1})

    opo.setdefault('scenario_tag', []).append('landscape')
    return opo
