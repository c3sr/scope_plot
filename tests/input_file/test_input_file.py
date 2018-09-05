import pytest

from scope_plot.specification import Specification
from scope_plot.specification import InputFileNotDefinedError

s = Specification({
    "input_file": "figure",
    "subplots": [
        {  # subplot 0
            "input_file": "subplot",
            "series": [
                {
                    "input_file": "series"
                },
                {},
            ],
        },
        {  # subplot 1
            "series": [
                {  # series 0

                }
            ]
        },
    ]
})

n = Specification({
    "subplots": [
        {
            "series": [
                {
                },
            ],
        },
    ]
})


def test_figure():
    assert s.subplots[1].series[0].input_file() == "figure"


def test_series():
    assert s.subplots[0].series[0].input_file() == "series"


def test_subplot():
    assert s.subplots[0].series[1].input_file() == "subplot"


def test_undefined():
    with pytest.raises(InputFileNotDefinedError):
        n.subplots[0].series[0].input_file()
