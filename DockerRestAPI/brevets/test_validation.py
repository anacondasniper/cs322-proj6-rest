import validation

def test_empty_list():
    assert validation.validate_controls([], 200) == "No controls to submit"

def test_good_controls():
    assert validation.validate_controls([{"km": "100"}, {"km": "200"}], 200) is None

def test_non_numeric_km():
    assert validation.validate_controls([{"km": "abc"}], 200) is not None

def test_missing_km():
    assert validation.validate_controls([{"miles": "10"}], 200) is not None

def test_negative_km():
    assert validation.validate_controls([{"km": "-5"}], 200) is not None

def test_over_20_percent():
    assert validation.validate_controls([{"km": "400"}], 300) is not None

def test_exactly_20_percent_is_ok():
    assert validation.validate_controls([{"km": "360"}], 300) is None
