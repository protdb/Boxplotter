import pandas as pd
import numpy as np
from itertools import combinations
from typing import Any
import copy
from smart_round import smart_round

from scipy.stats import mannwhitneyu, ttest_ind, false_discovery_control

STATISTIC_OPTIONS = {
    'values': ['count', 'mean', 'median', 'std', 'max', 'min', 'median±std'],
    'indep_methods': ['Mann-Whitney U', 'Student indep. T'],
    'fdc_methods': ['Benjamini-Hochberg', 'Bonferroni', 'None']
}


def apply_fdc(values: dict[str, float | None], method: str) -> dict[str, float | None]:
    if method == 'None':
        return values
    res = copy.deepcopy(values)
    good_keys = []
    good_values = []
    for k, v in values.items():
        if v is not None and v is not str and not np.isnan(v):
            good_keys.append(k)
            good_values.append(v)
    if len(good_keys) <= 1:
        return res
    print(good_keys)
    print(good_values)
    if method == 'Benjamini-Hochberg':
        pvals = false_discovery_control(good_values)
    elif method == 'Bonferroni':
        pvals = [x * len(good_values) for x in good_values]
    else:
        raise ValueError(f'Method {method} not supported')
    for i in range(len(good_keys)):
        res[good_keys[i]+'_corr'] = pvals[i]
    return res

def get_pval(list1: Any, list2: Any, method: str) -> float | None:
    if method == 'Student indep. T':
        try:
            return ttest_ind(list1, list2).pvalue
        except:
            return None
    elif method == 'Mann-Whitney U':
        try:
            return mannwhitneyu(list1, list2).pvalue
        except:
            return None
    else:
        raise ValueError(f'Method {method} not recognized')

def get_p_values(df: pd.DataFrame, method: str, fdc_method: str, one_vs_all: bool = False) -> dict:
    if 'subset' not in df.columns:
        raise ValueError('No subset column')
    if 'value' not in df.columns:
        raise ValueError('No value column')
    subsets = df['subset'].unique()
    res = {}
    pairs = combinations(subsets, 2)
    for p1, p2 in pairs:
        d1 = df.query('subset == @p1')['value'].dropna()
        d2 = df.query('subset == @p2')['value'].dropna()
        pval = get_pval(d1, d2, method)
        res[f'{p1}||{p2}'] = pval
    if one_vs_all:
        for p1 in subsets:
            d1 = df.query('subset == @p1')['value'].dropna()
            d2 = df.query('subset != @p1')['value'].dropna()
            res[f'{p1}||All'] = get_pval(d1, d2, method)
    return apply_fdc(res, fdc_method)


def pvals_for_df(df: pd.DataFrame, subset_col, process_cols, method, fdc_method, one_vs_all) -> pd.DataFrame:
    results = []
    for col in process_cols:
        sub_df = df[[subset_col, col]].rename(columns={subset_col: 'subset', col: 'value'})
        res = {
            'column': col,
        }
        res.update(get_p_values(sub_df, method, fdc_method, one_vs_all))
        results.append(res)
    return pd.json_normalize(results)


def get_stat_values(df: pd.DataFrame, stat_values: list[str]) -> dict:
    if 'subset' not in df.columns:
        raise ValueError('No subset column')
    if 'value' not in df.columns:
        raise ValueError('No value column')
    res = {}
    for subset in df['subset'].unique():
        sub_df = df.query('subset == @subset')['value']
        if 'count' in stat_values:
            res[f'{subset}_count'] = len(sub_df.dropna())
        if 'mean' in stat_values:
            res[f'{subset}_mean'] = sub_df.mean()
        if 'median' in stat_values:
            res[f'{subset}_median'] = sub_df.median()
        if 'std' in stat_values:
            res[f'{subset}_std'] = sub_df.std()
        if 'max' in stat_values:
            res[f'{subset}_max'] = sub_df.max()
        if 'min' in stat_values:
            res[f'{subset}_min'] = sub_df.min()
        if 'median±std' in stat_values:
            res[subset] = f"{smart_round(sub_df.median(), 2)}±{smart_round(sub_df.std(), 2)}"
    return res


def stats_for_df(df: pd.DataFrame, subset_col, process_cols, stat_values) -> pd.DataFrame:
    results = []
    for col in process_cols:
        sub_df = df[[subset_col, col]].rename(columns={subset_col: 'subset', col: 'value'})
        res = {
            'column': col,
        }
        res.update(get_stat_values(sub_df, stat_values))
        results.append(res)
    return pd.json_normalize(results)