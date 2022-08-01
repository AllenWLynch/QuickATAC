
from quickatac.base import enforce_string, add_default_input, add_default_output

####
# A "tool" has a main "tool function" which takes all the requisite parameters
# and performs the tool's task in entirety. This function is intended to be imported
# or used directly by other python code.
# Fragment files (and all other types of files) should be passed to the 
# function as opened filetype objects/iterators.
# The function must not write results, but yield them. This keeps IO operations 
# separate from the functions of the tool itself, making the tool more
# flexible and portable.
####
def label_fragments(fragment_stream, prefix):

    for fragment in map(enforce_string, fragment_stream):

        if not fragment[0] == '#': # skip commented lines

            line = fragment.strip().split('\t')
            assert(len(line) >= 4)
            
            barcode = line[3]

            barcode = '{batch}:{barcode}'.format(
                batch = str(prefix), barcode = barcode
            )

            yield '\t'.join(                        # Yield
                [*line[:3], barcode, *line[4:]]     # the
            )                                       # result


#####
# The next function that must be defined is "add_arguments", which
# takes an argparse parser (pass from cli.py) as the parameter. 
# This function specifies the CLI for this tool. The "add_default_input"
# function adds the argument for the fragment file input, and the 
# "add_default_output" function adds an argument for "--outfile",
# which defaults to stdin.
#####
def add_arguments(parser):

    add_default_input(parser)
    parser.add_argument('--prefix', '-p', type = str, required = True)
    add_default_output(parser)


#####
# Finally, a tool must implement the "main" function, which takes arguments
# parsed from the CLI specified above and specifies how the inputs are 
# recieved by the tool function, and how results from the tool function
# are written. 
#####
def main(args):

    for line_out in label_fragments(
        args.fragments, args.prefix
    ):
        args.outfile.write(line_out + '\n')