
import pandas as pd

df = pd.read_csv("data/flat/aapl_chain_flat.csv")
print("Columns:", df.columns.tolist())
print("Unique underlyings:", df["underlying"].unique()[:5])
print("Unique expiries:", df["expiry"].unique()[:10])
