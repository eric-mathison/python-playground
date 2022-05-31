import pandas as pd

def filter():
    df = pd.read_csv("emails.csv")
    v = df[df["MXRecords"].str.contains("outlook")]
    print(v)
    v.to_csv('outlook_emails.csv', index=False)