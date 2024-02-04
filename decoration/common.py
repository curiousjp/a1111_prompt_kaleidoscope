import random

class DecorationNode:
    def __init__(self, children, basis_dict = {}, is_default = False, root_weight = None):
        child_topics = []
        weights = []
        for item in children:
            if type(item) == tuple:
                child_topics.append(item[0])
                weights.append(item[1])
            else:
                child_topics.append(item)
                weights.append(1)
        self._children = child_topics
        self._weights = weights
        self._basis = basis_dict
        self._is_default = is_default
        self._root_weight = root_weight
    
    @property
    def default(self):
        return self._is_default
    
    @property
    def desired_root_weight(self):
        return self._root_weight
    
    def add_child(self, new_child, new_weight = 1):
        self._children.append(new_child)
        self._weights.append(new_weight)

    def select(self, selection_decay = 1.0):
        selection = random.choices(self._children, weights = self._weights, k = 1)[0]
        selection_index = self._children.index(selection)
        self._weights[selection_index] *= selection_decay
        if isinstance(selection, DecorationNode):
            value = selection.select()
        else:
            value = dict(selection)
        value.update(self._basis)
        return value
