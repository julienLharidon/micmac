from pymicmac.core.tapioca import extract_tie_points


def test_extract_tie_points():
    result = extract_tie_points("test.tif")
    assert "image_id" in result
    assert result["image_id"] == "test.tif"
    assert result["number_of_features"] == 1000
    assert "processing_time" in result
    assert len(result["points"]) == 1000
