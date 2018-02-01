import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd  # Not used here but will be required for creating dataframe
import re
import seaborn.apionly as sns

"""
MIT License

Copyright (c) [2016] [Parashar Dhapola]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__ = "Parashar Dhapola"
__email__ = "parashar.dhapola@gmail.com"


class ChromVis(object):

    chromInfo = {
        'hg38': {
            'lengths': {
                'chr1': 248956422, 'chr2': 242193529, 'chr3': 198295559,
                'chr4': 190214555, 'chr5': 181538259, 'chr6': 170805979,
                'chr7': 159345973, 'chr8': 145138636, 'chr9': 138394717,
                'chr10': 133797422, 'chr11': 135086622, 'chr12': 133275309,
                'chr13': 114364328, 'chr14': 107043718, 'chr15': 101991189,
                'chr16': 90338345, 'chr17': 83257441, 'chr18': 80373285,
                'chr19': 58617616, 'chr20': 64444167, 'chr21': 46709983,
                'chr22': 50818468, 'chrX': 156040895, 'chrY': 57227415
            },
            'centromeres': {
                'chr1': 123400000, 'chr10': 39800000, 'chr11': 53400000,
                'chr12': 35500000, 'chr13': 17700000, 'chr14': 17200000,
                'chr15': 19000000, 'chr16': 36800000, 'chr17': 25100000,
                'chr18': 18500000, 'chr19': 26200000, 'chr2': 93900000,
                'chr20': 28100000, 'chr21': 12000000, 'chr22': 15000000,
                'chr3': 90900000, 'chr4': 50000000, 'chr5': 48800000,
                'chr6': 59800000, 'chr7': 60100000, 'chr8': 45200000,
                'chr9': 43000000, 'chrX': 61000000, 'chrY': 10400000
            }
        }
    }

    def __init__(self, data, chromosomes='all', chromosome_lengths='hg38',
                 centromere_pos='hg38', height=15, width=15, descaling_factor=1000,
                 val_scaling_factor=10, grid_ratio=[1, 1, 8], chrom_spacing=0.1,
                 bar_lim=1, max_val=None, seaborn_palette='muted'):
        """
        Args:
            data: A pandas dataframe with three columns compulsary columns:
                    'chromosomes': Chromosome name
                    'positions': position of feature on chromosome in bases
                    '<sample_name>': Value at the corresponding position for a
                                     given sample. Should be positive intergers.
                     ..'<sample_name>': Further sample values might be added in
                                        additional columns.
            chromosomes: Chromosome name in the order to be plotted.
            chromosome_lengths: List of length of each chromosome in order
                                given in argument 'chroms'. If a string is provided
                                than the class attribute 'chromInfo' (dict) is
                                looked up for the key.
            centromere_pos: List containing the position of centromeres
                            (center of centromere to be indicated).If a string is
                            provided than the class attribute 'chromInfo' (dict)
                            is looked up for the key.
            height: Figure height in inches.
            width: Figure width in inches.
            descaling_factor: The longest chromosome is descaled to this length
            val_scaling_factor:  A multiplication factor for values. Increasing this
                                 will make the vertical bars over chromosomes taller.
            grid_ratio: A list of three integer values defining the the width
                        ratio of columns in the figure. First column
                        containing the chromsome name, second contains the bar
                        plots for sum of values plotted in each chromosome and
                        the third the annotated chromosomes.
            chrom_spacing: Spacing between chromosomes.
            max_val: If set to none, the maximum value is automatically found from
                     the dataframe. This value is used to normalize the rest values
                     to set the scale to one, which might be further increased using
                     'val_scaling_factor' . However, in certain cases where user wants
                     to plot to chromosome maps and compare there values, this might
                     be set.
            seaborn_palette: Seaborn color palette
        """
        self.data = data
        self.chroms = chromosomes
        self.chromLengths = chromosome_lengths
        self.centromerePos = centromere_pos
        self.figHeight = height
        self.figWidth = width
        self.descalingFactor = descaling_factor
        self.valScalingFactor = val_scaling_factor
        self.gridRatio = grid_ratio
        self.chromSpacing = chrom_spacing
        self.colorPalette = seaborn_palette

        if self._sanitize() is True:
            self.maxChromLen = self._get_max_chrom_len()
            self.maxVal = self._get_max_val()
            self.figure = self._make_canvas()
            self.grid = self._make_grid()
            self.sampleNames = self._get_sample_names()
            self.barVals, self.maxBarVal = self._make_bar_values()
            self.colors = self._make_colors()

            for n, c in enumerate(self.chroms):
                self.curChromName = c
                self.curChromNum = n
                self.curChromScaledLen = self._get_chrom_scaled_len()
                self.curCenPos = self._get_centromere_position()
                self.curPositions, self.curValues = self._get_chrom_data()
                _ = self._make_label_axis()
                _ = self._make_bar_axis()
                _ = self._make_chrom_axis()
        else:
            print "ERROR"

    @staticmethod
    def _clean_axis(ax):
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        for i in ax.spines:
            ax.spines[i].set_visible(False)
        return True

    @staticmethod
    def _natsort(l):
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(l, key=alphanum_key)

    def _sanitize(self):
        if type(self.chroms) is list:
            pass
        else:
            if self.chroms == 'all':
                self.chroms = ChromVis._natsort(list(set(
                    self.data.chromosomes.values)))
            else:
                pass
        if type(self.chromLengths) is list:
            pass
        else:
            if self.chromLengths in ChromVis.chromInfo:
                info = ChromVis.chromInfo[self.chromLengths]['lengths']
                self.chromLengths = []
                for i in self.chroms:
                    if i in info:
                        self.chromLengths.append(info[i])
        if type(self.centromerePos) is list:
            pass
        else:
            if self.centromerePos in ChromVis.chromInfo:
                info = ChromVis.chromInfo[self.centromerePos]['centromeres']
                self.centromerePos = []
                for i in self.chroms:
                    if i in info:
                        self.centromerePos.append(info[i])
        return True

    def _get_max_chrom_len(self):
        return max(self.chromLengths)

    def _get_max_val(self):
        max_val = 0
        for sample in self.data:
            if sample not in ['chromosomes', 'positions']:
                if max(self.data[sample]) > max_val:
                    max_val = max(self.data[sample])
        return float(max_val)

    def _make_canvas(self):
        return plt.figure(figsize=(self.figWidth, self.figHeight))

    def _make_grid(self):
        return mpl.gridspec.GridSpec(
            len(self.chromLengths), sum(self.gridRatio),
            hspace=self.chromSpacing)

    def _get_sample_names(self):
        names = []
        for sample in self.data:
            if sample not in ['chromosomes', 'positions']:
                names.append(sample)
        return names

    def _get_chrom_scaled_len(self):
        return int(self.chromLengths[self.curChromNum] *
                   self.descalingFactor / self.maxChromLen)

    def _get_centromere_position(self):
        return int((self.centromerePos[self.curChromNum] *
                    self.curChromScaledLen) /
                   self.chromLengths[self.curChromNum])

    def _get_chrom_data(self):
        df = self.data[self.data.chromosomes == self.curChromName]
        positions = df.positions.apply(
            lambda x: int((x * self.curChromScaledLen) /
                          self.chromLengths[self.curChromNum]))
        values = []
        for sample in self.sampleNames:
            values.append(df[sample].apply(
                lambda x: np.log2(x) / np.log2(self.maxVal)))
        return positions, np.asarray(values).T

    def _make_colors(self):
        return sns.color_palette(self.colorPalette,
                                 len(self.sampleNames), desat=0.7)

    def _make_bar_values(self):
        bar_vals = {}
        max_bar_val = 0
        for chrom in self.chroms:
            df = self.data[self.data.chromosomes == chrom]
            temp = []
            for sample in self.sampleNames:
                v = df[sample].sum()
                temp.append(v)
                if v > max_bar_val:
                    max_bar_val = v
            bar_vals[chrom] = temp
        return bar_vals, max_bar_val

    def _make_label_axis(self):
        ax = plt.subplot(self.grid[self.curChromNum, :self.gridRatio[0]])
        ax.set_ylim((0, 1))
        ax.set_xlim((0, 1))
        ax.text(1, 0.25, self.curChromName, fontsize=20,
                horizontalalignment='right')
        return ChromVis._clean_axis(ax)

    def _make_bar_axis(self):
        ax = plt.subplot(self.grid[self.curChromNum, self.gridRatio[0]:
                                   self.gridRatio[0] + self.gridRatio[1]])
        x = [i for i in range(len(self.barVals[self.curChromName]))]
        y = [i for i in self.barVals[self.curChromName]]
        bar_list = ax.barh(x, y, 0.75)
        for i in range(len(bar_list)):
            bar_list[i].set_color(self.colors[i])
        ax.set_ylim((0, len(self.barVals[self.curChromName])))
        ax.set_xlim((0, self.maxBarVal))
        return ChromVis._clean_axis(ax)

    def _make_chrom_axis(self):
        ax = plt.subplot(self.grid[self.curChromNum, self.gridRatio[0] +
                                   self.gridRatio[1]:])
        ax.plot([0, self.curCenPos - 5], [-1, -1], alpha=0.6, c='grey', lw=3)
        ax.plot([self.curCenPos + 5, self.curChromScaledLen],
                [-1, -1], alpha=0.6, c='grey', lw=3)
        ax.scatter([self.curCenPos], [-1], c='crimson', lw=0, s=30, alpha=1)
        for p, vv in zip(self.curPositions, self.curValues):
            for c, v in zip(self.colors, vv):
                ax.plot([p, p + 0.01], [0, v * self.valScalingFactor],
                        lw=3, c=c, alpha=0.8)
        ax.set_xlim((0, self.descalingFactor))
        ax.set_ylim((-3, self.valScalingFactor))
        return ChromVis._clean_axis(ax)
