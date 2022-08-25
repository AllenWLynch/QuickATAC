from quickatac.base import enforce_string, OptionalGzipFiletype, add_default_output
from collections import Counter
import sys

def count_occurences(stream, column = -1, sep = '\t'):

    sink = Counter()

    assert isinstance(column, int)

    for line_no, line in enumerate(map(enforce_string, stream)):

        if not line[0] == '#': # skip commented lines
            
            collect_field = line
            if column > 0:
                try:
                    collect_field = line.strip().split(sep)[column - 1]
                except IndexError as err:
                    raise IndexError('Line {} does not have {} columns: {}'.format(
                        line_no, column, line
                    ))

            sink[collect_field]+=1

    return sink

def add_arguments(parser):

    parser.add_argument('infile', 
            nargs = '?', 
            default = sys.stdin.buffer,
            type = OptionalGzipFiletype('rb'),
        )
    parser.add_argument('--column', '-col', type = int, default = -1)
    parser.add_argument('--seperator','-sep', type = str, default = '\t')
    add_default_output(parser)

def main(args):

    for field, count in count_occurences(
        args.infile,
        column = args.column,
        sep = args.seperator,
    ).items():
        args.outfile.write(field + args.seperator + str(count) + '\n')