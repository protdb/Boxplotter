import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from template import template
from tempfile import gettempdir
from datetime import datetime
from typing import Literal

BASE_FONT_SIZE = 30

def plot_boxplots(
        df,
        subset_col,
        process_cols,
        plot_size_multiplier: float = 1,
        plot_mode: Literal['boxplot', 'violin'] = 'boxplot',
        log_y: bool = False
    ) -> dict[str, tuple[str, go.Figure]]:
    run_folder = os.path.join(gettempdir(), f'boxplots_{datetime.now().strftime("%Y%m%d%H%M%S")}')
    os.makedirs(run_folder, exist_ok=True)
    result = {}
    for col in process_cols:
        if plot_mode == "boxplot":
            fig = px.box(df, x=subset_col, y=col, log_y=log_y, color_discrete_sequence=['blue'])
        else:
            fig = px.violin(df, x=subset_col, y=col, log_y=log_y, color_discrete_sequence=['blue'])
        fig.update_layout(template=template)
        fig.update_layout(
            {
                'font': {'size': BASE_FONT_SIZE * plot_size_multiplier},
                'title': {'font': {'size': BASE_FONT_SIZE * plot_size_multiplier}},
            }
        )
        fig.update_annotations({'font': {'size': BASE_FONT_SIZE * plot_size_multiplier}})
        col_file_name = col
        for repl in '()*%/\\':
            col_file_name = col_file_name.replace(repl, '_')
        fig_path = os.path.join(run_folder, f'{col_file_name}.png')
        fig.write_image(fig_path, width=2400 * plot_size_multiplier, height=1200 * plot_size_multiplier)
        result[col] = (fig_path, fig)
    return result

