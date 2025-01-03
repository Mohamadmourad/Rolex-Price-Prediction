import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.neighbors import KNeighborsRegressor
import matplotlib.pyplot as plt

df = pd.read_csv('watchesData - WorkSheet.csv')

df = df[df["Price"] != "Price on request"]
df["Number of Jewls"].fillna(0, inplace=True)
df = df.drop(columns=["Title", "Clasp", "Condition", "Diameter", "Rating", "Water Resistance"])
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df = df.dropna(subset=['Price'])
df['Number of Jewls'] = pd.to_numeric(df['Number of Jewls'], errors='coerce')
df = df.dropna(subset=['Number of Jewls'])
df['Year of Production'] = pd.to_numeric(df['Year of Production'], errors='coerce')
mostFrequentYear = df["Year of Production"].mode()[0]
df["Year of Production"].fillna(mostFrequentYear, inplace=True)
df['Gender'] = np.where(
    (df['Gender'] == "Mens watch/Unisex") | (df['Gender'] == "Womens watch"),
    df['Gender'], 
    np.nan
)
mostFrequentGender = df["Gender"].mode()[0]
df["Gender"].fillna(mostFrequentGender, inplace=True)
mostFrequentBraceletMaterial = df["Bracelet Material"].mode()[0]
df["Bracelet Material"].fillna(mostFrequentBraceletMaterial, inplace=True)
mostFrequentClaspMaterial = df["Clasp Material"].mode()[0]
df["Clasp Material"].fillna(mostFrequentClaspMaterial, inplace=True)

df.drop_duplicates(inplace=True)

label_encoder = LabelEncoder()
df['Model'] = label_encoder.fit_transform(df['Model'])
df['Case Material'] = label_encoder.fit_transform(df['Case Material'])
df['Bracelet Material'] = label_encoder.fit_transform(df['Bracelet Material'])
df['Gender'] = label_encoder.fit_transform(df['Gender'])
df['Clasp Material'] = label_encoder.fit_transform(df['Clasp Material'])

X = df.drop(columns=["Price"])
y = df["Price"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

best_n = 0
best_mse = float('inf')  
best_r2 = -float('inf')  
r2_scores = [] 
mse_scores = []

for n in range(1, 21): 
    knn_model = KNeighborsRegressor(n_neighbors=n)
    knn_model.fit(X_train, y_train)
    y_pred = knn_model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    mse_scores.append(mse)
    r2_scores.append(r2)
    
    if mse < best_mse:
        best_mse = mse
        best_n = n
        best_r2 = r2


model = KNeighborsRegressor(n_neighbors=best_n)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(f"Best Mean Squared Error: {best_mse}")
print(f"R2 Score for Best n: {best_r2}")

