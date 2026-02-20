import pandas as pd
import numpy as np

# Import your function here

from pyreporter.plot import create_ggplot
from pyreporter.utils import get_metadata, get_sname


# -------------------------------------------------
# Dummy Data for UBB = TRUE
# -------------------------------------------------

data_ubb = pd.DataFrame({
    "label_short": [
        "Very satisfied with the service quality",
        "Satisfied overall",
        "Neutral response",
        "Dissatisfied with support",
        "Very dissatisfied experience"
    ] * 2,
    "vals": ["Positive"] * 5 + ["Negative"] * 5,
    "anz": [120, 95, 60, 30, 15, 20, 25, 40, 55, 70]
})

labels = {
    "labels": ["Positive", "Negative"],
    "colors": ["#4CAF50", "#F44336"]
}


# -------------------------------------------------
# Dummy Data for UBB = FALSE
# -------------------------------------------------

data_non_ubb = pd.DataFrame({
    "vars": ["Q1", "Q2", "Q3", "Q4"],
    "label_short": [
        "Satisfaction with price",
        "Ease of use",
        "Recommendation likelihood",
        "Customer support quality"
    ],
    "vals": ["Agree", "Neutral", "Disagree", "Agree"],
    "p": [55, 25, 10, 65],
    "anz": [110, 50, 20, 130],
    "label_n": ["n=110", "n=50", "n=20", "n=130"]
})

labels_non_ubb = {
    "labels": ["Agree", "Neutral", "Disagree"],
    "colors": ["#2E7D32", "#9E9E9E", "#C62828"]
}


# -------------------------------------------------
# Run Tests
# -------------------------------------------------

if __name__ == "__main__":

    #print("Testing UBB=True plot...")
    #plot1 = create_ggplot(data_ubb, ubb=True, labels=labels)
    #plot1.show()

    print("Testing UBB=False plot...")
    plot2 = create_ggplot(data_non_ubb, ubb=False, labels=labels_non_ubb)
    plot2.show()