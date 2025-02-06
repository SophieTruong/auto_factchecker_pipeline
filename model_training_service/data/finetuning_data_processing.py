from datetime import datetime

import argparse

import pandas as pd

import aiohttp

def parse_args():
    """
    Parse command line arguments
    Args:
        source_db_url (str): The URL of the source database
        db_table_name (str): The name of the table to read from
        start_date (str): The start date of the date range to read from
        end_date (str): The end date of the date range to read from
        target_file_path (str): The path to save the processed data 
    Returns:
        args: The parsed command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_data_url", type=str, required=True)
    parser.add_argument("--start_date", type=str, required=True)
    parser.add_argument("--end_date", type=str, required=True)
    parser.add_argument("--target_file_path", type=str, default="data/finetuning_data.parquet")
    return parser.parse_args()

async def fetch_data_from_api(url: str, start_date: datetime, end_date: datetime):
    """
    Fetch data from the API
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"start_date": start_date, "end_date": end_date}) as response:
            return await response.json()

async def main():
    
    args = parse_args()
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    print(f"table_name: {args.db_table_name}, start_date: {start_date}, end_date: {end_date}")
    
    data_json = await fetch_data_from_api(args.source_data_url, start_date, end_date)
    df = pd.DataFrame(data_json)
    print(df.head())
    
    if df is not None:
        df.to_parquet(args.target_file_path)
    else:
        print(f"ERROR fetching data from {args.db_table_name} between {start_date} and {end_date}")

if __name__ == "__main__":
    main()