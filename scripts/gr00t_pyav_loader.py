"""Replace Isaac-GR00T's video frame loader with PyAV (libdav1d) so AV1 LeRobot datasets load without decord/torchcodec."""

import av
import numpy as np

from gr00t.data import dataset as D
from gr00t.utils import video as V


def _decode(path, want_ts=None):
    with av.open(path) as c:
        s = c.streams.video[0]
        s.thread_type = "AUTO"
        tb = float(s.time_base)
        frames, ts = [], []
        for f in c.decode(s):
            frames.append(f.to_ndarray(format="rgb24"))
            ts.append(f.pts * tb)
            if want_ts is not None and ts[-1] > want_ts + 0.5:
                break
    return np.stack(frames), np.array(ts)


def get_frames_by_timestamps(video_path, timestamps, video_backend="pyav", video_backend_kwargs={}):
    timestamps = np.asarray(timestamps, dtype=float)
    frames, ts = _decode(video_path, want_ts=timestamps.max())
    idx = np.abs(ts[:, None] - timestamps[None, :]).argmin(axis=0)
    return frames[idx]


def get_all_frames(video_path, video_backend="pyav", video_backend_kwargs={}):
    return _decode(video_path)[0]


def install():
    for mod in (D, V):
        mod.get_frames_by_timestamps = get_frames_by_timestamps
        mod.get_all_frames = get_all_frames
    print("[pyav] video frames decoded with PyAV", flush=True)
