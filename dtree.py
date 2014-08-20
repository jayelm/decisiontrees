"""
Implements a decision tree class, to be used in decision tree construction
algorithms.

"""

# import matplotlib.pyplot as plt

# FIXME information_gain is (maybe) specific to ID3. Replace with properties
# dict, then when plotting, annotate all of those


class DTree(object):
    """
    A recursively defined decision tree.

    """
    decision_node = dict(boxstyle="sawtooth", fc="0.8")
    leaf_node = dict(boxstyle="round4", fc="0.8")
    arrow_args = dict(arrowstyle="<-")

    def __init__(self, attribute, parent_value=None,
                 information_gain=None, leaf=False,
                 attribute_order=[]):
        # FIXME figure out good class design, keep attributes protected
        self.attribute = attribute
        self.children = []
        self.parent_value = parent_value
        self.information_gain = information_gain
        self.leaf = leaf
        self.attribute_order = attribute_order

    def plot(self, x=1, y=1):
        """
        Recursively plot the given node and its children with matplotlib

        """
        raise NotImplementedError

    def set_attributes(self, attributes):
        self.attribute_order = attributes

    def decide(self, attributes):
        # import pdb; pdb.set_trace()
        if len(attributes) != len(self.attribute_order):
            print self.attribute_order
            raise ValueError("attributes supplied does not match data")
        attrs_dict = dict(zip(self.attribute_order, attributes))
        return self._decide(attrs_dict)

    def _decide(self, attrs_dict):
        if self.leaf:
            return self.attribute
        val = attrs_dict[self.attribute]
        for node in self.children:
            if val == node.parent_value:
                return node._decide(attrs_dict)
        raise Exception("Invalid property found: {0}".format(val))

    def _plot(self, xoffset, yoffset):
        raise NotImplementedError

    def add_child(self, node):
        self.children.append(node)

    @property
    def num_leaves(self):
        if self.leaf:
            return 1
        else:
            return sum(c.num_leaves for c in self.children)

    @property
    def num_children(self):
        return len(self.children)

    @property
    def depth(self):
        return self._depth(0)

    def _depth(self, init):
        if self.leaf:
            return init
        else:
            return max(c._depth(init+1) for c in self.children)

    @property
    def attributes(self):
        attributes = [self.attribute]
        for node in self.children:
            attributes.extend(node.attributes)
        return attributes

    def __str__(self):
        # TODO improve this string method
        s = "{0} -- ({1}, {2})".format(
            str(self.parent_value),
            str(self.attribute),
            ', '.join(str(c) for c in self.children)
        )
        return s
