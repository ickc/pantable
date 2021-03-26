from __future__ import annotations

from logging import getLogger

logger = getLogger('pantable')

try:
    from numba import jit
except ImportError:
    logger.warning('Consider `pip install numba` to speed up `transpose`.')

    def jit(func, *args, **kwargs):
        return func

import numpy as np


@jit('int64[:, :, :, ::1](int64[:, :, :, ::1])', nopython=True, nogil=True)
def transpose(data: np.ndarray[np.int64]) -> np.ndarray[np.int64]:
    m, n = data.shape[:2]
    res = np.empty((n, m, 2, 2), dtype=np.int64)
    for i in range(m):
        for j in range(n):
            res[j, i, 1, 1] = data[i, j, 0, 0]
            res[j, i, 1, 0] = data[i, j, 0, 1]
            res[j, i, 0, 1] = data[i, j, 1, 0]
            res[j, i, 0, 0] = data[i, j, 1, 1]
    return res
