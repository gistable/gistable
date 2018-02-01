"""Run Length Encoding utilities for NumPy arrays.

Authors
-------
- Nezar Abdennur
- Anton Goloborodko

"""
from __future__ import division, print_function
import numpy as np


def rlencode(x, dropna=False):
    """
    Run length encoding.
    Based on http://stackoverflow.com/a/32681075, which is based on the rle 
    function from R.
    
    Parameters
    ----------
    x : 1D array_like
        Input array to encode
    dropna: bool, optional
        Drop all runs of NaNs.
    
    Returns
    -------
    start positions, run lengths, run values
    
    """
    where = np.flatnonzero
    x = np.asarray(x)
    n = len(x)
    if n == 0:
        return (np.array([], dtype=int), 
                np.array([], dtype=int), 
                np.array([], dtype=x.dtype))

    starts = np.r_[0, where(~np.isclose(x[1:], x[:-1], equal_nan=True)) + 1]
    lengths = np.diff(np.r_[starts, n])
    values = x[starts]
    
    if dropna:
        mask = ~np.isnan(values)
        starts, lengths, values = starts[mask], lengths[mask], values[mask]
    
    return starts, lengths, values


def rldecode(starts, lengths, values, minlength=None):
    """
    Decode a run-length encoding of a 1D array.
    
    Parameters
    ----------
    starts, lengths, values : 1D array_like
        The run-length encoding.
    minlength : int, optional
        Minimum length of the output array.
    
    Returns
    -------
    1D array. Missing data will be filled with NaNs.
    
    """
    starts, lengths, values = map(np.asarray, (starts, lengths, values))
    # TODO: check validity of rle
    ends = starts + lengths
    n = ends[-1]
    if minlength is not None:
        n = max(minlength, n)
    x = np.full(n, np.nan)
    for lo, hi, val in zip(starts, ends, values):
        x[lo:hi] = val
    return x


def iterruns(x, value=None, **kwargs):
    starts, lengths, values = rlencode(x, **kwargs)
    if value is None:
        ends = starts + lengths
        return zip(starts, ends, values)
    else:
        mask = values == value
        starts, lengths = starts[mask], lengths[mask]
        ends = starts + lengths
        return zip(starts, ends)


def isrle(starts, lengths, values):
    if not (len(starts) == len(lengths) == len(values)):
        return False

    if np.any(np.diff(starts) < 0):
        return False

    ends = starts + lengths
    if np.any(ends[:-1] > starts[1:]):
        return False

    return True


def slv2sev(starts, lengths, values):
    return starts, starts + lengths, values


def sev2slv(starts, ends, values):
    return starts, ends - starts, values


def simplify(starts, lengths, values, minlength=None):
    """
    Remove NaN runs and runs of length zero and stich together consecutive runs
    of the same value.
    
    """
    starts, lengths, values = fill_gaps(starts, lengths, values, minlength)
    n = starts[-1] + lengths[-1]
    
    is_nontrivial = lengths > 0
    starts = starts[is_nontrivial]
    values = values[is_nontrivial]
    
    is_new_run = np.r_[True, ~np.isclose(values[:-1], values[1:], equal_nan=True)]
    starts = starts[is_new_run]
    values = values[is_new_run]
    
    lengths = np.r_[starts[1:] - starts[:-1], n - starts[-1]]

    mask = ~np.isnan(values)
    return starts[mask], lengths[mask], values[mask]


def fill_gaps(starts, lengths, values, minlength=None, fill_value=np.nan):
    """
    Add additional runs to fill in spaces between runs. Defaults to runs of NaN.

    """
    where = np.flatnonzero
    n = starts[-1] + lengths[-1]
    if minlength is not None:
        n = max(minlength, n)

    ends = starts + lengths
    lo = np.r_[0, ends] 
    hi = np.r_[starts, n]    
    gap_locs = where((hi - lo) > 0)
    if len(gap_locs):
        starts = np.insert(starts, gap_locs, lo[gap_locs])
        lengths = np.insert(lengths, gap_locs, hi[gap_locs] - lo[gap_locs])
        values = np.insert(values, gap_locs, fill_value)
    return starts, lengths, values


def impute_missing(starts, lengths, values, terminal_values=(0, 0)):
    """
    Replace NaN runs by imputing the values in them. The values inside the two
    halves of a NaN run are imputed according to the values of its flanking 
    runs.

    Parameters
    ----------
    starts, lengths, values: 1D array_like
        run-length encoding
    terminal_values: tuple, optional
        terminal flanking values to use to impute terminal NaN runs

    Returns
    -------
    starts, lengths, values
    
    """
    where = np.flatnonzero
    n = starts[-1] + lengths[-1]
    starts  = np.r_[0, starts, n]
    lengths = np.r_[0, lengths, 0]
    values = np.r_[terminal_values[0], values, terminal_values[1]]
    
    nanrun_mask = np.isnan(values)
    nanrun_locs = where(nanrun_mask)
    starts[nanrun_locs + 1] -= lengths[nanrun_locs] // 2

    starts  = starts[~nanrun_mask]
    values  = values[~nanrun_mask]
    lengths = np.r_[starts[1:] - starts[:-1], n - starts[-1]]
    return simplify(starts, lengths, values)
