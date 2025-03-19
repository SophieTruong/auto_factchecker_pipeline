import pandas as pd
import os
import dotenv
import re

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

def remove_emojis(text):
    """
    Remove emojis from text
    """
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', text) 

def process_facepager_data(data_path):
    src_df = pd.read_csv(data_path, delimiter=";")
    
    # Drop rows where 'text' is empty
    src_df = src_df[src_df['message'].notna()]
    
    # Drop rows where 'text' is duplicated
    src_df = src_df[~src_df.duplicated(subset=['message'])]
    print(f"AFTER DROP DUPLICATES src_df.shape: {src_df.shape}")
    
    # Remove emojis from text
    src_df.loc[:, "message"] = src_df["message"].apply(remove_emojis)
    
    # Remove text with length less than 10
    src_df = src_df[src_df["message"].str.len() > 10]
    
    # Covert created_time to created_at
    src_df.loc[:, "created_time"] = pd.to_datetime(src_df["created_time"], utc=True)
    
    # Add source and url column
    has_path = "path" in src_df.columns
    
    source = "Facebook posts from Finnish news media" if not has_path else "Facebook posts from International news media"
    src_df.loc[:, "source"] = [source for _ in range(src_df.shape[0])]
    
    # Add url column
    src_df.loc[:, "url"] = src_df["path"] if has_path else ["" for _ in range(src_df.shape[0])]
    
    df = src_df[['id', 'message', 'created_time', 'source', 'url']].copy()
    
    df.loc[:, "label"] = ["Nan" for _ in range(df.shape[0])]
    
    df.rename(columns={
        "message": "text",
        "created_time": "created_at",
        }, inplace=True)
    
    df = df[['id', 'text', 'label', 'source', 'url', 'created_at']]
    
    print(f"process_facepager_data df.shape: {df.shape}")
    
    return df

def get_news_data(file_name):
    data_fn = os.path.join(DATA_DIR, file_name)
    data_df = pd.read_csv(data_fn) # id, author, text
    return data_df

def process_news_data(file_name):

    src_df = get_news_data(file_name)
    
    #src_df.columns: Index(['id', 'author', 'text', 'source', 'url', 'apiURL', 'headline'], dtype='object')
    # print(f"src_df.shape: {src_df.shape}")
    
    # Remove rows where 'text' is empty
    src_df = src_df[src_df['text'].notna()]
    
    # Remove rows where 'text' is duplicated
    src_df = src_df[~src_df.duplicated(subset=['text'])]
    
    # Create label column
    src_df.loc[:, "label"] = ["None" for _ in range(src_df.shape[0])]
    
    # Create created_at column
    src_df.loc[:, "created_at"] = pd.to_datetime(src_df["createdAt"], utc=True)
    
    df = src_df[['id', 'text', 'label', 'source', 'url', 'created_at']]
    
    return df

def merge_all_data():
    dfs = []
    
    finnish_df = process_facepager_data(FINNISH_DATA)
    dfs.append(finnish_df)
    
    international_df = process_facepager_data(INTERNATIONAL_DATA)
    dfs.append(international_df)
    
    file_names = os.listdir(DATA_DIR)
    print("file_names: ", file_names)
    
    filtered_file_names = [fn for fn in file_names if (fn.endswith(".csv") and fn != "test.csv")]
        
    for file_name in filtered_file_names:
        
        df = process_news_data(file_name)
    
        dfs.append(df)
    
    df = pd.concat(dfs)
    
    print(f"merge_all_data df.head(): {df.head()}")
    print(f"merge_all_data df.shape: {df.shape}")
    
    return df


