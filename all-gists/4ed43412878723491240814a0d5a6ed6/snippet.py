'''
:Date: 26 Jul 2016
:Author: Public Health England
'''

"""Detect peaks in data based on their amplitude and other features."""
import argparse

from khmer import khmer_args
import khmer
from khmer.kfile import check_input_files
from khmer.khmer_args import build_counting_args
from scipy.signal import find_peaks_cwt
import sys

import numpy as np

def peakdet(v, delta, x=None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Returns two arrays
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    maxtab = []
    mintab = []

    if x is None:
        x = np.arange(len(v))

    v = np.asarray(v)

    mn, mx = np.Inf, -np.Inf
    mnpos, mxpos = np.NaN, np.NaN

    lookformax = True

    for i in np.arange(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]

        if lookformax:
            if this < mx - delta:
                maxtab.append((mxpos, mx))
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn + delta:
                mintab.append((mnpos, mn))
                mx = this
                mxpos = x[i]
                lookformax = True


    maxtab = [ int(i[0]) for i in maxtab]

    return maxtab

def plot(x, plot_file, min_peaks=None, max_peaks=None):
    """Plot results of the detect_peaks function, see its help."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print('matplotlib is not available.')
    else:
        plt.style.use('ggplot')
        _, ax = plt.subplots(1, 1, figsize=(8, 4))

        ax.plot(x, 'black', lw=1)
        if max_peaks:
            ax.plot(max_peaks, x[max_peaks], '+', mfc=None, mec='g', mew=2, ms=8,
                    label='Max peaks')
        if min_peaks:
            ax.plot(min_peaks, x[min_peaks], '+', mfc=None, mec='r', mew=2, ms=8,
                    label='Min peaks')

        ax.set_xlim(-.02 * x.size, x.size * 1.02 - 1)
        ymin, ymax = x[np.isfinite(x)].min(), x[np.isfinite(x)].max()
        yrange = ymax - ymin if ymax > ymin else 1
        ax.set_ylim(ymin - 0.1 * yrange, ymax + 0.1 * yrange)
        ax.set_xlabel('Abundance', fontsize=12)
        ax.set_ylabel('Counts', fontsize=12)
        plt.gcf().subplots_adjust(bottom=0.15)

        ax.set_title("Min abundance finding.")
        # plt.grid()
        plt.savefig(plot_file)

def get_args():
    parser = build_counting_args(
        descr="Calculate the abundance distribution of k-mers from a "
        "single sequence file.")

    parser.add_argument('input_sequence_filename', help='The name of the input'
                        ' FAST[AQ] sequence file.')
    parser.add_argument('-z', '--no-zero', dest='output_zero', default=True,
                        action='store_false',
                        help='Do not output zero-count bins')
    parser.add_argument('-b', '--no-bigcount', dest='bigcount', default=True,
                        action='store_false',
                        help='Do not count k-mers past 255')
    parser.add_argument('-s', '--squash', dest='squash_output', default=False,
                        action='store_true',
                        help='Overwrite output file if it exists')
    parser.add_argument('--savegraph', default='', metavar="filename",
                        help="Save the k-mer countgraph to the specified "
                        "filename.")
    parser.add_argument('-f', '--force', default=False, action='store_true',
                        help='Overwrite output file if it exists')
    parser.add_argument('-q', '--quiet', dest='quiet', default=False,
                        action='store_true')

    parser.add_argument('--max-abundance', default=300, type=int, help="Max abundance to consider.")

    parser.add_argument('--hist-plot', help="If set, the histogram of process will be saved there.")
    return parser

def main():
    args = get_args().parse_args()


    check_input_files(args.input_sequence_filename, args.force)

    print('making countgraph')
    countgraph = khmer_args.create_countgraph(args, multiplier=1.1)
    countgraph.set_use_bigcount(args.bigcount)

    print('building k-mer tracking graph')
    tracking = khmer_args.create_nodegraph(args, multiplier=1.1)

    print('kmer_size: %s' % countgraph.ksize())
    print('k-mer countgraph sizes: %s' % countgraph.hashsizes())

    # start loading
    rparser = khmer.ReadParser(args.input_sequence_filename)
    print('consuming input, round 1 -- %s' % args.input_sequence_filename)

    countgraph.consume_fasta_with_reads_parser(rparser)

    print('Total number of unique k-mers: %s' %
             countgraph.n_unique_kmers())

    abundance_lists = []

    def __do_abundance_dist__(read_parser):
        abundances = countgraph.abundance_distribution_with_reads_parser(
            read_parser, tracking)
        abundance_lists.append(abundances)

    print('preparing hist from %s...' %
             args.input_sequence_filename)

    rparser = khmer.ReadParser(args.input_sequence_filename)

    print('consuming input, round 2 -- %s' % args.input_sequence_filename)

    __do_abundance_dist__(rparser)

    assert len(abundance_lists) == 1, len(abundance_lists)
    abundance = {}
    for abundance_list in abundance_lists:
        for i, count in enumerate(abundance_list):
            abundance[i] = abundance.get(i, 0) + count

    total = sum(abundance.values())

    if 0 == total:
        print("ERROR: abundance distribution is uniformly zero; "
                  "nothing to report.")
        print("\tPlease verify that the input files are valid.")
        return 1


    np_abundance = np.zeros(len(abundance))
    max_count = 0

    sofar = 0
    for row_i, count in sorted(abundance.items()):
        if row_i == 0 and not args.output_zero:
            continue

        np_abundance[row_i] = count

        if count > max_count:
            max_count = count


        sofar += count

        if sofar == total:
            break

    if args.max_abundance:
        np_abundance = np_abundance[:args.max_abundance]

    max_peaks = peakdet(np_abundance, 100)

    min_peak = None
    # Find lowest point in the interval
    try:
        for valley in xrange(max_peaks[0], max_peaks[1]):
            if min_peak is None:
                min_peak = valley
            elif np_abundance[valley] < np_abundance[min_peak]:
                min_peak = valley
        print min_peak if min_peak is not None else -1
        result = 0
    except IndexError:
        sys.stderr.write("Could not estimate min abundance for %s.\n" % args.input_sequence_filename)
        if len(max_peaks) <= 1:
            sys.stderr.write("Is there enough data in the FastQ? Only %s peaks have been identified." % len(max_peaks))
        result = 1

    if args.hist_plot:
        plot(np_abundance, args.hist_plot, max_peaks=max_peaks[0:2], min_peaks=min_peak)

    return result

if __name__ == '__main__':
    exit(main())
