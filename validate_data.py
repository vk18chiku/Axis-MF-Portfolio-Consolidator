# Data validation script
# checks quality of generated CSV files

import pandas as pd
import os
from datetime import datetime


class DataValidator:
    
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        
    def get_latest_csv_files(self):
        files = {}
        
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.output_dir, filename)
                
                if 'equity' in filename and 'all' not in filename:
                    files['equity'] = filepath
                elif 'debt' in filename and 'all' not in filename:
                    files['debt'] = filepath
                elif 'all_holdings' in filename:
                    files['all'] = filepath
        
        return files
    
    def validate_data_quality(self, df, data_type):
        # perform data quality checks
        print(f"\n{'='*80}")
        print(f"DATA QUALITY REPORT - {data_type.upper()}")
        print(f"{'='*80}")
        
        print(f"\n📏 Basic Statistics:")
        print(f"  Total Records: {len(df)}")
        print(f"  Total Columns: {len(df.columns)}")
        
        print(f"\n🔍 Missing Value Analysis:")
        missing = df.isnull().sum()
        missing_pct = (df.isnull().sum() / len(df)) * 100
        
        for col in df.columns:
            if missing[col] > 0:
                print(f"  {col}: {missing[col]} ({missing_pct[col]:.2f}%)")
        

        print(f"\n📈 Unique Value Counts:")
        print(f"  Unique AMCs: {df['amc_name'].nunique()}")
        print(f"  Unique Schemes: {df['scheme_name'].nunique()}")
        print(f"  Unique Instruments: {df['instrument_name'].nunique()}")
        if 'instrument_type' in df.columns:
            print(f"  Instrument Types: {df['instrument_type'].nunique()}")
        
        if 'isin' in df.columns:
            valid_isin = df['isin'].notna()
            print(f"\n📋 ISIN Analysis:")
            print(f"  Records with ISIN: {valid_isin.sum()} ({(valid_isin.sum()/len(df)*100):.2f}%)")
            print(f"  Records without ISIN: {(~valid_isin).sum()} ({((~valid_isin).sum()/len(df)*100):.2f}%)")
            
            if valid_isin.any():
                isin_lengths = df[valid_isin]['isin'].str.len()
                invalid_format = (isin_lengths != 12).sum()
                if invalid_format > 0:
                    print(f"  ⚠ Invalid ISIN format: {invalid_format}")
        
        if 'portfolio_percentage' in df.columns:
            print(f"\n💰 Portfolio Percentage Analysis:")
            print(f"  Min: {df['portfolio_percentage'].min():.4f}%")
            print(f"  Max: {df['portfolio_percentage'].max():.4f}%")
            print(f"  Mean: {df['portfolio_percentage'].mean():.4f}%")
            print(f"  Median: {df['portfolio_percentage'].median():.4f}%")
            
            outliers = df[df['portfolio_percentage'] > 50]
            if len(outliers) > 0:
                print(f"  ⚠ Holdings > 50%: {len(outliers)}")
        

        print(f"\n📑 Scheme-level Analysis:")
        scheme_counts = df.groupby('scheme_name').size().sort_values(ascending=False)
        print(f"  Top 5 schemes by holdings count:")
        for scheme, count in scheme_counts.head(5).items():
            print(f"    - {scheme[:50]}...: {count} holdings")
        
        if 'portfolio_percentage' in df.columns:
            print(f"\n🏆 Top 10 Holdings by Percentage:")
            top_holdings = df.nlargest(10, 'portfolio_percentage')[
                ['scheme_name', 'instrument_name', 'portfolio_percentage']
            ]
            for idx, row in top_holdings.iterrows():
                scheme_short = row['scheme_name'][:30]
                instrument_short = row['instrument_name'][:40]
                print(f"    {row['portfolio_percentage']:.2f}% - {instrument_short} ({scheme_short})")
        
        print(f"\n🔧 Data Type Validation:")
        print(f"  String fields: amc_name, scheme_name, instrument_name")
        print(f"  Numeric fields: portfolio_percentage")
        print(f"  Date fields: reporting_date")
        
        duplicates = df.duplicated(subset=['scheme_name', 'instrument_name']).sum()
        if duplicates > 0:
            print(f"\n⚠ Warning: {duplicates} potential duplicate holdings found")
        
        print(f"\n{'='*80}")
    
    def generate_insights(self, equity_df, debt_df):
        # generate insights from data
        print(f"\n{'='*80}")
        print("INVESTMENT INSIGHTS")
        print(f"{'='*80}")
        

        total_holdings = len(equity_df) + len(debt_df)
        print(f"\n📊 Overall Portfolio Statistics:")
        print(f"  Total Holdings: {total_holdings}")
        print(f"  Equity Holdings: {len(equity_df)} ({len(equity_df)/total_holdings*100:.1f}%)")
        print(f"  Debt Holdings: {len(debt_df)} ({len(debt_df)/total_holdings*100:.1f}%)")
        
        if not equity_df.empty:
            print(f"\n🔝 Most Popular Equity Instruments:")
            top_equity = equity_df['instrument_name'].value_counts().head(10)
            for instrument, count in top_equity.items():
                print(f"    {count} schemes hold: {instrument}")
        
        if not debt_df.empty:
            print(f"\n🔝 Most Popular Debt Instruments:")
            top_debt = debt_df['instrument_name'].value_counts().head(10)
            for instrument, count in top_debt.items():
                print(f"    {count} schemes hold: {instrument[:60]}")
        
        print(f"\n{'='*80}")
    
    def run_validation(self):
        print("\n" + "="*80)
        print("PORTFOLIO DATA VALIDATION & ANALYSIS")
        print("="*80)
        
        files = self.get_latest_csv_files()
        
        if not files:
            print("✗ No CSV files found in output directory")
            return
        
        print(f"\n✓ Found {len(files)} CSV file(s) to validate")
        
        equity_df = None
        debt_df = None
        
        if 'equity' in files:
            print(f"\n📂 Loading: {files['equity']}")
            equity_df = pd.read_csv(files['equity'])
            self.validate_data_quality(equity_df, "Equity Holdings")
        
        if 'debt' in files:
            print(f"\n📂 Loading: {files['debt']}")
            debt_df = pd.read_csv(files['debt'])
            self.validate_data_quality(debt_df, "Debt Holdings")
        
        if 'all' in files:
            print(f"\n📂 Loading: {files['all']}")
            all_df = pd.read_csv(files['all'])
            self.validate_data_quality(all_df, "All Holdings")
        
        if equity_df is not None and debt_df is not None:
            self.generate_insights(equity_df, debt_df)
        
        print("\n✅ VALIDATION COMPLETE")
        print("="*80)


def main():
    validator = DataValidator(output_dir="output")
    validator.run_validation()


if __name__ == "__main__":
    main()
