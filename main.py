import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.neighbors import KNeighborsRegressor
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import json

df = pd.read_csv('watchesData - WorkSheet.csv')

df = df[df["Price"] != "Price on request"]
df["Number of Jewls"] = df["Number of Jewls"].fillna(0)
df = df.drop(columns=["Title", "Clasp", "Condition", "Diameter", "Rating", "Water Resistance"])
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df = df.dropna(subset=['Price'])
df['Number of Jewls'] = pd.to_numeric(df['Number of Jewls'], errors='coerce')
df = df.dropna(subset=['Number of Jewls'])
df['Year of Production'] = pd.to_numeric(df['Year of Production'], errors='coerce')
mostFrequentYear = df["Year of Production"].mode()[0]
df["Year of Production"] = df["Year of Production"].fillna(mostFrequentYear)
df['Gender'] = np.where(
    (df['Gender'] == "Mens watch/Unisex") | (df['Gender'] == "Womens watch"),
    df['Gender'],
    np.nan
)
mostFrequentGender = df["Gender"].mode()[0]
df["Gender"] = df["Gender"].fillna(mostFrequentGender)
mostFrequentBraceletMaterial = df["Bracelet Material"].mode()[0]
df["Bracelet Material"] = df["Bracelet Material"].fillna(mostFrequentBraceletMaterial)
mostFrequentClaspMaterial = df["Clasp Material"].mode()[0]
df["Clasp Material"] = df["Clasp Material"].fillna(mostFrequentClaspMaterial)

df.drop_duplicates(inplace=True)

label_encoders = {
    "Model": LabelEncoder(),
    "Case Material": LabelEncoder(),
    "Bracelet Material": LabelEncoder(),
    "Gender": LabelEncoder(),
    "Clasp Material": LabelEncoder()
}

for column, encoder in label_encoders.items():
    df[column] = encoder.fit_transform(df[column])

def convert_mapping(mapping):
    """Convert all keys and values in the mapping to standard Python types."""
    return {str(k): int(v) for k, v in mapping.items()}

mappings = {
    column: convert_mapping(dict(zip(encoder.classes_, encoder.transform(encoder.classes_))))
    for column, encoder in label_encoders.items()
}

with open("mappings.json", "w") as f:
    json.dump(mappings, f)

X = df.drop(columns=["Price"])
y = df["Price"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

best_n = 0
best_mse = float('inf')
best_r2 = -float('inf')

for n in range(1, 21):
    knn_model = KNeighborsRegressor(n_neighbors=n)
    knn_model.fit(X_train, y_train)
    y_pred = knn_model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    if mse < best_mse:
        best_mse = mse
        best_n = n
        best_r2 = r2

model = KNeighborsRegressor(n_neighbors=best_n)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Best Mean Squared Error: {mean_squared_error(y_test, y_pred)}")
print(f"R2 Score: {r2_score(y_test, y_pred)}")

initial_type = [("float_input", FloatTensorType([None, X.shape[1]]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)

with open("knn_model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())
