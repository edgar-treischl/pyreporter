import pandas as pd

data = pd.read_pickle("tests/fake_data_0001.pkl")
data.to_csv("fake_data_delete.csv", index=False)

print("\nWrote fake_data_0001.csv")
