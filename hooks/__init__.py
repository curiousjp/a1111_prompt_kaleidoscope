import sys
import inspect
import pathlib
import importlib.util

this_path = pathlib.Path(__file__)

## hooks

hook_modules = [(x.stem, str(x)) for x in this_path.parent.glob('**/*.py') if x.is_file() and not x.stem.startswith('_')]

hook_list = {}
for hook_module_pair in hook_modules:
    mod_name, mod_path = hook_module_pair
    mod_spec = importlib.util.spec_from_file_location(mod_name, mod_path)
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    hook_list.update({k: v for (k,v) in inspect.getmembers(mod, inspect.isfunction) if k.endswith('_hook')})

def applyHooksFor(spec, hook_tag, args = None):
    matching_hooks = [x for x in hook_list.keys() if x.startswith(hook_tag)]
    for hook in matching_hooks:
        spec = hook_list[hook](spec, args)
    return spec

__all__ = [applyHooksFor]

