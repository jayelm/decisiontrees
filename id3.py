"""
Implements the ID3 algorithm for the construction of decision trees.

"""

import dtree
import csv
import math
from collections import Counter


class ID3(object):
    def __init__(self, filename):
        """
        Initialize the ID3 instance from the given filename by parsing CSV
        data and setting necessary attributes.

        Args:
            filename: relative or absolute filepath to CSV file. CSV must
            follow format specified in README.
        Returns:
            An ID3 instance ready for decision tree learning.

        """
        self.filename = filename
        self.dtree = None
        self.parse_csv()
        self.get_distinct_values()

    def create_tree(self, subset=None, parent=None, parent_value=None):
        """
        Recursively create the decision tree with the specified subset
        and node positions. Sets the created tree to self.dtree.

        Args:
            subset: the subset of the data to create decision nodes on
                (defaut None, which is interpreted as using entire CSV data).
            parent: the parent of the node to be created (default None, which
                sets the root of the dtree).
            parent_value: the name of the value connecting the parent node and
                the current node (default None).

        """

        # Identify the subset of the data used in the igain calculation
        if subset is None:
            subset = self.data
        else:
            subset = self.filter_subset(subset, parent.label, parent_value)

        counts = self.attr_counts(subset, self.dependent)
        # If every element in the subset belongs to one dependent group, label
        # with that group.
        if len(counts) == 1:  # Only one value of self.dependent detected
            node = dtree.DTree(
                label=counts.keys()[0],
                leaf=True,
                parent_value=parent_value
            )
        elif not self.remaining_attributes:
            # If there are no remaining attributes, label with the most
            # common attribute in the subset.
            most_common = max(counts, key=lambda k: counts[k])
            node = dtree.DTree(
                label=most_common,
                leaf=True,
                parent_value=parent_value
            )
        else:
            # Calculate max information gain
            igains = []
            for attr in self.remaining_attributes:
                igains.append((attr, self.information_gain(subset, attr)))

            max_attr = max(igains, key=lambda a: a[1])

            # Create the decision tree node
            node = dtree.DTree(
                max_attr[0],
                properties={'information_gain': max_attr[1]},
                parent_value=parent_value
            )

        if parent is None:
            # Set known order of attributes for dtree decisions
            node.set_attributes(self.attributes)
            self.dtree = node
        else:
            parent.add_child(node)

        if not node.leaf:  # Continue recursing
            for value in self.values[node.label]:
                self.create_tree(
                    subset=subset,
                    parent=node,
                    parent_value=value
                )

    def parse_csv(self, dependent_index=-1):
        """
        Set the object's attributes and data, where attributes is a list of
        attributes and data is an array of row dictionaries keyed by attribute.

        Also sets the dependent variable, which defaults to the last one. An
        option to change the position of this dependent variable has not yet
        been implemented.

        Args:
            dependent_index: the index to be specified as the dependent
                variable (default -1).
        Raises:
            NotImplementedError: If dependent_index is specified, since I
                haven't implemented that yet.

        """
        if dependent_index != -1:
            raise NotImplementedError

        with open(self.filename) as fin:
            reader = csv.reader(fin)
            attributes = reader.next()
            data = []
            for row in reader:
                row = dict(zip(attributes, row))
                data.append(row)

        self.dependent = attributes[dependent_index]
        self.attributes = [a for a in attributes if a != self.dependent]
        self.all_attributes = attributes
        self.data = data

    def get_distinct_values(self):
        """
        Get the distinct values for each attribute in the CSV data.

        Returns:
            A dictionary with attribute keys and set values corresponding to
            the unique items in each attribute.

        """
        values = {}
        for attr in self.all_attributes:  # Use all attributes because ugly
            values[attr] = set(r[attr] for r in self.data)
        self.values = values

    def filter_subset(self, subset, attr, value):
        """
        Filter a subset of CSV data further by selecting only the rows of
        subset which have the given attribute and value.

        Args:
            subset: the subset of the CSV data to filter upon.
            attr: the attribute of the value to filter upon.
            value: the value to filter upon.
        Returns:
            A list of the filtered rows according to the attribute and value.

        """
        return [r for r in subset if r[attr] == value]

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

    def value_counts(self, subset, attr, value, base=False):
        """
        Get the number of currences per value of the dependent variable when
        the given attribute is equal to the given value.

        FIXME: Can attr/value be eliminated??

        Args:
            subset: the subset with which to act upon.
            attr: the attribute of the value.
            value: the value with which to track counts.
            base: whether or not to calculate values based on the dependent
                value (default False).
        Returns:
            A Counter instance detailing the number of occurrences per
            dependent variable.

        """
        counts = Counter()
        for row in subset:
            if row[attr] == value or base:
                counts[row[self.dependent]] += 1
        return counts

    def attr_counts(self, subset, attr):
        """
        Get the number of occurrences per value of the given attribute

        Args:
            subset: the subset with which to act upon.
            attr: the selected attribute.
        Returns:
            A Counter instance detailing the number of occurrences per
            attribute value.

        """
        counts = Counter()
        for row in subset:
            counts[row[attr]] += 1
        return counts

    @property
    def distinct_values(self):
        """
        Returns a readable list of all values in the CSV data set.

        Returns:
            A flattened list of all distinct values.

        """
        values_list = []
        for s in self.values.values():
            for val in s:
                values_list.append(val)
        return values_list

    @property
    def remaining_attributes(self):
        """
        Return a list of remaining attributes that have not yet been used as
        decision nodes in the given tree.

        Returns:
            A list of unused attributes.

        """
        if self.dtree is None:
            return self.attributes
        return [a for a in self.attributes if a not in self.dtree.attributes]

    def __str__(self):
        """
        Return the filename of the ID3 instance, the dependent variable, and
        the string representation of the ID3 decision tree.

        """
        return "ID3 for {0}:\nDependent variable: {1}\n{2}".format(
            self.filename,
            self.dependent,
            self.dtree
        )

    def __repr__(self):
        """
        Return the filename of the ID3 instance and other useful diagnostics.

        """
        return ("ID3 for {0}:\nDependent variable: {1}\n{2}\nRows: {3}\n" +
                "Values: {4}\nBase Data Entropy: {5}").format(
            self.filename,
            self.dependent,
            repr(self.dtree),
            len(self.data),
            self.values,
            self.get_base_entropy(self.data)
        )


def decision_repl(id3):
    """
    An interactive REPL for making decisions based on the created decision
    tree.

    """
    print
    print ','.join("{{{0}}}".format(a) for a in id3.attributes)
    print "Decision tree REPL. Enter above parameters separated by commas,"
    print "no spaces between commas or brackets."
    while True:
        x = raw_input('> ').split(',')
        print "Decision for {0}:".format(x)
        try:
            print id3.dtree.decide(x)
        except Exception as e:
            print "Error with decision: {0}".format(e)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='name of the .csv file')
    parser.add_argument('-d', '--decide', action='store_true',
                        help='enter decision REPL for the given tree')
    args = parser.parse_args()

    id3 = ID3(args.filename)
    id3.create_tree()
    print repr(id3)

    if args.decide:
        print
        decision_repl(id3)
