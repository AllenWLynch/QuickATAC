from quickatac.base import enforce_string, add_default_input, add_default_output

def check_num_columns(fragments, 
    min_cols = 5, max_cols = 5):

    for i, line in enumerate(map(enforce_string, fragments)):
        
        if not line[0] == '#':
            num_cols = len(line.strip().split('\t'))

            try:
                initial_num_cols
            except UnboundLocalError:
                initial_num_cols = num_cols
                assert num_cols >= min_cols, 'Line {} of the fragment file does not have sufficient number of columns: {}'\
                    .format(str(i), line) 

                assert num_cols <= max_cols, 'Line {} of the fragment file has too many columns: {}'\
                    .format(str(i), line) 

            else:
                assert num_cols == initial_num_cols, 'Line {} of the fragment file has a different number of columns than the first fragment: {}'\
                    .format(str(i), line)

        yield line.strip()


def main(args):

    for fragment in check_num_columns(args.fragments,
        min_cols = args.min_cols,
        max_cols = args.max_cols,
    ):
        args.outfile.write(fragment + '\n')

def add_arguments(parser):

    add_default_input(parser)
    parser.add_argument('--min-cols','-min', default = 5, type = int)
    parser.add_argument('--max-cols','-max', default = 5, type = int)
    add_default_output(parser)
    
