try:
    import numpy as np
except ImportError:
    np = None
try:
    import pandas as pd
except ImportError:
    pd = None


def smart_round(i: float, tail: int = 2, tail_always: bool = False) -> float:
    if np is not None:
        if np.isnan(i):
            return np.nan
    if i == 0:
        return 0.0
    if abs(i) >= 1:
        return round(i, tail)
    c_tail = 0
    while round(i, c_tail) == 0:
        c_tail += 1
    if tail_always:
        return round(i, tail+c_tail)
    else:
        return round(i, max(tail, c_tail))


def smart_round_deci(i: float | None, tail=2, tail_always: bool = False, nan: str = '') -> float:
    if np is not None:
        if np.isnan(i):
            return nan
    if i is None:
        return nan
    return smart_round(i, tail, tail_always)


def smart_round_dataframe(df, tail=2, tail_always: bool = False, nan: str = ''):
    if pd is None:
        raise ImportError('you need pandas installed!')
    for flo_col in df.select_dtypes(include='float').columns:
        df[flo_col] = df[flo_col].apply(lambda x: smart_round_deci(x, tail, tail_always, nan))
    return df
