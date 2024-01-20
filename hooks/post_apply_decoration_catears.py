# some of the models have a habit of adding cat ears
# even when they weren't asked for - speaks to the
# training set, I guess

# here, if cat ears weren't directly asked for, 
# they are negatively weighted out

def post_apply_decoration_catears_hook(shell, args):
    for ear_type in ['animal ears', 'dog ears', 'cat ears']:
        if ear_type not in shell['prompt']:
            shell['prompt'].merge({ear_type: -1})
    return shell
