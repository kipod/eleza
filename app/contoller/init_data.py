import os
import uuid
from datetime import datetime

import pandas as pd  # for manipulating data
import xgboost as xgb  # for building models
import pickle
import shap  # SHAP package
import matplotlib.pyplot as plt  # for custom graphs at the end

from app.logger import log


PATH_TO_RESULT = os.environ.get("PATH_TO_RESULT", "results")


def generate_bkg_exp(path_to_pkl, path_to_data):
    # LOAD PKL FILE
    xgb_model = None
    with open(path_to_pkl, "rb") as f:
        xgb_model = pickle.load(f)

    # Separate test (evaluation) dataset that doesn't include the output
    test_data = pd.read_csv(path_to_data)

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
    # fig = shap.summary_plot(shap_values_XGB_test, X_new, show=False)
    plot_file = os.path.join(PATH_TO_RESULT, f"plot_{file_uuid}.png")
    plt.savefig(plot_file)

    return background_file, explainer_file, plot_file
