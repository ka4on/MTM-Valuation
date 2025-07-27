# main.py

import os
import pandas as pd
from config import INPUT_EXCEL_PATH, OUTPUT_DETAILED_REPORT, OUTPUT_DAILY_REPORT
from utils import preprocess_data, calculate_mtm, generate_reports

def main():
    if not os.path.exists(INPUT_EXCEL_PATH):
        raise FileNotFoundError(f"Input file not found: {INPUT_EXCEL_PATH}")

    xls = pd.ExcelFile(INPUT_EXCEL_PATH)
    df_price = xls.parse('Price')
    df_contracts = xls.parse('Contracts')

    df_price, df_contracts = preprocess_data(df_price, df_contracts)
    df_merged = calculate_mtm(df_price, df_contracts)
    detailed_report, daily_report = generate_reports(df_merged)

    os.makedirs(os.path.dirname(OUTPUT_DETAILED_REPORT), exist_ok=True)
    detailed_report.to_excel(OUTPUT_DETAILED_REPORT, index=False)
    daily_report.to_excel(OUTPUT_DAILY_REPORT, index=False)
    print("✅ Reports generated successfully.")

if __name__ == "__main__":
    main()
