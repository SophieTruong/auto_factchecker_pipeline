import os
import pandas as pd
from sklearn.model_selection import train_test_split

from datasets import Dataset

classes=[0,1]
classes0 = ['Ei_tarkistettavissa_oleva_väite', 'Määrä', 'Ennuste', 'Korrelaatio/kaussatio', 'Lait/toimintasäännot', 'Muu', 'Henkilökohtainen_kokemus']

num_classes = len(classes)

def get_text_label(path):

    print(f"path = {path}")
    files=['Dana_annotation_1000_sentences_Henna.csv', 'DIME_claim_annotation_1000_sentences_Minttu.csv', 'DIME_claim_annotation_500_sentences_Pipsa.csv'] #, '3xNCS.json']
    
    fns = [os.path.join(path, f) for f in files]
    
    assert len(fns) == 3
    assert os.path.exists(fns[0])
    assert os.path.exists(fns[1])
    assert os.path.exists(fns[2])
    
    # Open and read the JSON file
    data1 = pd.read_csv(fns[0], sep=';')
    
    data2 = pd.read_csv(fns[1], sep=';')
    
    data3 = pd.read_csv(fns[2], sep=';')
    
    data3=data3[:501]
    
    datasets=[data1, data2, data3]
    texts=[]
    labels=[]
    
    for item in datasets:
        
        try:
            newtext=item['Lauseet']
        except:
            newtext=item['sentences']
        newlab=item['Kategoria']
        
        for it in newtext:
            if it == '':
                pass
            else:
                texts.append(it)
        for lab in newlab:
            if lab=='Ei_tarkistettavissa_oleva_väite':
                labels.append(0)    
            elif lab=='Henkilökohtainen_kokemus':
                labels.append(0)    
            elif lab=='Muu':
                labels.append(0)  
            elif lab=='':
                pass
            else:
                labels.append(1)
    
    print(labels)
    print(texts[0])
    return texts, labels

def get_data_splits(state_x, texts, labels):
    state_r=state_x

    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.3, random_state=state_r) #10 has been run
    X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, test_size=0.5, random_state=state_r)

    test_scores=y_test
    
    print(len(X_train))
    X_tr=[]
    y_train_n=[]
    i =0
    for item in X_train:
        new = str(item)
        X_tr.append(new)
        y_train_n.append(y_train[i])
        i+=1

    
    X_te=[]
    y_test_n=[]
    test_scores2=[]
    i =0
    for item in X_test:
        new = str(item)
        X_te.append(new)
        y_test_n.append(y_test[i])
        i+=1

    X_va=[]
    y_val_n=[]
    i =0
    for item in X_val:
        new = str(item)
        X_va.append(new)
        y_val_n.append(y_val[i])
        i+=1

    traind = pd.DataFrame()
    traind['Label'] = y_train_n
    traind['Text'] = X_tr
    train_df = traind[['Text', 'Label']]
    train_df.columns = ['text', 'label']

    testd = pd.DataFrame()
    testd['Label'] = y_test_n
    testd['Text'] = X_te
    test_df1 = testd[['Text', 'Label']]
    test_df1.columns = ['text', 'label']

    vald = pd.DataFrame()
    vald['Label'] = y_val_n
    vald['Text'] = X_va
    dev_df = vald[['Text', 'Label']]
    dev_df.columns = ['text', 'label']

    return train_df, test_df1, dev_df, test_scores2

def encode_labels(record):
    return {"label": [record[feature] for feature in classes]}


def shape_data(train_df, test_df1, dev_df, multi_label):
    train_ds = Dataset.from_dict(train_df)
    dev_ds = Dataset.from_dict(dev_df)
    test_ds1 = Dataset.from_dict(test_df1)
    
    if multi_label:
        train_ds = train_ds.map(encode_labels)
        test_ds1 = test_ds1.map(encode_labels)

    test_df = test_df1
    test_ds = test_ds1

    return train_ds, test_ds, dev_ds, test_df
