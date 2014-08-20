# decisiontrees

Implementations of decision tree construction algorithms, done during my time
at GUCAS Beijing.

## Usage

The source code is well documented, so don't be afraid to poke around in the
files for more information on functionality.

### id3.py

With a CSV file `filename.csv` (see `example_data` for formatting), the
following creates a decision tree using the [ID3](http://en.wikipedia.org/wiki/ID3_algorithm)
algorithm and enters a REPL loop where decisions can be made with by inputting
attribute values:

    python id3.py filename.csv --decide

The decision rules for the decision tree can also be printed with the `--rules` flag.

Learning from testing and training sets is also supported. Try this as test data:

    python id3.py example_data/breast-cancer-training.csv -t example_data/breast-cancer-testing.csv

Support for outputting testing set predictions to CSV will be added soon.

See `python id3.py --help` for more details.

### dtree.py

A very simple recursively defined class used to represent decision trees.

### example_data

Has a couple of data sets of varying complexity. Breast cancer data taken from [UCI Machine Learning](http://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/) and modified to fit script requirements.

## Todo

Class abstraction and encapsulation needs to be improved.
