from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score, recall_score

import pandas as pd
import numpy as np


def churn_prediction(
    algorithm,
    training_x,
    testing_x,
    training_y,
    testing_y,
    cols,
    cf,
    threshold_plot,
    coefs_or_features=False,
):

    # model
    predictions = algorithm.predict(testing_x)
    probabilities = algorithm.predict_proba(testing_x)
    # Added by Ariel
    predictions_train = algorithm.predict(training_x)
    probabilities_train = algorithm.predict_proba(training_x)

    # coeffs
    if cf == "coefficients" and coefs_or_features:
        coefficients = pd.DataFrame(algorithm.coef_.ravel())
    elif cf == "features" and coefs_or_features:
        coefficients = pd.DataFrame(algorithm.feature_importances_)
    # Added by Ariel
    else:
        coefficients = None

    column_df = pd.DataFrame(cols)

    if coefficients is not None:
        coef_sumry = pd.merge(
            coefficients, column_df, left_index=True, right_index=True, how="left"
        )
        coef_sumry.columns = ["coefficients", "features"]
        coef_sumry = coef_sumry.sort_values(by="coefficients", ascending=False)

    print(
        "-------------------------------------------------------------------------------"
    )
    print(algorithm)
    print(
        "-------------------------------------------------------------------------------"
    )
    print()
    print(
        "\n Classification report - test : \n",
        classification_report(testing_y, predictions),
    )
    print("F1 score - test : ", round(f1_score(testing_y, predictions), 2))

    # confusion matrix
    conf_matrix = confusion_matrix(testing_y, predictions)
    # roc_auc_score
    model_roc_auc = roc_auc_score(testing_y, predictions)
    print("ROC AUC - test: ", round(model_roc_auc, 2), "\n")
    fpr, tpr, thresholds = roc_curve(testing_y, probabilities[:, 1])
    print()
    print(
        "                ---------------------------------                             "
    )
    print()

    # Added by Ariel
    print(
        "\n Classification report - train: \n",
        classification_report(training_y, predictions_train),
    )
    print("F1 score - train: ", round(f1_score(training_y, predictions_train), 2))

    # confusion matrix
    conf_matrix_train = confusion_matrix(training_y, predictions_train)
    # roc_auc_score
    model_roc_auc_train = roc_auc_score(training_y, predictions_train)
    print("ROC AUC - train: ", round(model_roc_auc_train, 2), "\n")
    fpr, tpr, thresholds = roc_curve(training_y, probabilities_train[:, 1])

    return algorithm


def churn_prediction_alg(
    algorithm, training_x, testing_x, training_y, testing_y, threshold_plot=True
):
    # model
    algorithm.fit(training_x, training_y.values.ravel())
    predictions = algorithm.predict(testing_x)
    probabilities = algorithm.predict_proba(testing_x)

    print(algorithm)
    print(
        "\n Classification report : \n", classification_report(testing_y, predictions)
    )
    print("Accuracy Score   : ", accuracy_score(testing_y, predictions))
    # confusion matrix
    conf_matrix = confusion_matrix(testing_y, predictions)
    # roc_auc_score
    model_roc_auc = roc_auc_score(testing_y, predictions)
    print("Area under curve : ", model_roc_auc)
    fpr, tpr, thresholds = roc_curve(testing_y, probabilities[:, 1])

    return algorithm
