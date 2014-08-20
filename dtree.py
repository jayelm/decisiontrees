"""
Implements a decision tree class, to be used in decision tree construction
algorithms.

"""


class DTree(object):
    """
    A recursively defined decision tree.

    """

    def __init__(self, attribute, parent_value=None, information_gain=None, leaf=False):
        # FIXME figure out good class design, keep attributes protected
        self.attribute = attribute
        self.children = []
        self.parent_value = parent_value
        self.information_gain = information_gain
        self.leaf = leaf

    def add_child(self, node):
        self.children.append(node)

    @property
    def num_children(self):
        return len(self.children)

    @property
    def attributes(self):
        attributes = [self.attribute]
        for node in self.children:
            attributes.extend(node.attributes)
        return attributes

    def __str__(self):
        s = "{0} -- ({1}, {2})".format(
            str(self.parent_value),
            str(self.attribute),
            ', '.join(str(c) for c in self.children)
        )
        return s








