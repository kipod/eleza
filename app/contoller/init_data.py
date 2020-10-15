import os
import uuid
from datetime import datetime

import pandas as pd  # for manipulating data
import xgboost as xgb  # for building models
import pickle
import shap  # SHAP package
import matplotlib.pyplot as plt  # for custom graphs at the end

from app.logger import log


PATH_TO_RESULT = os.path.abspath(os.environ.get("PATH_TO_RESULT", "results"))


class ParsingError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def generate_bkg_exp(file_pkl, file_data):
    # LOAD PKL FILE
    try:
        xgb_model = pickle.load(file_pkl)
    except Exception:
        raise ParsingError(
            "The model file uploaded cannot be parsed."
            " Please check you have uploaded the correct file."
        )

    # Separate test (evaluation) dataset that doesn't include the output
    try:
        test_data = pd.read_csv(file_data)
    except Exception:
        raise ParsingError(
            "The Testing Dataset file uploaded cannot be parsed."
            " Please check you have uploaded the correct file."
        )

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

    return background_file, explainer_file, plot_file
