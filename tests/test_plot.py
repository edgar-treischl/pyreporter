import pandas as pd
from plotnine import ggplot

from pyreporter.plot import create_ggplot


def test_create_ggplot_ubb():
    """create_ggplot works with UBB=True."""

    data = pd.DataFrame({
        "label_short": [
            "Very satisfied with the service quality",
            "Satisfied overall",
            "Neutral response",
            "Dissatisfied with support",
            "Very dissatisfied experience",
        ] * 2,
        "vals": [
            "Positive",
            "Positive",
            "Positive",
            "Positive",
            "Positive",
            "Negative",
            "Negative",
            "Negative",
            "Negative",
            "Negative",
        ],
        "anz": [120, 95, 60, 30, 15, 20, 25, 40, 55, 70],
    })

    labels = pd.DataFrame({
        "labels": ["Positive", "Negative"],
        "colors": ["#4CAF50", "#F44336"],
    })

    plot = create_ggplot(data, ubb=True, labels=labels)

    assert isinstance(plot, ggplot)


def test_create_ggplot_non_ubb():
    """create_ggplot works with UBB=False."""

    data = pd.DataFrame({
        "vars": ["Q1", "Q2", "Q3", "Q4"],
        "label_short": [
            "Satisfaction with price",
            "Ease of use",
            "Recommendation likelihood",
            "Customer support quality",
        ],
        "vals": ["Agree", "Neutral", "Disagree", "Agree"],
        "p": [55, 25, 10, 65],
        "anz": [110, 50, 20, 130],
        "label_n": ["n=110", "n=50", "n=20", "n=130"],
    })

    labels = pd.DataFrame({
        "labels": ["Agree", "Neutral", "Disagree"],
        "colors": ["#2E7D32", "#9E9E9E", "#C62828"],
    })

    plot = create_ggplot(data, ubb=False, labels=labels)

    assert isinstance(plot, ggplot)