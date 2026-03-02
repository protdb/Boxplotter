from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import pandas as pd
from typing import Any
from io import BytesIO

DEFAULT_WIDTH = 170
DEFAULT_HEIGHT = 86

def make_document(
        context: dict,
        pval_df: pd.DataFrame,
        stat_df: pd.DataFrame,
        plots: dict[str, tuple[str, Any]],
        plot_size_multiplier
) -> bytes:
    merge_df = pd.merge(stat_df, pval_df, on='column')
    columns = []
    template = DocxTemplate('template.docx')
    for _, row in merge_df.iterrows():
        col_data = {
            'name': row['column'],
            'plot_image': InlineImage(
                template,
                plots[row['column']][0],
                width=Mm(DEFAULT_WIDTH * plot_size_multiplier if plot_size_multiplier <= 1 else DEFAULT_WIDTH),
                height=Mm(DEFAULT_HEIGHT * plot_size_multiplier if plot_size_multiplier <= 1 else DEFAULT_HEIGHT)
            ),
            'value_list': [{'name': k, 'value': v} for k,v in row.to_dict().items() if k != 'column']
        }
        columns.append(col_data)
    context['columns'] = columns
    template.render(context)
    out = BytesIO()
    template.save(out)
    return out.getvalue()