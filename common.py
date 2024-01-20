import random
import enum

simple_colours = ['black', 'blue', 'brown', 'cyan', 'green', 'grey', 'orange', 'pink', 'purple', 'red', 'violet', 'white', 'yellow', 'gold', 'platinum', 'silver', 'multicolor', 'rainbow']
k_camera_angles = ['cowboy shot', 'dutch angle', 'from above', 'from behind', 'from below', 'from side', 'front view', 'pov']

class MergeType(enum.Enum):
    BLEND = 1
    ADD = 2
    REPLACE = 3

class PromptDict(dict):
    def merge(self, *new, mode = MergeType.BLEND):
        for new_instance in new:
            for key, value in new_instance.items():
                match mode:
                    case MergeType.REPLACE:
                        self[key] = value
                    case MergeType.ADD:
                        self[key] = self.get(key, 0) + value
                    case MergeType.BLEND:
                        if key not in self.keys():
                            self[key] = value
                        else:
                            old_value = self.get(key, 0)
                            
                            # there are a few negative defaults that, in some circumstances,
                            # we just want to replace instead of doing a weighting between 
                            # them - for example, the drp "animal ears" negative.. so where
                            # a positive is BLENDed over a negative like that, there's a case
                            # to be made for just replacing it outright...
                            if old_value < 0 and value > 0:
                                self[key] = value
                                continue
                            
                            # otherwise,
                            # we don't want multiple common keys to blow out prompt
                            # weights, so we cap how much each addition can shift the needle
                            intensity_cap = max(abs(old_value) * 1.1, abs(value) * 1.1)
                            new_value = old_value + value
                            if abs(new_value) > intensity_cap:
                                new_value = intensity_cap if new_value > 0 else -intensity_cap
                            self[key] = new_value
        return self
    
    def heat(self, h):
        for k, v in self.items():
            if not isinstance(v, float) or v <= 0:
                continue
            self[k] = v * random.uniform(1-h, 1+h)

def merge_weight_keys(old, *new):
    result = dict(old)
    for new_instance in new:
        for key, value in new_instance.items():
            if key not in result:
                result[key] = value
                continue
            old_value = result[key]
            intensity_cap = max(abs(old_value) * 1.1, abs(value) * 1.1)
            new_value = old_value + value
            if abs(new_value) > intensity_cap:
                new_value = intensity_cap if new_value > 0 else -intensity_cap
            result[key] = new_value
    return result 

def additive_merge(old, *new):
    result = dict(old)
    for new_instance in new:
        for key, value in new_instance.items():
            result[key] = result.get(key,0) + value
    return result 

def select_from_choices(choices, w = 1):
    selected = random.choice(choices)
    if type(selected) == list:
        return {k:w for k in selected}        
    return {selected: w}

def roll(n):
    return (random.randint(1,n) == 1)

def falloff_randint(x,y, falloff = 0.5):
    choices = list(range(x,y+1))
    weights = [1*pow(falloff,idx) for idx in range(len(choices))]
    return random.choices(population = choices, weights = weights, k = 1)[0]