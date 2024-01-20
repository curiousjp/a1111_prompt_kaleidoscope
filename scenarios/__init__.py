import inspect
import pathlib
import importlib.util

this_path = pathlib.Path(__file__)

## scenarios

scenario_modules = [(x.stem, str(x)) for x in this_path.parent.glob('**/*.py') if x.is_file() and not x.stem.startswith('_')]

scenario_list = {}
for scenario_module_pair in scenario_modules:
    mod_name, mod_path = scenario_module_pair
    mod_spec = importlib.util.spec_from_file_location(mod_name, mod_path)
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    scenario_list.update({k: v for (k,v) in inspect.getmembers(mod, inspect.isfunction) if k.endswith('_scenario')})

__all__ = [scenario_list]

