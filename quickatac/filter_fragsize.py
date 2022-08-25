from typing import Type
from quickatac.base import enforce_string, add_default_input, add_default_output

def filter_fragsize(fragment_stream, min_size = 15, max_size = 294):

    assert isinstance(min_size, int) and isinstance(max_size, int)
    assert min_size < max_size

    for line_no, fragment in enumerate(map(enforce_string, fragment_stream)):

        if not fragment[0] == '#': # skip commented lines

            line = fragment.strip().split('\t')
            assert(len(line) >= 4)
            
            try:
                chr, start, end = str(line[0]), int(line[1]), int(line[2])
            except TypeError:
                raise ValueError(
                    'Line {} has invalid fragment record: {}'.format(
                        line_no, fragment
                    )
                )

            fraglen = end - start
            if min_size <= fraglen <= max_size:
                yield fragment.strip()

def add_arguments(parser):

    add_default_input(parser)
    parser.add_argument('--min-size', '-min', type = int, default = 15)
    parser.add_argument('--max-size', '-max', type = int, default = 297)
    add_default_output(parser)


def main(args):

    for fragment in filter_fragsize(
            args.fragments, 
            min_size = args.min_size,
            max_size = args.max_size,  
        ):

        args.outfile.write(fragment + '\n')