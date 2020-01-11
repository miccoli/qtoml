#!python3

from hypothesis import given
import hypothesis.strategies as s
from hypothesis.extra.pytz import timezones

from test_tomltest import patch_floats

import qtoml

@s.composite
def single_type_lists(draw, types=s.integers()):
    """Create lists drawn from only one of the types generated by the argument
    strategy.

    """
    v = draw(types)
    if isinstance(v, list) and len(v) > 0:
        es = s.lists(s.from_type(type(v[0])))
    else:
        es = s.from_type(type(v))
    vl = draw(s.lists(es))
    return vl

toml_vals = s.recursive(
    s.text() | s.integers() | s.floats() | s.booleans() |
    s.datetimes(timezones=s.none() | timezones()) |
    s.dates() | s.times(),
    lambda leaves: (single_type_lists(leaves) |
                    s.dictionaries(s.text(), leaves)))

# Top-level TOML element must be a dict
toml_data = s.dictionaries(s.text(), toml_vals)

@given(toml_data)
def test_circular_encode(data):
    assert patch_floats(qtoml.loads(qtoml.dumps(data))) == patch_floats(data)

@given(s.text())
def test_string_encode(data):
    obj = {'key': data}
    assert qtoml.loads(qtoml.dumps(obj)) == obj
