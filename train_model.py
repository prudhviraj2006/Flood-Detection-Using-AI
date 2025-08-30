import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import pickle

data = {
    'humidity': [75, 82, 90, 65, 95],
    'distance': [30, 25, 10, 50, 8],
    'water': [400, 700, 950, 200, 980],
    'flood': [0, 1, 1, 0, 1]
}

df = pd.DataFrame(data)
X = df[['humidity', 'distance', 'water']]
y = df['flood']

model = DecisionTreeClassifier()
model.fit(X, y)

with open("flood_model.pkl", "wb") as f:
    pickle.dump(model, f)
