# utils.py

import pandas as pd

def preprocess_data(df_price, df_contracts):
    df_contracts['Base Index'] = df_contracts['Base Index'].str.upper().str.replace('PLATTS62', 'PLTTS62')

    def get_fe_ratio(row):
        if str(row['Typical Fe']).upper() == 'NOADJ':
            return 1
        else:
            return float(row['Typical Fe']) / 62

    df_contracts['Fe Adjustment Ratio'] = df_contracts.apply(get_fe_ratio, axis=1)
    df_contracts['Discount'] = df_contracts['Discount'].fillna(1)

    def compute_dmt(row):
        if row['Unit'] == 'DMT':
            return row['Quantity']
        else:
            return row['Quantity'] * (1 - row['Moisture'])

    df_contracts['DMT Quantity'] = df_contracts.apply(compute_dmt, axis=1)

    df_price['Tenor'] = pd.to_datetime(df_price['Tenor'])
    df_contracts['Tenor'] = pd.to_datetime(df_contracts['Tenor'])

    return df_price, df_contracts


def calculate_mtm(df_price, df_contracts):
    df_merged = pd.merge(df_contracts, df_price,
                         left_on=['Base Index', 'Tenor'],
                         right_on=['Index Name', 'Tenor'],
                         how='left')

    df_merged['MTM Value'] = (
        (df_merged['Price'] * df_merged['Fe Adjustment Ratio'] + df_merged['Cost']) *
        df_merged['Discount'] * df_merged['DMT Quantity']
    )
    return df_merged


def generate_reports(df_merged):
    detailed_report = df_merged[[
        'Contract_Ref', 'Counterparty', 'Base Index', 'Tenor', 'Price Date', 'Price',
        'Typical Fe', 'Cost', 'Discount', 'Fe Adjustment Ratio', 'Quantity', 'Unit',
        'DMT Quantity', 'MTM Value'
    ]]

    df_daily_mtm = df_merged.dropna(subset=['Price'])
    daily_report = df_daily_mtm.groupby('Price Date').agg(
        Total_MTM_Value=('MTM Value', 'sum'),
        Contract_Count=('Contract_Ref', 'count')
    ).reset_index().sort_values('Price Date')

    return detailed_report, daily_report
