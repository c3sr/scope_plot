import os
from scope_plot.specification import Specification

def test_red():
    s = Specification({
        "series": [
            {
                "color": "red"
            }
        ]
    })
    assert s.subplots[0].series[0].color_or(None) == "red"

def test_default():
    s = Specification({
        "series": [
            {
                "not-color": "red"
            }
        ]
    })
    assert s.subplots[0].series[0].color_or(3) == 3