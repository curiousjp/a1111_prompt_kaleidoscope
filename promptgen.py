#!/usr/bin/env python 
import json
import random
import copy
import glob
import argparse
import os.path

from common import PromptDict, MergeType, k_camera_angles, falloff_randint
from hooks import applyHooksFor
from scenarios import scenario_list
from decoration import decorate, decorateByName, applyDefaultDecorations

try:
    with open('config.json') as fh:
        config_store = json.load(fh)
except:
    config_store = {}

LARGE_NUMBER = config_store.get('large_number', 4294967294)
EMBEDDING_FOLDER = config_store.get('embed_path', '/mnt/sd/webui/embeddings/')

try:
    embeddings = [x.replace(EMBEDDING_FOLDER, '')[:-3] for x in glob.glob( f'{EMBEDDING_FOLDER}*.pt')]
except:
    embeddings = []

# prompting kaleidoscope
#  builds prompts from a dictionary files of weights and other functions.
#  there is only one prompt during the calculation stage - negative prompts are
#  generated post-hoc from terms with negative weights

# remember - the model, adetailer, hires, etc are to be set in the UI, not here

def merge_spec_with_preset_file(spec, preset_filename):
    with open(preset_filename) as file_handle:
        preset_dictionary = json.load(file_handle)
    for preset_key, preset_value in preset_dictionary.items():
        if type(preset_value) == dict:
            preset_value = PromptDict(preset_value)
        if preset_key not in spec or not isinstance(preset_value, PromptDict): 
            spec[preset_key] = preset_value
        elif preset_key == 'subjects':
            spec[preset_key].merge(preset_value, mode = MergeType.ADD)
        else:
            spec[preset_key].merge(preset_value)
    return spec

def stringify_weights(v):
    def format_term(t,w):
        t = t.replace("'", "")
        if t.startswith('lora:'):
            return f'<{t}:{w:.02f}>'
        elif w != 1:
            return f'({t}:{w:.02f})'
        else:
            return t
    return ', '.join([format_term(st,sw) for st,sw in v.items()])

def stringify_spec(spec, args):
    scenario_tag = ", ".join(spec.get('scenario_tag', ['unknown_scene']))
    if args.dump:
        acceptable_tags = ['prompt', 'negative_prompt']
    else:
        acceptable_tags = [
            'batch_size',
            'cfg_scale',
            'height',
            'n_iter',
            'negative_prompt',
            'prompt',
            'seed',
            'steps',
            'width',
        ]
    
    result = ''
    for spec_key, spec_value in spec.items():
        if spec_key not in acceptable_tags:
            continue
        if isinstance(spec_value, dict):
            spec_value = stringify_weights(spec_value)
        if spec_key == 'prompt':
            spec_value = f'[scenario_tag {scenario_tag}::-1] {spec_value}'
        if args.dump:
            result += f'\n{spec_value}\n'
        else:
            if isinstance(spec_value, str):
                spec_value = f'\'{spec_value}\''
            result += f'--{spec_key} {spec_value} '
    
    return result

def main(args):
    if args.rngseed != None:
        random.seed(args.rngseed)

    generation_spec_master = {
        'batch_size': args.batch_size,
        'n_iter': args.iterations,
        'steps': 20,
    }
    generation_spec_master['prompt'] = PromptDict()

    # include any forced terms
    if args.force_term:
        for forced_item in args.force_term:
            if ':' in forced_item:
                forced_term, forced_weight = forced_item.rsplit(':', 1)
            else:
                forced_term = forced_item
                forced_weight = 1
            forced_weight = float(forced_weight)
            generation_spec_master['prompt'].merge({forced_term: forced_weight})

    # load merge in any provided json presets
    for preset in args.presets:
        generation_spec_master = merge_spec_with_preset_file(generation_spec_master, preset)

    seed = args.seed if args.seed != -1 else random.randint(1, LARGE_NUMBER)
    seed_step = args.step if args.step != 0 else random.randint(1,LARGE_NUMBER//7)

    for generation_index in range(args.generations):
        # local copy
        generation_spec = copy.deepcopy(generation_spec_master)
        generation_spec = applyHooksFor(generation_spec, 'post_gs_init', args)

        # if we have rotating presets, apply them
        if args.rotator:
            selected_rotator = args.rotator[generation_index % len(args.rotator)]
            generation_spec = merge_spec_with_preset_file(generation_spec, selected_rotator)
        generation_spec = applyHooksFor(generation_spec, 'post_apply_rotators', args)

        # apply _scenario_rate_ number of scenarios from the pool
        if args.scenario_pool:
            scenario_choices = [f for n, f in scenario_list.items() if n in args.scenario_pool]
        else:
            scenario_choices = list(scenario_list.values())
        for scenario_function in random.sample(scenario_choices, args.scenario_rate):
            generation_spec = scenario_function(generation_spec)
        generation_spec = applyHooksFor(generation_spec, 'post_apply_scenario', args)

        # if there is a known camera angle present in the prompt, use it to set the outer camera
        for angle in k_camera_angles:
            # angles in prompt overwrite external setting
            if generation_spec['prompt'].get(angle, 0) > 0:
                generation_spec['camera'] = angle
        # if the outer camera is still not set, choose at random
        if 'camera' not in generation_spec:
            generation_spec['camera'] = random.choice(k_camera_angles)
        # reintroduce the camera into the prompt (I know this is odd)
        generation_spec['prompt'].merge({generation_spec['camera']: 1}, mode = MergeType.REPLACE)
        generation_spec = applyHooksFor(generation_spec, 'post_apply_camera', args)

        # apply the default decoration package
        generation_spec = applyDefaultDecorations(generation_spec)
        # add decorations, reducing the weight exponentially as we go
        for decoration_index in range(args.decoration_rate + generation_spec.get('bonus_decorations', 0)):
            decoration_weight = pow(0.8, decoration_index)
            generation_spec = decorate(generation_spec, decoration_weight)
        # additional decorations can be forced by name
        for forced_decoration in args.decorate_by_name:
            if ':' in forced_decoration:
                forced_term, forced_weight = forced_decoration.rsplit(':', 1)
            else:
                forced_term = forced_decoration
                forced_weight = 1
            forced_weight = float(forced_weight)
            generation_spec = decorateByName(generation_spec, forced_term, forced_weight)
        generation_spec = applyHooksFor(generation_spec, 'post_apply_decoration', args)

        # subject management
        if 'subjects' not in generation_spec:
            generation_spec['subjects'] = {'girl': falloff_randint(1,3), 'boy': falloff_randint(0,2)}
        headcount = sum(generation_spec['subjects'].values())
        subject_prompts = {}
        if headcount > 1:
            subject_prompts['multiple people'] = 1
        else:
            subject_prompts['solo'] = 1
            subject_prompts['solo focus'] = 1
        if generation_spec['subjects'].get('girl', 0) > 1:
            subject_prompts['multiple girls'] = 1
        if generation_spec['subjects'].get('boy', 0) > 1:
            subject_prompts['multiple boys'] = 1
        if generation_spec['subjects'].get('girl', 0) == generation_spec['subjects'].get('boy', 0):
            subject_prompts['couple'] = 1
        
        for subject_key, subject_value in generation_spec['subjects'].items():
            if subject_value == 0:
                continue
            sub_value_str = str(subject_value) if subject_value < 6 else '6+'
            sub_key_str = f'{sub_value_str}{subject_key}' if subject_value == 1 else f'{sub_value_str}{subject_key}s'
            subject_prompts[sub_key_str] = 1.5
        if headcount == 1:
            generation_spec['prompt'].merge({'looking at viewer': 1})
        else:
            generation_spec['prompt'].merge({'looking at another': 1})
        generation_spec = applyHooksFor(generation_spec, 'post_apply_subject_management', args)

        # heat on positive terms
        if args.heat > 0:
            generation_spec['prompt'].heat(args.heat)
        generation_spec = applyHooksFor(generation_spec, 'post_apply_heat', args)

        # prompt degrade if applicable
        if args.degrade_prompt != 1:
            positive_terms = list(generation_spec['prompt'].keys())
            terms_to_remove = int(len(positive_terms) * args.degrade_prompt)
            for deleted_term in random.sample(positive_terms, terms_to_remove):
                del(generation_spec['prompt'][deleted_term])
        generation_spec = applyHooksFor(generation_spec, 'post_apply_degrade', args)

        # reordering - try and frontload the subject stuff, 
        # do any shuffling, or drop out the zero weight terms at the same time
        positive_prompt = PromptDict(subject_prompts)
        negative_prompt = PromptDict({})
        current_keys = list(generation_spec['prompt'].keys())
        if args.shuffle_prompt:
            random.shuffle(current_keys)
        for key in current_keys:
            val = generation_spec['prompt'].get(key, 0)
            # drop loras without 'XL' in them if xlsafe is turned on
            if args.xlsafe and key.startswith('lora:') and 'XL' not in key:
                continue
            if val > 0:
                positive_prompt.merge({key:val}, mode = MergeType.BLEND)
            elif val < 0:
                negative_prompt.merge({key:-val}, mode = MergeType.BLEND)
        generation_spec['prompt'] = positive_prompt
        generation_spec['negative_prompt'] = negative_prompt
        generation_spec = applyHooksFor(generation_spec, 'post_split_prompts', args)

        # weight caps for terms prone to overloading
        safeties = config_store.get('safeties', {})

        lora_pos = [x for x in generation_spec['prompt'].keys() if x.startswith('lora:')]
        lora_neg = [x for x in generation_spec['negative_prompt'].keys() if x.startswith('lora:')]

        embd_pos = [x for x in generation_spec['prompt'].keys() if x in embeddings]
        embd_neg = [x for x in generation_spec['negative_prompt'].keys() if x in embeddings]
        
        # first pass - deal with any individual strength caps on overloadable elements
        for overloadable_term in (lora_pos + embd_pos):
            generation_spec['prompt'][overloadable_term] = min(safeties.get(overloadable_term, 1.8), generation_spec['prompt'][overloadable_term])
        for overloadable_term in (lora_neg + embd_neg):
            generation_spec['negative_prompt'][overloadable_term] = min(safeties.get(overloadable_term, 1.8), generation_spec['negative_prompt'][overloadable_term])
        
        # second pass - cap cumulative strength for each group separately
        if args.lora_cap:
            def get_strength_multiplier(all_items, included_terms, cap_weight):
                total = sum([v for k, v in all_items.items() if k in included_terms])
                if total > cap_weight:
                    return cap_weight / total
                return 1.0
            multiplier = get_strength_multiplier(generation_spec['prompt'], lora_pos, args.lora_cap)
            for term in lora_pos:
                generation_spec['prompt'][term] *= multiplier
            multiplier = get_strength_multiplier(generation_spec['prompt'], embd_pos, args.lora_cap)
            for term in embd_pos:
                generation_spec['prompt'][term] *= multiplier
            multiplier = get_strength_multiplier(generation_spec['negative_prompt'], lora_neg, args.lora_cap)
            for term in lora_neg:
                generation_spec['negative_prompt'][term] *= multiplier
            multiplier = get_strength_multiplier(generation_spec['negative_prompt'], embd_neg, args.lora_cap)
            for term in embd_neg:
                generation_spec['negative_prompt'][term] *= multiplier

        # prompt dynamic compression
        if args.crush:
            maximum = max([abs(v) for k,v in generation_spec['prompt'].items()]) if generation_spec['prompt'] else 0
            if maximum > args.crush:
                multiplier = args.crush / maximum
                for k, v in generation_spec['prompt'].items():
                    generation_spec['prompt'][k] = v * multiplier
            maximum = max([abs(v) for k,v in generation_spec['negative_prompt'].items()]) if generation_spec['negative_prompt'] else 0
            if maximum > args.crush:
                multiplier = args.crush / maximum
                for k, v in generation_spec['negative_prompt'].items():
                    generation_spec['negative_prompt'][k] = v * multiplier

        generation_spec = applyHooksFor(generation_spec, 'post_weight_adjust', args)

        # pick a cfg value
        generation_spec['cfg_scale'] = random.randint(10,15)/2.0
        
        if args.fix_weights != None:
            generation_spec['prompt'] = {k:args.fix_weights for k,v in generation_spec['prompt'].items()}
            generation_spec['negative_prompt'] = {k:args.fix_weights for k,v in generation_spec['negative_prompt'].items()}

        for dwell_index in range(args.dwell):
            generation_spec['seed'] = seed
            if args.height_swizzle:
                prompt_height = generation_spec.get('height', 0)
                prompt_width = generation_spec.get('width', 0)
                short_edge, long_edge = sorted([prompt_height, prompt_width])
                base_edge = short_edge
                if short_edge == 0:
                    short_edge = config_store.get('short_dimension', 364)
                if long_edge == 0:
                    long_edge = config_store.get('long_dimension', 720)
                if base_edge == 0:
                    base_edge = config_store.get('base_dimension', 512)
                
                temporary_copy = copy.deepcopy(generation_spec)
                
                temporary_copy['height'] = base_edge
                temporary_copy['width'] = base_edge
                print(stringify_spec(temporary_copy, args))

                temporary_copy['height'] = long_edge
                temporary_copy['width'] = short_edge
                print(stringify_spec(temporary_copy, args))

                temporary_copy['height'] = short_edge
                temporary_copy['width'] = long_edge
                print(stringify_spec(temporary_copy, args))

                if args.mega:
                    mega_multiplier = config_store.get('mega_multiplier', 2.0)
                    temporary_copy['height'] = base_edge * mega_multiplier
                    temporary_copy['width'] = base_edge * mega_multiplier
                    print(stringify_spec(temporary_copy, args))
            else:
                print(stringify_spec(generation_spec, args))
            seed = (seed + seed_step) % LARGE_NUMBER

def is_valid_file(p, a):
    if not os.path.exists(a):
        p.error(f'file {a} does not exist!')
    else:
        return a

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('presets', nargs = '+', type = lambda x: is_valid_file(parser, x))
    parser.add_argument('--batch_size', nargs = '?', type = int, default = 1)
    parser.add_argument('--crush', nargs = '?', type = float, default = None)
    parser.add_argument('--decorate_by_name', nargs = '*', type = str, default = [])
    parser.add_argument('--decoration_rate', nargs = '?', type = int, default = 0)
    parser.add_argument('--degrade_prompt', nargs = '?', type = float, default = 1)
    parser.add_argument('--dump', default = False, action = 'store_true')
    parser.add_argument('--dwell', nargs = '?', type = int, default = 1)
    parser.add_argument('--fix_weights', nargs = '?', type = int, default = None)
    parser.add_argument('--force_term', nargs = '*', type = str)
    parser.add_argument('--generations', nargs = '?', type = int, default = 1)
    parser.add_argument('--heat', nargs = '?', type = float, default = 0)
    parser.add_argument('--height_swizzle', default = False, action = 'store_true')
    parser.add_argument('--iterations', nargs = '?', type = int, default = 1)
    parser.add_argument('--lora_cap', nargs = '?', type = float)
    parser.add_argument('--mega', default = False, action = 'store_true')
    parser.add_argument('--rngseed', nargs = '?', type = int, default = None)
    parser.add_argument('--rotator', nargs = '*', type = lambda x: is_valid_file(parser, x), default = [])
    parser.add_argument('--scenario_pool', nargs = '*', type = str)
    parser.add_argument('--scenario_rate', nargs = '?', type = int, default = 1)
    parser.add_argument('--seed', nargs = '?', type = int, default = -1)
    parser.add_argument('--shuffle_prompt', default = False, action = 'store_true')
    parser.add_argument('--step', nargs = '?', type = int, default = 0)
    parser.add_argument('--xlsafe', default = False, action = 'store_true')
    args = parser.parse_args()
    main(args)
