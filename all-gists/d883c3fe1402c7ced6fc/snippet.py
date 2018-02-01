import numpy as np
import scipy.signal
import mne
from scipy.stats import kurtosis
from mne.preprocessing import find_outliers
from mne.fixes import nanmean
from mne.utils import logger
#from mne.preprocessing.eog import _get_eog_channel_index


def hurst(x):
    """Estimate Hurst exponent on a timeseries.

    The estimation is based on the second order discrete derivative.

    Parameters
    ----------
    x : 1D numpy array
        The timeseries to estimate the Hurst exponent for.

    Returns
    -------
    h : float
        The estimation of the Hurst exponent for the given timeseries.
    """
    y = np.cumsum(np.diff(x, axis=1), axis=1)

    b1 = [1, -2, 1]
    b2 = [1,  0, -2, 0, 1]

    # second order derivative
    y1 = scipy.signal.lfilter(b1, 1, y, axis=1)
    y1 = y1[:, len(b1) - 1:-1]  # first values contain filter artifacts

    # wider second order derivative
    y2 = scipy.signal.lfilter(b2, 1, y, axis=1)
    y2 = y2[:, len(b2) - 1:-1]  # first values contain filter artifacts

    s1 = np.mean(y1 ** 2, axis=1)
    s2 = np.mean(y2 ** 2, axis=1)

    return 0.5 * np.log2(s2 / s1)

def _freqs_power(data, sfreq, freqs):
    fs, ps = scipy.signal.welch(data, sfreq,
                                nperseg=2 ** int(np.log2(10 * sfreq) + 1),
                                noverlap=0,
                                axis=-1)
    return np.sum([ps[..., np.searchsorted(fs, f)] for f in freqs], axis=0)

def faster_bad_channels(epochs, picks=None, thres=3, use_metrics=None):
    """Implements the first step of the FASTER algorithm.
    
    This function attempts to automatically mark bad EEG channels by performing
    outlier detection. It operated on epoched data, to make sure only relevant
    data is analyzed.

    Parameters
    ----------
    epochs : Instance of Epochs
        The epochs for which bad channels need to be marked
    picks : list of int | None
        Channels to operate on. Defaults to EEG channels.
    thres : float
        The threshold value, in standard deviations, to apply. A channel
        crossing this threshold value is marked as bad. Defaults to 3.
    use_metrics : list of str
        List of metrics to use. Can be any combination of:
            'variance', 'correlation', 'hurst', 'kurtosis', 'line_noise'
        Defaults to all of them.

    Returns
    -------
    bads : list of str
        The names of the bad EEG channels.
    """
    metrics = {
        'variance':    lambda x: np.var(x, axis=1),
        'correlation': lambda x: nanmean(
                           np.ma.masked_array(
                               np.corrcoef(x),
                               np.identity(len(x), dtype=bool)
                           ),
                           axis=0),
        'hurst':       lambda x: hurst(x),
        'kurtosis':    lambda x: kurtosis(x, axis=1),
        'line_noise':  lambda x: _freqs_power(x, epochs.info['sfreq'],
                                              [50, 60]),
    }

    if picks is None:
        picks = mne.pick_types(epochs.info, meg=False, eeg=True, exclude=[])
    if use_metrics is None:
        use_metrics = metrics.keys()

    # Concatenate epochs in time
    data = epochs.get_data()
    data = data.transpose(1, 0, 2).reshape(data.shape[1], -1)
    data = data[picks]

    # Find bad channels
    bads = []
    for m in use_metrics:
        s = metrics[m](data)
        b = [epochs.ch_names[picks[i]] for i in find_outliers(s, thres)]
        logger.info('Bad by %s:\n\t%s' % (m, b))
        bads.append(b)

    return np.unique(np.concatenate(bads)).tolist()

def _deviation(data):
    """Computes the deviation from mean for each channel in a set of epochs.

    This is not implemented as a lambda function, because the channel means
    should be cached during the computation.
    
    Parameters
    ----------
    data : 3D numpy array
        The epochs (#epochs x #channels x #samples).

    Returns
    -------
    dev : 1D numpy array
        For each epoch, the mean deviation of the channels.
    """
    ch_mean = np.mean(data, axis=2)
    return ch_mean - np.mean(ch_mean, axis=0)

def faster_bad_epochs(epochs, picks=None, thres=3, use_metrics=None):
    """Implements the second step of the FASTER algorithm.
    
    This function attempts to automatically mark bad epochs by performing
    outlier detection.

    Parameters
    ----------
    epochs : Instance of Epochs
        The epochs to analyze.
    picks : list of int | None
        Channels to operate on. Defaults to EEG channels.
    thres : float
        The threshold value, in standard deviations, to apply. An epoch
        crossing this threshold value is marked as bad. Defaults to 3.
    use_metrics : list of str
        List of metrics to use. Can be any combination of:
            'amplitude', 'variance', 'deviation'
        Defaults to all of them.

    Returns
    -------
    bads : list of int
        The indices of the bad epochs.
    """

    metrics = {
        'amplitude': lambda x: np.mean(np.ptp(x, axis=2), axis=1),
        'deviation': lambda x: np.mean(_deviation(x), axis=1),
        'variance':  lambda x: np.mean(np.var(x, axis=2), axis=1),
    }

    if picks is None:
        picks = mne.pick_types(epochs.info, meg=False, eeg=True,
                               exclude='bads')
    if use_metrics is None:
        use_metrics = metrics.keys()

    data = epochs.get_data()[:, picks, :]

    bads = []
    for m in use_metrics:
        s = metrics[m](data)
        b = find_outliers(s, thres)
        logger.info('Bad by %s:\n\t%s' % (m, b))
        bads.append(b)

    return np.unique(np.concatenate(bads)).tolist()

def _power_gradient(ica, source_data):
    # Compute power spectrum
    f, Ps = scipy.signal.welch(source_data, ica.info['sfreq'])

    # Limit power spectrum to upper frequencies
    Ps = Ps[:, np.searchsorted(f, 25):np.searchsorted(f, 45)]

    # Compute mean gradients
    return np.mean(np.diff(Ps), axis=1)


def faster_bad_components(ica, epochs, thres=3, use_metrics=None):
    """Implements the third step of the FASTER algorithm.
    
    This function attempts to automatically mark bad ICA components by
    performing outlier detection.

    Parameters
    ----------
    ica : Instance of ICA
        The ICA operator, already fitted to the supplied Epochs object.
    epochs : Instance of Epochs
        The untransformed epochs to analyze.
    thres : float
        The threshold value, in standard deviations, to apply. A component
        crossing this threshold value is marked as bad. Defaults to 3.
    use_metrics : list of str
        List of metrics to use. Can be any combination of:
            'eog_correlation', 'kurtosis', 'power_gradient', 'hurst',
            'median_gradient'
        Defaults to all of them.

    Returns
    -------
    bads : list of int
        The indices of the bad components.

    See also
    --------
    ICA.find_bads_ecg
    ICA.find_bads_eog
    """
    source_data = ica.get_sources(epochs).get_data().transpose(1,0,2)
    source_data = source_data.reshape(source_data.shape[0], -1)

    metrics = {
        'eog_correlation': lambda x: x.find_bads_eog(epochs)[1],
        'kurtosis':        lambda x: kurtosis(
                               np.dot(
                                   x.mixing_matrix_.T,
                                   x.pca_components_[:x.n_components_]),
                               axis=1),
        'power_gradient':  lambda x: _power_gradient(x, source_data),
        'hurst':           lambda x: hurst(source_data),
        'median_gradient': lambda x: np.median(np.abs(np.diff(source_data)),
                                               axis=1),
        'line_noise':  lambda x: _freqs_power(source_data,
                                              epochs.info['sfreq'], [50, 60]),
    }

    if use_metrics is None:
        use_metrics = metrics.keys()

    bads = []
    for m in use_metrics:
        scores = np.atleast_2d(metrics[m](ica))
        for s in scores:
            b = find_outliers(s, thres)
            logger.info('Bad by %s:\n\t%s' % (m, b))
            bads.append(b)

    return np.unique(np.concatenate(bads)).tolist()

def faster_bad_channels_in_epochs(epochs, picks=None, thres=3, use_metrics=None):
    """Implements the fourth step of the FASTER algorithm.
    
    This function attempts to automatically mark bad channels in each epochs by
    performing outlier detection.

    Parameters
    ----------
    epochs : Instance of Epochs
        The epochs to analyze.
    picks : list of int | None
        Channels to operate on. Defaults to EEG channels.
    thres : float
        The threshold value, in standard deviations, to apply. An epoch
        crossing this threshold value is marked as bad. Defaults to 3.
    use_metrics : list of str
        List of metrics to use. Can be any combination of:
            'amplitude', 'variance', 'deviation', 'median_gradient'
        Defaults to all of them.

    Returns
    -------
    bads : list of lists of int
        For each epoch, the indices of the bad channels.
    """

    metrics = {
        'amplitude':       lambda x: np.ptp(x, axis=2),
        'deviation':       lambda x: _deviation(x),
        'variance':        lambda x: np.var(x, axis=2),
        'median_gradient': lambda x: np.median(np.abs(np.diff(x)), axis=2),
        'line_noise':      lambda x: _freqs_power(x, epochs.info['sfreq'],
                                                  [50, 60]),
    }

    if picks is None:
        picks = mne.pick_types(epochs.info, meg=False, eeg=True,
                               exclude='bads')
    if use_metrics is None:
        use_metrics = metrics.keys()

    
    data = epochs.get_data()[:, picks, :]

    bads = [[] for i in range(len(epochs))]
    for m in use_metrics:
        s_epochs = metrics[m](data)
        for i, s in enumerate(s_epochs):
            b = [epochs.ch_names[picks[j]] for j in find_outliers(s, thres)]
            logger.info('Epoch %d, Bad by %s:\n\t%s' % (i, m, b))
            bads[i].append(b)

    for i, b in enumerate(bads):
        if len(b) > 0:
            bads[i] = np.unique(np.concatenate(b)).tolist()

    return bads

def run_faster(epochs, thres=3, copy=True):
    """Run the entire FASTER pipeline on the data.
    """
    if copy:
        epochs = epochs.copy()

    # Step one
    logger.info('Step 1: mark bad channels')
    epochs.info['bads'] += faster_bad_channels(epochs, thres=5)

    # Step two
    logger.info('Step 2: mark bad epochs')
    bad_epochs = faster_bad_epochs(epochs, thres=thres)
    good_epochs = list(set(range(len(epochs))).difference(set(bad_epochs)))
    epochs = epochs[good_epochs]

    # Step three (using the build-in MNE functionality for this)
    logger.info('Step 3: mark bad ICA components')
    picks = mne.pick_types(epochs.info, meg=False, eeg=True, eog=True, exclude='bads')
    ica = mne.preprocessing.run_ica(epochs, len(picks), picks=picks, eog_ch=['vEOG', 'hEOG'])
    print ica.exclude
    ica.apply(epochs)

    # Step four
    logger.info('Step 4: mark bad channels for each epoch')
    bad_channels_per_epoch = faster_bad_channels_in_epochs(epochs, thres=thres)
    for i, b in enumerate(bad_channels_per_epoch):
        if len(b) > 0:
            epoch = epochs[i]
            epoch.info['bads'] += b
            epoch.interpolate_bads_eeg()
            epochs._data[i, :, :] = epoch._data[0, :, :]

    # Now that the data is clean, apply average reference
    epochs.info['custom_ref_applied'] = False
    epochs, _ = mne.io.set_eeg_reference(epochs)
    epochs.apply_proj()

    # That's all for now
    return epochs
