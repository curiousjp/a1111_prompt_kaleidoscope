# a1111_prompt_kaleidoscope
a command line tool for the large-scale generation of prompts for stable diffusion checkpoints trained on booru style tags.

## overview
This program generates random prompts by combining JSON documents containing information about a proposed generation (called a 'generation shell'), running functions over this shell that represent 'scenarios', applying further but less state-oriented modifications known as 'decorations', and finally rendering the shell into a string compatible with a1111's 'prompts from file or textbox' script or my own [a1111_xyzabc](https://github.com/curiousjp/a1111_xyzabc). 'scenarios' and 'decorations' use a simple plug-in style architecture, and a hook system provides additional control.

The plug-in system revolves around dynamically loading python code and running the functions found within - you should never install a plugin unless you either wrote it yourself or you have read it from end to end and understand everything it does. There is no sandboxing unless you provide it yourself.

The ability to inspect the terms of the prompt as it is created and to carry out control flow decisions accordingly provides some advantages compared to existing wildcard solutions. A large number of additional options are also provided to further permute the generated prompts.

## example
```
$ python promptgen.py --generations 2 --lora_cap 1 json/default-scene.json json/sfw.json

--batch_size 1 --n_iter 1 --steps 20 --prompt '[scenario_tag place::-1] multiple people, couple, (1girl:1.50), (1boy:1.50), (sfw:1.50), (clothed:1.50), (dramatic lighting:1.50), (beautiful landscape:1.40), from above, (long hair:1.40), (train interior:1.40), (gothic:1.40), dramatic shadows, (semi-rimless eyewear:0.80), (glasses:0.80), looking at another' --width 512 --height 768 --negative_prompt '(nsfw:1.50), (nude:1.50), animal ears, dog ears, cat ears' --cfg_scale 7.0 --seed 1380731068

--batch_size 1 --n_iter 1 --steps 20 --prompt '[scenario_tag portrait::-1] solo, solo focus, (1girl:1.50), (sfw:1.50), (clothed:1.50), painting \(object\), (framed image:1.50), (portrait:1.50), front view, straight-on, (watercolor \(medium\):1.50), (short hair:1.40), (spacewalk:1.40), (sportswear:1.40), private club, (red-framed eyewear:0.80), (glasses:0.80), looking at viewer' --width 512 --height 768 --negative_prompt '(nsfw:1.50), (nude:1.50), animal ears, dog ears, cat ears' --cfg_scale 5.5 --seed 1174320052
```

Note the scenario_tag uses a1111's [prompt editing syntax](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features#prompt-editing) to allow metadata like `scenario_tag place` to be injected into the prompt (for ease of searching with things like [DiffusionToolkit](https://github.com/RupertAvery/DiffusionToolkit)) without also altering the generation itself. Following generation with `hiresfix`, `adetailer` and a model-appropriate a1111 style, the following two images were produced:

![Side by side examples.](README-sample.png)

## my recommendations
Despite all of the settings for weight permutation provided, I tend to just fix term weights at one, generating prompts with something like the following: `python promptgen.py --generations 10 --fix_weights 1 --lora_cap 2.0 --crush 1.3 chars/whatever.json`

However, all the command line arguments were created to address something I wanted at least once, so read on for more information.

## command line arguments
`promptgen` requires at least one json file to serve as the base for the generation (although it could in principle be empty). The other command line switches are optional.

### --batch_size
Controls the `batch_size` output flag, which allows for parallel generation when you have more VRAM available.

### --crush
Performs range compression across the prompt and negative prompt separately. With `--crush 1.4`, the maximum strength of each term in the prompt will be scaled to 1.4 - this may be a scale up or a scale down depending on your original strengths. Useful to protect against (or force) weight blowouts. The positive and negative prompts are scaled separately.

### --decorate_by_name
Will apply a decoration, for example, `decorations_Settings` to your shells. This is in addition to any other decorations mandated by a scenario or the decoration rate.

### --decoration_decay
When decorations are applied through the `--decoration_rate` argument or the `bonus_decorations` key in a scenario, you can have them applied in increasingly lower strengths by specifying a `decoration_decay` less than 1.0. For example, at 0.8 (the old default), the first of these decorations will receive a weight multiplier of 0.8, the second 0.64, then 0.51, etc (i.e. the strength of the *n*th decoration is `decoration_decay` raised to the *n*th power.)

### --decoration_rate
Sets the 'decoration rate', or how many random decorations are applied to each generation. The default is zero. This is in addition to any decorations mandated by a scenario, added to the `bonus_decorations` count by a scenario, or manually specified by the user with `--decorate_by_name`.

### --degrade_prompt
Deletes a random fraction of prompt terms from the positive prompt only. At `--degrade_prompt 0.5`, 50% of terms will be deleted. Will not touch terms created from the 'subjects' dictionary as these are not integrated into the positive prompt until after this change is made - for more information see the discussion on 'scenarios' below.

### --dump
Provides simplified output more suited to copying and pasting directly into the UI.

### --dwell
Generates additional batch generation output for each shell, iterating the random seed if required. See also `--iterations` - this allows for larger seed steps if desired.

### --fix_weights
Overrides the weights of the generated prompt (including subject weights). Usually done with `--fix_weights 1.0` to produce neater output. Designed as a testing feature, has become part of my standard workflow. Weights are fixed before lora and embed strength capping takes place, before forced terms are injected, and before crushing is applied, so these features are still respected.

### --force_term
Manually injects a term into the prompt - this is done after scenarios, decoration, weight fixing, heat, degrade etc, but before lora and embed strength capping and crushing. Can either be a bare term, `--force_term moon` or a term and weight, `--force_term moon:0.5`.

### --generation
The number of shells to generate.

### --heat
Randomly perturbs term weights in the prompt. With a heat of 0.2, the weight of each term is multiplied by a random number between 0.8 and 1.2.

### --height_swizzle
Will force the height and weight for the image in the resulting output, and then create three variants for each shell - one square (default 512x512), one portrait (364x720), one landscape (720x364). These sizes can be overridden by setting the `base_dimension`, `long_dimension`, and `short_dimension` keys in 'config.json'.  See also the related switch, `--mega`.

### --iterations
Directly controls the `n_iter` value in the resulting output, causing a1111 to generate successive images, iterating the seed by one for each. See also `--dwell`.

### --lora_cap
Provides a similar mechanism to `--crush`, but only applied to terms at risk of overloading and blowing out the result - LORA and embeddings. When it is enabled, the total weight of all overloadable terms in the positive and negative terms (separately) are calculated and then scaled to fall under this value.

As an example, a positive prompt containing `lora:1.6` and `embedding:0.8` and subject to a `--lora_cap 1.2` will be modified to contain `lora:0.8` and `embedding:0.4`. A positive prompt containing `lora:1.0` and `embedding:0.1` would be unchanged. The same procedure would be carried out on the negative prompt separately.

Embeddings are detected by setting the `embed_path` key to your embeddings folder in 'config.json', or by prefacing the term with `embed:`.

Overloadable terms are also subject to another, separate capping mechanism that runs before `--lora_cap` and regardless of whether or not it is enabled - no identified LORA or embedding is allowed to exceed an immediate strength of 1.8 or whatever strength is set for it by a `safeties` dictionary key inside 'config.json'.

### --mega
Only active if `--height_swizzle` is enabled, this will create one additional picture with a width and height of the `base_dimension` multiplied by the `mega_multiplier` from 'config.json' (default 2.0).

### --rngseed
Seeds the random number generator for the entire execution - can be used to generate consistent prompt sets with different values for `--lora_cap`, `--xlsafe` etc.

### --rotator
Allows you to provide multiple json files that will be rotated through as generations are created.

### --scenario_pool
Lets you limit the available scenarios for generation.

### --scenario_rate
Allows for multiple scenarios to be applied to a single shell. Almost never what you want, unless what you want is chaos.

### --selection_decay
An experimental (but enabled by default!) feature to force your generations to explore more of the decoration space - if this is set to a value less than 1.0 (and the new default is 0.2), each time a decoration endpoint is selected, its weight in the decoration is multiplied down by this value. Because of the way that decorations are nested, this also impacts any parent decorations that were traversed to get to the selected endpoint.

The changes to weights persist until the end of the program execution, so subsequent generations in the same run are less likely to select the previously selected decorations. This should promote more varied prompts per run.

### --shuffle_prompt
Will shuffle your prompt keys (negative and positive) but not the subject keys.

### --step
The amount added to the random seed at each shell / dwell step. If left blank will choose something random and generally large.

### --xlsafe
If turned on, will remove any lora terms from the generated prompt prior to output unless they contain 'XL' in their names. A hedge to stop me trying to load SD1.5 lora against SDXL.

## scenarios
Scenarios are functions that receive a shell, modify it, and return it. The name of a scenario function must end with _scenario, and they should be placed in python files in the 'scenarios/' directory.

 A sample is provided in 'scenarios/place.py', and will provide a good template for further experimentation.

 ```py
## boilerplate to provide access to the common library
import sys
import pathlib
this_path = pathlib.Path(__file__)
sys.path.append(str(this_path.parent.parent))

import decoration
from common import falloff_randint, roll
## #####################################################

def place_scenario(opo):
    opo = decoration.decorateByName(opo, 'decorations_Light', multiplier = 1.5)
    opo['subjects'] = {'girl': falloff_randint(1,3), 'boy': falloff_randint(0,2)}
    opo['prompt'].merge({'beautiful landscape': 1.4})
    if roll(5):
        opo['prompt'].merge({'night': 1})
    opo['bonus_decorations'] = opo.get('bonus_decorations', 0) + 2
    opo.setdefault('scenario_tag', []).append('place')
    return opo
 ```

Key elements of the shell object to consider modifying include:

* 'subjects', a dictionary listing the number and type of subjects in the scene. This is later interpreted by the 'subject management' section of the main program, converted into relevant tags, and injected into the prompts. Subject Management will provide a default if the 'subject' key is missing from the shell.

* `falloff_randint(x, y, z = 0.5)` generates a random integer between `x` and `y`, but with the chances of each number being picked being `z` times the previous one - `falloff_randint(0,2,0.5)` has term weightings of {0: 1, 1: 0.5, 2: 0.25}.

* 'prompt' and 'negative_prompt' - not dictionaries, but a subclass of them that provides a 'merge' method that allows key weights to be blended together instead of simply replaced as done by `.update()`.  Add lora to prompts by using the 'lora:' prefix, e.g. `opo['prompt'].merge({'lora:fantasyV1.1': 0.6, 'fantasy': 1})`.

* 'bonus_decorations' allows additional random decorations to be added to the prompt at the end of shell generation process.

* `roll` is a function defined in the common library. `roll(x)` generates a random number between 1 and `x`, and returns true if the result was 1, false otherwise - it can be used to simulate 'one in x' chances. 

* 'bonus_decorations' means the decoration root object (see below) will be asked to provide an additional two random decorations to this shell.

* 'scenario_tag' is used to build the non-rendered metadata at the start of the prompt.

There are other meaningful keys on the shell object, including keys relating to 'camera angle' and so on. See the text of the main program for more information.

## decorations
Decorations are instances of a specific class, `DecorationNode` or its inheritors, that contain a variety of sub-objects. When a decoration is `select()`ed, it chooses one of its sub-objects and returns it.

`DecorationNode`s can be nested together, and generally, when the program wants to decorate a shell, it requests that a specific single object known as the 'root' provide a selection - but scenarios or hooks might request decorations by their names, and so on. 

The sub-objects of a `DecorationNode` can be weighted (by specifying them as 2-tuples with the weight as the second term.) The root starts with a minimal example decoration object, 'decorations_Light', that uses this weighting system.

When the decoration system comes online, it scans the 'decoration/' folder for other python files, and then loads them as modules and extracts objects that are instances of `DecorationNode` and registers them as a list. Decorations that nominated themselves as default decorations (via the `is_default` argument to their constructor) will thereafter be applied to any shell passing through the decoration system (use sparingly), and those that specified a `root_weight` in their constructor will be added as sub-items of the root with the designated weighting.

The constructor of a `DecorationNode` can also accept an additional argument, a dictionary known as `basis_dict`. During the final stage of returning the value from `select()`, the `basis_dict` is combined (via `update()`) with the result. This can save typing if all of the sub-items in the node have common terms, for example, you might add a basis dictionary of {'lips': 0.25, 'lipstick': 0.25} to a `DecorationNode` dealing with various lipstick colours.

## hooks
Like scenarios, hooks are functions contained within loose python files, in this case contained within 'hooks/'. An example is provided - `post_apply_decoration_catears_hook` - hooks receive the shell as their first argument, and the program's overall arguments as their second. It returns the modified shell. 

Hook function names must end with `_hook`, and the beginning of their names determine when they are run. The current hook timing names are:

* `post_gs_init`
* `post_apply_rotators`
* `post_apply_scenario`
* `post_apply_camera`
* `post_apply_decoration`
* `post_apply_subject_management`
* `post_apply_heat`
* `post_apply_degrade`
* `post_split_prompts`
* `post_weight_adjust`

If you want to use the hook system, you really need to read the main program code to get a sense of what each of these points represents.