"""Time-lag MSD for independent experimental or simulated particle tracks."""

from dataclasses import dataclass

import numpy as np


@dataclass
class LagMSD:
    lag_frames: np.ndarray
    lag_time: np.ndarray
    mean: np.ndarray
    sem_across_tracks: np.ndarray
    valid_track_counts: np.ndarray


def time_averaged_msd(
    tracks: np.ndarray, frame_interval: float, max_lag: int | None = None
) -> LagMSD:
    """Compute lag MSD averaged first within each independent track.

    Parameters
    ----------
    tracks:
        Shape (n_frames, n_particles, 2), with x/y in physical or dimensionless
        length units. Use *unwrapped* tracks for periodic simulations.
        NaN entries indicate missing detections; missing track pairs are skipped.
    frame_interval:
        Time between sampled frames in matching time units.
    max_lag:
        Largest integer frame offset, default min(n_frames//3, 100).

    Notes
    -----
    We average squared displacements within one track before averaging
    independently tracked particles. SEM is across tracks, not falsely
    across heavily overlapping lagged windows.
    """
    xyz = np.asarray(tracks, dtype=float)
    if xyz.ndim != 3 or xyz.shape[2] != 2 or xyz.shape[0] < 4:
        raise ValueError("tracks must have shape (frames >= 4, particles, 2)")
    if xyz.shape[1] < 2:
        raise ValueError("at least two independent particle tracks required")
    if not np.isfinite(frame_interval) or frame_interval <= 0:
        raise ValueError("frame_interval must be finite and positive")
    if max_lag is None:
        max_lag = min(xyz.shape[0] // 3, 100)
    if not 1 <= max_lag < xyz.shape[0]:
        raise ValueError("max_lag must be between 1 and frames-1")

    mean = np.full(max_lag, np.nan, dtype=float)
    sem = np.full(max_lag, np.nan, dtype=float)
    counts = np.zeros(max_lag, dtype=int)

    for lag in range(1, max_lag + 1):
        difference = xyz[lag:] - xyz[:-lag]
        valid = np.isfinite(difference).all(axis=2)
        squared = np.sum(np.where(np.isfinite(difference), difference, 0.0)**2, axis=2)
        n_valid = np.sum(valid, axis=0)
        per_track = np.divide(
            np.sum(np.where(valid, squared, 0), axis=0),
            n_valid,
            out=np.full(xyz.shape[1], np.nan),
            where=n_valid > 0,
        )
        good = per_track[np.isfinite(per_track)]
        counts[lag - 1] = len(good)
        if len(good):
            mean[lag - 1] = float(np.mean(good))
        if len(good) >= 2:
            sem[lag - 1] = float(np.std(good, ddof=1) / np.sqrt(len(good)))

    lags = np.arange(1, max_lag + 1)
    return LagMSD(lags, lags * frame_interval, mean, sem, counts)
