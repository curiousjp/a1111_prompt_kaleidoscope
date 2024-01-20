import sys
import pathlib
this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

from decoration.common import DecorationNode

decorations_Settings = DecorationNode(
    [
        {'apartment': 1},
        {'atelier': 1},
        {'aztec': 1},
        {'barn': 1},
        {'battlefield': 1},
        {'bedroom': 1},
        {'biopunk': 1},
        {'boardroom': 1},
        {'castle': 1},
        {'cave': 1},
        {'church':1},
        {'clearing': 1},
        {'clockpunk': 1, 'clockwork': 1},
        {'cramped interior': 1},
        {'cyberpunk': 1},
        {'cyberspace': 1},
        {'desert': 1},
        {'dieselpunk': 1},
        {'dungeon':1},
        {'dystopia': 1},
        {'elaborate starry background': 1},
        {'enchanted glade': 1},
        {'factory': 1},
        {'farm': 1},
        {'forest': 1},
        {'gothic': 1},
        {'grassland': 1},
        {'gym': 1},
        {'hell': 1},
        {'high fantasy':1}, 
        {'industrial':1, 'wires': 1, 'pipes': 1},
        {'inside': 1},
        {'kitchen': 1},
        {'laboratory':1},
        {'library': 1},
        {'living room': 1},
        {'low fantasy':1}, 
        {'magical':1},
        {'maze': 1},
        {'monastery': 1},
        {'mountainside': 1},
        {'office':1},
        {'onsen': 1},
        {'outdoors': 1},
        {'outer space':1},
        {'outside': 1},
        {'park':1},
        {'prarie': 1},
        {'private club': 1},
        {'public': 1},
        {'public bath': 1},
        {'ruins': 1},
        {'sauna': 1},
        {'science fiction':1}, 
        {'shop': 1},
        {'spaceship': 1},
        {'spaceship bridge': 1},
        {'spacestation': 1},
        {'spacewalk': 1},
        {'sports': 1},
        {'steampunk': 1, 'victorian': 1, 'gothic': 1},
        {'swamp': 1},
        {'temple': 1},
        {'theater': 1},
        {'train interior': 1},
        {'train station': 1},
        {'transformation pod': 1},
        {'tunnel': 1},
        {'underground': 1},
        {'underwater': 1},
        {'urban': 1}, 
        {'western': 1, 'cowgirl': 1, 'cowboy': 1},
        {'workshop': 1},
        {'zero gravity': 1},
    ],
    is_default = True,
    root_weight = 1
)
