import sys
import pathlib
this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

import decoration
from common import falloff_randint, roll

def place_scenario(opo):
    opo = decoration.decorateByName(opo, 'decorations_Light', multiplier = 1.5)
    opo['subjects'] = {'girl': falloff_randint(1,3), 'boy': falloff_randint(0,2)}
    opo['prompt'].merge({'beautiful landscape': 1.4})
    if roll(5):
        opo['prompt'].merge({'night': 1})
    opo['bonus_decorations'] = opo.get('bonus_decorations', 0) + 2
    opo.setdefault('scenario_tag', []).append('place')
    return opo
