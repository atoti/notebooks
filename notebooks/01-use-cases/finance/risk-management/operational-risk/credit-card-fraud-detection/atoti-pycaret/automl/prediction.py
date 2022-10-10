from flask import Flask, jsonify, request
import pandas as pd
import pycaret.classification as pyc
import pickle
import os

app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)


def predict(df):
    model = pyc.load_model("./automl/models/Final_LGBM_Model_20211130")
    return pyc.predict_model(model, data=df)


@app.route("/predict", methods=["POST"])
def predict_model():
    test = request.json

    features_json = test["features"]
    features_df = pd.read_json(features_json)
    print(f"Features received: {len(features_df)}")

    model_prediction = predict(features_df)
    print(f"Prediction completed for {len(model_prediction)}")

    return model_prediction.to_json(orient="records")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=105)
