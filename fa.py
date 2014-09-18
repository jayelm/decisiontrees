"""
Implements the Factorial Analysis algorithm for the construction of
decision trees.

"""

import dtree


class FactorialAnalysis(dtree.DTree):

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
            if max_attr[0] == 0:
                # No positive information gain. Select group with most
                # Attributes instead
                distinct_values = []
                for attr in remaining:
                    distinct_values.append(
                        (attr, self.remaining_distinct_values(subset, attr))
                    )
                max_attr = max(distinct_values, key=lambda a: a[1])
                properties = {'max_groups': max_attr[1]}
            else:
                # Use max_attr info gain
                properties = {'information_gain': max_attr[1]}

            # Create the decision tree node
            node = dtree.DTreeNode(
                max_attr[0],
                properties=properties,
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

    def remaining_distinct_values(self, subset, attr):
        return len(set(r[attr] for r in subset))

    def information_gain(self, subset, attr):
        """
        Calculate possible information gain from splitting the given subset
        with the specified attribute. For the factorial analysis algorithm,
        this ratio is the number of data rows which are members of an
        attribute/value pair where splitting the subset on that attribute/value
        pair results in a perfect classification of the dependent variable
        divided by the total number of rows in the subset.

        Args:
            subset: the subset with which to calculate information gain.
            attr: the attribute used to calculate information gain.
        Returns:
            A float of the total information gain from the given split.

        """
        perfect = 0.
        total = 0.
        for val in self.values[attr]:
            counts = self.value_counts(subset, attr, val)
            total += sum(counts.values())
            if len(counts) == 1:
                # Only one dependent value found; perfect classification
                perfect += counts.values()[0]
        counts = self.attr_counts
        return perfect / total


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
        sys.exit('factorial_analysis.py: error: testing file not specified')

    fa = FactorialAnalysis(args.training_file)
    fa.create_tree()

    if args.rules:
        pprint.pprint(fa.rules(), width=400)

    if args.testing_file:
        fa.test_file(args.testing_file)

    if args.decide:
        fa.decision_repl()
