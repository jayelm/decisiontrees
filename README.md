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

That's currently pretty much all there is to it, where `--decide` is a flag
indicating REPL functionality. See `python id3.py --help` for more details.

### dtree.py

A very simple recursively defined class used to represent decision trees.

## Todo

Class abstraction and encapsulation needs to be improved.
