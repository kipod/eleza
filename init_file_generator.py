#!/usr/local/bin/python
import os
import sys

import uuid
from datetime import datetime

import click

import pandas as pd  # for manipulating data
import xgboost as xgb  # for building models
import pickle
import shap  # SHAP package
import matplotlib.pyplot as plt  # for custom graphs at the end

from app.logger import log

PATH_TO_RESULT = os.path.abspath(os.environ.get("PATH_TO_RESULT", "results"))
log.set_level(log.ERROR)


@click.command()
@click.option('--file-pkl', prompt='Model', help='Path to model file.')
@click.option('--file-data', prompt='Testing Dataset', help='Path to Testing Dataset file.')
def generator(file_pkl, file_data):
    """Simple program that greets NAME for a total of COUNT times."""

# LOAD PKL FILE
    xgb_model = None
    try:
        xgb_model = pickle.load(open(file_pkl, 'rb'))
    except Exception:
        sys.stderr.write(
            "The model file uploaded cannot be parsed."
            " Please check you have uploaded the correct file."
        )
        return

    # Separate test (evaluation) dataset that doesn't include the output
    test_data = None
    try:
        test_data = pd.read_csv(file_data)
    except Exception:
        sys.stderr.write(
            "The Testing Dataset file uploaded cannot be parsed."
            " Please check you have uploaded the correct file."
        )
        return

    # Choose the same columns you trained the model with
    start_time = datetime.now()
    X_new = test_data[test_data.columns]
    ypred = xgb_model.predict(xgb.DMatrix(X_new))
    test_data["predictions"] = ypred
    file_uuid = str(uuid.uuid4())
    background_file = os.path.join(PATH_TO_RESULT, f"background_{file_uuid}.csv")
    test_data.to_csv(background_file)
    log(log.DEBUG, "Prediction. Took time: [%s]", datetime.now() - start_time)

    explainerXGB = shap.TreeExplainer(xgb_model)
    shap_values_XGB_test = explainerXGB.shap_values(X_new)

    df_shap_XGB_test = pd.DataFrame(shap_values_XGB_test, columns=X_new.columns.values)
    explainer_file = os.path.join(PATH_TO_RESULT, f"explainer_{file_uuid}.csv")
    df_shap_XGB_test.to_csv(explainer_file)

    # PLOT
    # load JS visualization code to notebook
    shap.initjs()

    # summarize the effects of all the features
    shap.summary_plot(shap_values_XGB_test, X_new, show=False)
    plot_file = os.path.join(PATH_TO_RESULT, f"plot_{file_uuid}.png")
    plt.savefig(plot_file, bbox_inches='tight')

    print(background_file)
    print(explainer_file)
    print(plot_file)


if __name__ == '__main__':
    generator()
