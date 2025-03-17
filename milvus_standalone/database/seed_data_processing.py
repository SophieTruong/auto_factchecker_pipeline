import pandas as pd
import os
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

# Facepager data
FACEPAGER_DATA = os.getenv("FACEPAGER_DATA")
FINNISH_DATA = os.path.join(FACEPAGER_DATA, "fb_data_finnish.csv")
INTERNATIONAL_DATA = os.path.join(FACEPAGER_DATA, "fb_data_international_news_sources.csv")

# Finnish news media data
DATA_DIR = os.getenv("DATA_DIR")

print(f"FINNISH_DATA: {FINNISH_DATA}")
print(f"INTERNATIONAL_DATA: {INTERNATIONAL_DATA}")
print(f"DATA_DIR: {DATA_DIR}")

def process_facepager_data(data_path):
    src_df = pd.read_csv(data_path, delimiter=";")
    print(src_df.head())
    print(f"ORIGINAL src_df.shape: {src_df.shape}")
    
    # Drop rows where 'text' is empty
    src_df = src_df[src_df['message'].notna()]
    print(f"AFTER DROP NA src_df.shape: {src_df.shape}")
    print(f"AFTER DROP NA src_df.message.value_counts(): {src_df['message'].value_counts()}")
    
    # Drop rows where 'text' is duplicated
    src_df = src_df[~src_df.duplicated(subset=['message'])]
    print(f"AFTER DROP DUPLICATES src_df.shape: {src_df.shape}")
    print(f"AFTER DROP DUPLICATES src_df.id.value_counts(): {src_df['id'].value_counts()}")
    
    # Covert created_time to created_at
    src_df.loc[:, "created_time"] = pd.to_datetime(src_df["created_time"], utc=True)
    
    # Add source and url column
    src_df.loc[:, "source"] = [
        "Facebook posts from Finnish news media" if "path" not in src_df.columns else "Facebook posts from  International news media"
        for _ in range(src_df.shape[0])
    ]
    
    # Add url column
    src_df.loc[:, "url"] = [
        "" if "path" not in src_df.columns else src_df["path"]
        for _ in range(src_df.shape[0])
    ]
    
    df = src_df[['id', 'message', 'created_time', 'source', 'url']].copy()
    
    df.loc[:, "label"] = ["Nan" for _ in range(df.shape[0])]
    
    df.rename(columns={
        "message": "text",
        "created_time": "created_at",
        }, inplace=True)
    
    df = df[['id', 'text', 'label', 'source', 'url', 'created_at']]
    
    print(f"FINAL df.head(): {df.head(5)}")
    print(f"df.created_at.dtype: {df.created_at.dtype}")
    
    return df

def get_news_data(file_name):
    data_fn = os.path.join(DATA_DIR, file_name)
    data_df = pd.read_csv(data_fn) # id, author, text
    return data_df

def process_news_data(file_name):
    print(f"Processing {file_name}...")
    src_df = get_news_data(file_name)
    
    print(f"src_df.head(): {src_df.head()}")
    #src_df.columns: Index(['id', 'author', 'text', 'source', 'url', 'apiURL', 'headline'], dtype='object')
    print(f"src_df.columns: {src_df.columns}")
    print(f"src_df.shape: {src_df.shape}")
    
    # Remove rows where 'text' is empty
    src_df = src_df[src_df['text'].notna()]
    
    # Remove rows where 'text' is duplicated
    src_df = src_df[~src_df.duplicated(subset=['text'])]
    
    # Create label column
    src_df.loc[:, "label"] = ["Nan" for _ in range(src_df.shape[0])]
    
    # Create created_at column
    src_df.loc[:, "created_at"] = pd.to_datetime(src_df["createdAt"], utc=True)
    
    df = src_df[['id', 'text', 'label', 'source', 'url', 'created_at']]

    print(f"FINAL df.head(): {df.head(5)}")
    print(f"df.created_at.dtype: {df.created_at.dtype}")
    
    return df

def merge_all_data(test=False):
    dfs = []
    
    finnish_df = process_facepager_data(FINNISH_DATA)
    dfs.append(finnish_df)
    
    international_df = process_facepager_data(INTERNATIONAL_DATA)
    dfs.append(international_df)
    
    file_names = os.listdir(DATA_DIR)
    print("file_names: ", file_names)
    
    filtered_file_names = [fn for fn in file_names if (fn.endswith(".csv") and fn != "test.csv")]
    
    if test:
        filtered_file_names = filtered_file_names[:5]
    
    for file_name in filtered_file_names:
        
        df = process_news_data(file_name)
    
        dfs.append(df)
    
    df = pd.concat(dfs)
    
    print(f"FINAL df.head(): {df.head()}")
    print(f"FINAL df.shape: {df.shape}")
    
    return df


