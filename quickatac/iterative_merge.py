
import argparse
from quickatac import genome_tools as gt
from quickatac.base import add_default_output
import tqdm
import numpy as np
import sys
import os

def check(genome, region):
    try:
        genome.check_region(region)
        return True
    except gt.NotInGenomeError:
        return False

       
def add_source(self, source):
    self.source = source
    return self
        
gt.Region.add_source = add_source


def _collect_summits(summit_files, genome):

    summits = [
        r.add_source(os.path.basename(summit_file))
        for summit_file in summit_files for r in gt.Region.read_bedfile(summit_file)
        if check(genome, r)
    ]

    return summits

def _iou(r1, r2, threshold = 0.2):
    
    intersection = r1._overlap_distance(r1.start, r1.end, r2.start, r2.end)
    union = len(r1) + len(r2) - intersection
    
    return int(intersection/union > threshold)
    

def _merge(*, overlap_peaks, summit_set, genome):
    if( summit_set.regions[0].annotation is None):
        significance = np.array([-float(r.end) for r in summit_set.regions]).argsort()
    else:
        significance = np.array([-float(r.annotation[1]) for r in summit_set.regions]).argsort()

    blacklist = {}
    peaklist = []
    for i in tqdm.tqdm(significance, desc = 'Iteratively merging peaks'):
    
        if not i in blacklist:
            
            overlaps_idx = overlap_peaks[i,:].indices
            for j in overlaps_idx:
                if not j in blacklist:
                    blacklist[j]=True

            peaklist.append(summit_set.regions[i])
            blacklist[i] = True

    peaklist = gt.RegionSet(peaklist, genome)

    return peaklist


def iterative_merge(*,
    peak_files,
    genome_file,
    ):

    genome = gt.Genome.from_file(genome_file)

    summits = _collect_summits(peak_files, genome)

    summit_set = gt.RegionSet(summits, genome)
    overlap_peaks = summit_set.map_intersects(summit_set, distance_function=_iou)

    overlap_peaks.eliminate_zeros()
    overlap_peaks = overlap_peaks.tocsr()

    peaks = _merge(
        overlap_peaks = overlap_peaks, 
        summit_set = summit_set, 
        genome = genome)

    return peaks


def add_arguments(parser):

    parser.add_argument('peakfiles', nargs = '+', type = str,
        help = 'List of MACS summit files to merge')
    parser.add_argument('--genome-file','-g', type = str, 
        help = 'Genome file (or chromlengths file).', required = True)
    
    add_default_output(parser)

def main(args):

    peaklist = iterative_merge(
        peak_files=args.peakfiles,
        genome_file= args.genome_file
    )

    for peak in peaklist.regions:
        if(peak.annotation is None):
            print(
                str(peak.chromosome), 
                peak.start, 
                peak.end, 
                peak.source, 
            file = args.outfile, sep = '\t', end = '\n'
        )
        else:

            print(
                str(peak.chromosome), 
                peak.start, 
                peak.end, 
                peak.source, 
                peak.annotation[1], 
                file = args.outfile, sep = '\t', end = '\n'
            )
