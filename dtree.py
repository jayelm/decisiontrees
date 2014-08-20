"""
Implements a basic decision tree class, to be used in decision tree
construction algorithms.

"""


class DTree(object):
    """
    A recursively defined decision tree.

    """

    def __init__(self, label, parent_value=None, properties={}, leaf=False):
        """
        Initialize a decision tree node.

        Args:
            label: the label of the node, which can either be a decision
                attribute or a leaf result.
            parent_value: the name of the link from the current node to its
                parent (default None, used in cases of root nodes).
            properties: a dictionary containing various diagnostic properties
                of the given node (e.g. information gain or entropy) (default
                empty dictionary).
            leaf: a boolean indicating whether or not this node is a leaf node
                (default False).
        """
        self.label = label
        self.children = []
        self.parent_value = parent_value
        self.properties = properties
        self.leaf = leaf

    def plot(self, x=1, y=1):
        """
        Recursively plot the given node and its children with matplotlib

        Args:
            x: the desired width of the plot (default 1).
            y: the desired height of the plot (default 1).
        Raises:
            NotImplementedError: Not yet implemented.

        """
        raise NotImplementedError

    def _plot(self, xoffset, yoffset):
        """
        Plot the given node at the xoffset and yoffset coordinates.

        Args:
            xoffset: the x coordinate for plotting of the given node.
            yoffset: the y coordinate for plotting of the given node.
        Raises:
            NotImplementedError: Not yet implemented.

        """
        raise NotImplementedError

    def set_attributes(self, attributes):
        """
        Set the correct order of the attributes in the decision tree
        based on the parsed CSV data.

        Args:
            attributes: the correctly ordered list of independent attributes
                from the CSV data.

        """
        self.attribute_order = attributes

    def decide(self, attributes):
        """
        Make a decision on the dependent variable of the tree given the
        provided attributes.

        Args:
            attributes: the list of independent attributes, correctly ordered,
                with which to make a decision on the dependent value.
        Returns:
            A dependent variable representing the decision tree decision.
        Raises:
            ValueError: if an invalid property is found which is not
                represented in the decision tree.

        """
        if len(attributes) != len(self.attribute_order):
            print self.attribute_order
            raise ValueError("supplied attributes do not match data")
        attrs_dict = dict(zip(self.attribute_order, attributes))
        return self._decide(attrs_dict)

    def _decide(self, attrs_dict):
        """
        Recursively decide using the given attribute/value dictionary.

        Internal function is separated from the more friendly decide() method.

        """
        if self.leaf:
            return self.label
        val = attrs_dict[self.label]
        for node in self.children:
            if val == node.parent_value:
                # FIXME
                # if 'estimated' in node.properties:
                    # return False
                return node._decide(attrs_dict)
        raise ValueError("Invalid property found: {0}".format(val))

    def add_child(self, node):
        """
        Add the given child node to the list of children of the current node.

        Args:
            node: the DTree node to be appended as a child.

        """
        self.children.append(node)

    @property
    def num_leaves(self):
        """
        Return the total number of leaves that exist under the current node.

        Returns:
            An integer of the number of leaves.

        """
        if self.leaf:
            return 1
        else:
            return sum(c.num_leaves for c in self.children)

    @property
    def num_children(self):
        """
        Return the total number of immediate child nodes under the current
        node.

        Returns:
            An integer of the number of children.

        """
        return len(self.children)

    @property
    def depth(self):
        """
        Return the maximum depth of the tree assuming the current node
        as the parent.

        Returns:
            An integer calculated from the longest tree branch traversal.

        """
        return self._depth(0)

    def _depth(self, init):
        """
        Accumulate the depth of the tree at the given node taking into
        account the previous depth of the tree.

        init is the existing depth accumulated from previous levels of the
        tree.

        """
        if self.leaf:
            return init
        else:
            return max(c._depth(init+1) for c in self.children)

    @property
    def attributes(self):
        """
        Return all attributes used as decision nodes in the tree.

        Returns:
            A list of attribute names.

        """
        attributes = [self.label]
        for node in self.children:
            attributes.extend(node.attributes)
        return attributes

    def rules(self):
        """
        Return all of the node's tree branch traversals, which
        can be used as if/then rules for simulating the decision process.

        Returns:
            A 2d list of all known tree branch traversals.

        """
        return sorted(
            self._rules(),
            key=lambda t: (len(t), [p[1] for p in t if isinstance(p, tuple)])
        )

    def _rules(self, parent=None, previous=()):
        """
        Return a 2d list of decision rules with the given parent node and
        the tuple of previous nodes.

        """
        # import pdb; pdb.set_trace()
        rows = []
        if parent is not None:
            previous += ((parent.label, self.parent_value), )
        if self.leaf:
            previous += ((self.label), )
            rows.append(previous)
        else:
            for node in self.children:
                rows.extend(node._rules(self, previous))
        return rows

    def __str__(self):
        """
        Recursively build a string representation of the tree starting at the
        current node.

        """
        return "--{0}--({1}, {2})".format(
            self.parent_value,
            self.label,
            ', '.join(str(c) for c in self.children)
        )

    def __repr__(self):
        """
        Recursively build a string representation of the tree starting at the
        current node. Differs from __str__ by including additional diagnostic
        information.

        """
        return "--{0}--({1} {2}, {3})".format(
            self.parent_value,
            self.label,
            self.properties,
            ', '.join(repr(c) for c in self.children)
        )
