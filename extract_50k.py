import pandas as pd

input_file = "Veremi_final_dataset.csv"   
output_file = "dataset_50k.csv"

df = pd.read_csv(input_file, nrows=50000)
df.to_csv(output_file, index=False)

print("Saved:", df.shape)
