import streamlit as st
import pandas as pd

from outliers import clear_outliers
from stat_calculator import STATISTIC_OPTIONS, stats_for_df, pvals_for_df
from boxplotter import plot_boxplots
from make_document import make_document
from io import BytesIO
from mimetypes import guess_type
from smart_round import smart_round_dataframe



uploaded_file = st.file_uploader("Input XLSX file")
sheets = None
sheet_name = None
submitted = None
if uploaded_file is None:
    if 'results' in st.session_state:
        del st.session_state['results']
else:
    with st.form('Set sheet parameters'):
        skip_rows = st.number_input("Number of rows to skip", min_value=0, value=0)
        sheet_name = st.selectbox("Sheet", pd.ExcelFile(uploaded_file).sheet_names)
        read_options = st.form_submit_button("Read file")
    if skip_rows is not None and sheet_name is not None:
        with pd.ExcelFile(uploaded_file) as f:
            df = pd.read_excel(f, sheet_name=sheet_name, skiprows=skip_rows)
        with st.expander("Preview", expanded=True):
            st.write(df)
        with st.form("get plots"):
            results = {}
            output_file_name = st.text_input(
                'Out file name',
                value=uploaded_file.name.replace('.xlsx', '')+('' if sheet_name in ('Лист1', 'Sheet1') else f'_{sheet_name}'))
            columns = df.columns.tolist()
            subset_column = st.selectbox("Subset column", columns)
            process_columns = st.multiselect("Data columns", columns, default=columns)
            p_value_type = st.radio("p-value calculation type", STATISTIC_OPTIONS['indep_methods'])
            fdc = st.radio("False discovery control method", STATISTIC_OPTIONS['fdc_methods'])
            one_vs_all_pval = st.checkbox("One vs All Pvalue", value=False)
            round_vals = st.checkbox("Round values", value=True)
            plot_type = st.radio("Plot type", ['violin', 'boxplot'])
            log_y = st.checkbox("Log y axis", value=False)
            plot_size_multiplier = st.selectbox(
                "Plot size (1 is full width of A4 page with 300dpi)",
                [1.0, 0.5, 2.0],

            )
            # use_log_y = st.checkbox("Logarifm on y axis", value=False)
            stat_values = st.multiselect(
                "Stat values", STATISTIC_OPTIONS['values'],
                default=STATISTIC_OPTIONS['values']
            )
            remove_outliers = st.checkbox("Remove outliers", value=False)
            outliers_treshold = st.number_input("Outlier treshold, times of column mean", value=10)
            submitted = st.form_submit_button("Submit")
        if submitted:
            with st.status("Processing", expanded=True) as status:
                if remove_outliers:
                    df, outliers_df = clear_outliers(df, process_columns, subset_column, outliers_treshold)
                st.write('calculating stats...')
                results['stats_df'] = stats_for_df(df, subset_column, process_columns, stat_values)
                st.write('calculating p-values...')
                results['pvals_df'] = pvals_for_df(df, subset_column, process_columns, p_value_type, fdc, one_vs_all_pval)
                st.write('preparing plots...')
                results['plots'] = plot_boxplots(
                    df,
                    subset_column,
                    process_columns,
                    plot_size_multiplier,
                    plot_type,
                    log_y
                )
                st.write('making downloadable documents...')
                res_xlsx = BytesIO()
                if round_vals:
                    results['stats_df'] = smart_round_dataframe(results['stats_df'])
                    results['pvals_df'] = smart_round_dataframe(results['pvals_df'])
                with pd.ExcelWriter(res_xlsx) as writer:
                    results['stats_df'].to_excel(writer, sheet_name='Statistics', index=False)
                    results['pvals_df'].to_excel(writer, sheet_name='P-values', index=False)
                    if remove_outliers:
                        outliers_df.to_excel(writer, sheet_name='Outliers', index=False)
                results['excel_out'] = res_xlsx.getvalue()
                results['docx_out'] = make_document(
                    {
                        'file_name': uploaded_file.name,
                        'sheet_name': sheet_name,
                        'subset_column': subset_column,
                        'subsets': list(df[subset_column].unique()),
                        'fdc': fdc,
                        'p_value_type': p_value_type
                    },
                    results['pvals_df'],
                    results['stats_df'],
                    results['plots'],
                    plot_size_multiplier,
                )
                status.update(
                    label="Processing complete!", state="complete", expanded=False
                )
                st.session_state.results = results
        if 'results' in st.session_state:
            results = st.session_state.results
            with st.expander("Stats data", expanded=True):
                st.write('Statistics')
                st.write(results['stats_df'])
                st.write('P-values')
                st.write(results['pvals_df'])
            current_plot = st.selectbox("Plot", results['plots'].keys())
            st.plotly_chart(results['plots'][current_plot][1], use_container_width=True)
            st.download_button(
                "Download XLSX table",
                results['excel_out'],
                file_name=output_file_name+'_stats.xlsx',
                mime=guess_type('test.xlsx')[0]
            )
            st.download_button(
                "Download DOCX report",
                results['docx_out'],
                file_name=output_file_name+'_report.docx',
                mime=guess_type('test.docx')[0]
            )