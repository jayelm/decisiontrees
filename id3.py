"""
Implements the ID3 algorithm for the construction of
decision trees.

"""

import dtree
import math


class ID3(dtree.DTree):

    def create_tree(self, parent_subset=None, parent=None, parent_value=None,
                    remaining=None):
        """
        Recursively create the decision tree with the specified subset
        and node positions. Sets the created tree to self.dtree.

        Args:
            parent_subset: the subset of the data of the parent
                to create decision nodes on (defaut None, which is interpreted
                as using entire CSV data). This is further filtered down in the
                body of the function
            parent: the parent of the node to be created (default None, which
                sets the root of the dtree).
            parent_value: the name of the value connecting the parent node and
                the current node (default None).

        """

        # Identify the subset of the data used in the igain calculation
        if parent_subset is None:
            subset = self.data
        else:
            subset = self.filter_subset(parent_subset,
                                        parent.label,
                                        parent_value)

        if remaining is None:
            remaining = self.attributes

        use_parent = False
        counts = self.attr_counts(subset, self.dependent)
        if not counts:
            # Nothing has been found for the given subset. We label the node
            # based on the parent subset instead. This triggers the elif block
            # below
            subset = parent_subset
            counts = self.attr_counts(subset, self.dependent)
            use_parent = True

        # If every element in the subset belongs to one dependent group, label
        # with that group.
        if len(counts) == 1:  # Only one value of self.dependent detected
            node = dtree.DTreeNode(
                label=counts.keys()[0],
                leaf=True,
                parent_value=parent_value
            )
        elif not remaining or use_parent:
            # If there are no remaining attributes, label with the most
            # common attribute in the subset.
            most_common = max(counts, key=lambda k: counts[k])
            node = dtree.DTreeNode(
                label=most_common,
                leaf=True,
                parent_value=parent_value,
                properties={'estimated': True}
            )
        else:
            # Calculate max information gain
            igains = []
            for attr in remaining:
                igains.append((attr, self.information_gain(subset, attr)))

            max_attr = max(igains, key=lambda a: a[1])

            # Create the decision tree node
            node = dtree.DTreeNode(
                max_attr[0],
                properties={'information_gain': max_attr[1]},
                parent_value=parent_value
            )

        if parent is None:
            # Set known order of attributes for dtree decisions
            self.set_attributes(self.attributes)
            self.root = node
        else:
            parent.add_child(node)

        if not node.leaf:  # Continue recursing
            # Remove the just used attribute from the remaining list
            new_remaining = remaining[:]
            new_remaining.remove(node.label)
            for value in self.values[node.label]:
                self.create_tree(
                    parent_subset=subset,
                    parent=node,
                    parent_value=value,
                    remaining=new_remaining
                )

    def information_gain(self, subset, attr):
        """
        Calculate possible information gain from splitting the given subset
        with the specified attribute.

        Args:
            subset: the subset with which to calculate information gain.
            attr: the attribute used to calculate information gain.
        Returns:
            A float of the total information gain from the given split.

        """
        gain = self.get_base_entropy(subset)
        counts = self.attr_counts(subset, attr)
        total = float(sum(counts.values()))  # Coerce to float for division
        for value in self.values[attr]:
            gain += -((counts[value]/total)*self.entropy(subset, attr, value))
        return gain

    def get_base_entropy(self, subset):
        """
        Get overall entropy of the subset based on the dependent variable.

        Note: Although the current implementation of this ID3 algorithm only
        supports binary dependent variables, the code for base entropy is
        written (with a for loop, instead of a binary choice) so that it may
        be easily expanded to multivariate calculations later.

        Args:
            subset: the subset with which to calculate base entropy.
        Returns:
            A float of the base entropy.

        """
        return self.entropy(subset, self.dependent, None, base=True)

    def entropy(self, subset, attr, value, base=False):
        """
        Calculate the entropy of the given attribute/value pair from the
        given subset.

        Args:
            subset: the subset with which to calculate entropy.
            attr: the attribute of the value.
            value: the value used in calculation.
            base: whether or not to calculate base entropy based solely on the
                dependent value (default False).

        Returns:
            A float of the entropy of the given value.

        """
        counts = self.value_counts(subset, attr, value, base)
        total = float(sum(counts.values()))  # Coerce to float division
        entropy = 0
        for dv in counts:  # For each dependent value
            proportion = counts[dv] / total
            entropy += -(proportion*math.log(proportion, 2))
        return entropy


if __name__ == '__main__':
    import argparse
    import pprint
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('training_file', type=argparse.FileType('r'),
                        help='name of the (training) .csv file')
    parser.add_argument('-t', '--testing_file', nargs='?', const=None,
                        default=False, type=argparse.FileType('r'),
                        help='name of the testing .csv file')
    parser.add_argument('-d', '--decide', action='store_true',
                        help='enter decision REPL for the given tree')
    parser.add_argument('-r', '--rules', action='store_true',
                        help='print out individual paths down the tree for'
                        'binary decisions')  # TODO: add CSV support

    args = parser.parse_args()
    if args.testing_file is None:
        sys.exit('id3.py: error: testing file not specified')

    id3 = ID3(args.training_file)
    id3.create_tree()
    print repr(id3)

    if args.rules:
        pprint.pprint(id3.rules(), width=400)

    if args.testing_file:
        id3.test_file(args.testing_file)

    if args.decide:
        id3.decision_repl()
