import pandas as pd
import numpy as np


def clear_outliers(df: pd.DataFrame, cols, subset_col, treshold=10) -> tuple[pd.DataFrame, pd.DataFrame]:
    outliers = []
    for col in cols:
        mean = abs(df[col].median())
        for idx, row in df.iterrows():
            if abs(row[col]) > treshold * mean:
                outliers.append({
                    'index': idx,
                    'subset': row[subset_col],
                    'col': col,
                    'mean': mean,
                    'value': row[col]
                })
        df[col] = df[col].apply(lambda x: x if abs(x) < mean * treshold else np.nan)
    return df, pd.json_normalize(outliers)