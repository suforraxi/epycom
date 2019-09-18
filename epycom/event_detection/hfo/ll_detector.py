# -*- coding: utf-8 -*-
# Copyright (c) St. Anne's University Hospital in Brno. International Clinical
# Research Center, Biomedical Engineering. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


# Std imports

# Third pary imports
import numpy as np
from scipy.signal import butter, filtfilt

# Local imports
from ...utils.signal_transforms import compute_line_lenght
from ...utils.thresholds import th_std
from ...utils.method import Method


def detect_hfo_ll(sig, fs=5000, threshold=3, window_size=100,
                  window_overlap=0.25):
    """
    Line-length detection algorithm {Gardner et al. 2007, Worrell et al. 2018,
    Akiyama et al. 2011}.

    Parameters
    ----------
    sig: np.ndarray
        1D array with raw data (already filtered if required)
    fs: int
        Sampling frequency
    threshold: float
        Number of standard deviations to use as a threshold
    window_size: int
        Sliding window size in samples
    window_overlap: float
        Fraction of the window overlap (0 to 1)

    Returns:
    --------
    output: list
        List of tuples with the following structure:
        (event_start, event_stop)
    """

    # Calculate window values for easier operation
    window_increment = int(np.ceil(window_size * window_overlap))

    output = []

    # Overlapping window

    win_start = 0
    win_stop = window_size
    n_windows = int(np.ceil((len(sig) - window_size) / window_increment)) + 1
    LL = np.empty(n_windows)
    LL_i = 0
    while win_start < len(sig):
        if win_stop > len(sig):
            win_stop = len(sig)

        LL[LL_i] = compute_line_lenght(sig[int(win_start):int(win_stop)],
                                       window_size)[0]

        if win_stop == len(sig):
            break

        win_start += window_increment
        win_stop += window_increment

        LL_i += 1

    # Create threshold
    det_th = th_std(LL, threshold)

    # Detect
    LL_idx = 0
    while LL_idx < len(LL):
        if LL[LL_idx] >= det_th:
            event_start = LL_idx * window_increment
            while LL_idx < len(LL) and LL[LL_idx] >= det_th:
                LL_idx += 1
            event_stop = (LL_idx * window_increment) + window_size

            if event_stop > len(sig):
                event_stop = len(sig)

            # Optional feature calculations can go here

            # Write into dataframe
            output.append((event_start, event_stop))

            LL_idx += 1
        else:
            LL_idx += 1

    return output


class LineLengthDetector(Method):

    def __init__(self, **kwargs):
        """
        Line-length detection algorithm {Gardner et al. 2007,
        Worrell et al. 2018, Akiyama et al. 2011}.

        Parameters
        ----------
        fs: int
            Sampling frequency
        threshold: float
            Number of standard deviations to use as a threshold
        window_size: int
            Sliding window size in samples
        window_overlap: float
            Fraction of the window overlap (0 to 1)
        """

        super().__init__(detect_hfo_ll, **kwargs)

        self.algorithm = 'LINELENGTH_DETECTOR'
        self.version = '1.0.0'
        self.dtype = [('event_start', 'int32'),
                      ('event_stop', 'int32')]