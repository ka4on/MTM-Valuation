# utils.py

import pandas as pd

def preprocess_data(df_price, df_contracts):
    # 将合同表中的'Base Index'字段标准化为大写，并修正'PLATTS62'为'PLTTS62'
    df_contracts['Base Index'] = df_contracts['Base Index'].str.upper().str.replace('PLATTS62', 'PLTTS62')

    # 计算铁品位调整系数
    def get_fe_ratio(row):
        # 如果'Typical Fe'为'NOADJ'，返回1，否则按照铁含量/62计算
        if str(row['Typical Fe']).upper() == 'NOADJ':
            return 1
        else:
            return float(row['Typical Fe']) / 62

    df_contracts['Fe Adjustment Ratio'] = df_contracts.apply(get_fe_ratio, axis=1)
    # 缺失的Discount用1填充
    df_contracts['Discount'] = df_contracts['Discount'].fillna(1)

    # 计算干吨数量（DMT Quantity）
    def compute_dmt(row):
        # 如果单位是DMT，直接返回数量，否则按湿吨减去水分计算
        if row['Unit'] == 'DMT':
            return row['Quantity']
        else:
            return row['Quantity'] * (1 - row['Moisture'])

    df_contracts['DMT Quantity'] = df_contracts.apply(compute_dmt, axis=1)

    # 将价格表和合同表的Tenor字段转换为日期类型
    df_price['Tenor'] = pd.to_datetime(df_price['Tenor'])
    df_contracts['Tenor'] = pd.to_datetime(df_contracts['Tenor'])

    return df_price, df_contracts

def calculate_mtm(df_price, df_contracts):
    # 按'Base Index'和'Tenor'合并合同和价格表
    df_merged = pd.merge(df_contracts, df_price,
                         left_on=['Base Index', 'Tenor'],
                         right_on=['Index Name', 'Tenor'],
                         how='left')

    # 计算MTM Value（市值）
    df_merged['MTM Value'] = (
        (df_merged['Price'] * df_merged['Fe Adjustment Ratio'] + df_merged['Cost']) *
        df_merged['Discount'] * df_merged['DMT Quantity']
    )
    return df_merged

def generate_reports(df_merged):
    # 生成详细报告，包括合同、价格、数量等详细信息
    detailed_report = df_merged[[
        'Contract_Ref', 'Counterparty', 'Base Index', 'Tenor', 'Price Date', 'Price',
        'Typical Fe', 'Cost', 'Discount', 'Fe Adjustment Ratio', 'Quantity', 'Unit',
        'DMT Quantity', 'MTM Value'
    ]]

    # 生成按日聚合的MTM报告
    df_daily_mtm = df_merged.dropna(subset=['Price'])
    daily_report = df_daily_mtm.groupby('Price Date').agg(
        Total_MTM_Value=('MTM Value', 'sum'),
        Contract_Count=('Contract_Ref', 'count')
    ).reset_index().sort_values('Price Date')

    return detailed_report, daily_report
