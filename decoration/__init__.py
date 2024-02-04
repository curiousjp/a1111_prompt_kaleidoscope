import sys
import inspect
import pathlib
import importlib.util

this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

from common import simple_colours
from decoration.common import DecorationNode

## decorations

decoration_modules = [(x.stem, str(x)) for x in this_path.parent.glob('**/*.py') if x.is_file() and not x.stem.startswith('_')]
decoration_list = {}
for decoration_module_list in decoration_modules:
    mod_name, mod_path = decoration_module_list
    mod_spec = importlib.util.spec_from_file_location(mod_name, mod_path)
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    decoration_list.update({k: v for (k,v) in inspect.getmembers(mod, lambda x: isinstance(x, DecorationNode))})

decorations_Light = DecorationNode(
    [
        ({'rainbow': 1, 'colorful': 1, 'bright': 1, 'saturated colors': 1}, 1.2),
        {'bright':1},
        {'dark theme': 1},
        {'dramatic lighting': 1},
        {'dramatic shadows': 1},
        {'lora:add_detail': 1},
        {'sunshine': 1},
    ] + [({f'{c} theme':1},1/len(simple_colours)) for c in simple_colours] 
)
decoration_list.update({'decorations_Light': decorations_Light})

decoration_root = DecorationNode(
    [
        decorations_Light,
    ]
)

for decoration_name, decoration_object in decoration_list.items():
    if decoration_object.desired_root_weight:
        decoration_root.add_child(decoration_object, decoration_object.desired_root_weight)

def applyDefaultDecorations(generation_spec, multiplier = 1.3, selection_decay = 1.0):
    default_decorations = [v for v in decoration_list.values() if v.default]
    for default_decoration in default_decorations:
        generation_spec = decorateByObject(generation_spec, default_decoration, multiplier, selection_decay)
    return generation_spec

def decorateByObject(generation_spec, decorator, multiplier, selection_decay):
    decoration_pieces = {k:(v * multiplier) for k, v in decorator.select(selection_decay).items()}
    generation_spec['prompt'].merge(decoration_pieces)
    return generation_spec

def decorateByName(generation_spec, decoratorName, multiplier = 1, selection_decay = 1.0):
    decorator_object = decoration_list[decoratorName]
    return decorateByObject(generation_spec, decorator_object, multiplier, selection_decay)

def decorate(generation_spec, multiplier = 1, selection_decay = 1.0):
    return decorateByObject(generation_spec, decoration_root, multiplier, selection_decay)

__all__ = [applyDefaultDecorations, decorateByName, decorate]
