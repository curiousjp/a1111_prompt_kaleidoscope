import sys
import pathlib
import random
this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

from common import roll

def portrait_scenario(opo):
    opo['subjects'] = {'girl': 1} if roll(2) else {'boy': 1}

    opo['prompt'].merge(
        {'painting \\(object\\)': 1},
        {'framed image': 1.5},
        {'portrait': 1.5},
    )

    if roll(2):
        opo['prompt'].merge(
            {'front view': 1},
            {'straight-on': 1},
        )
    else:
        opo['prompt'].merge(
            {'from side': 1},
        )

    media = [
        'photo', 
        'painting', 
        'marker', 
        'graphite', 
        'watercolor', 
        'colored pencil', 
        'poster', 
        'watercolor pencil', 
        'calligraphy brush', 
        'ink', 
        'pastel', 
        'oil painting', 
        'brush', 
        'gouache', 
        'charcoal'
    ]

    opo['prompt'].merge({f'{random.choice(media)} \\(medium\\)': 1.5})
    opo['bonus_decorations'] = opo.get('bonus_decorations', 0) + 2
    opo.setdefault('scenario_tag', []).append('portrait')
    return opo
