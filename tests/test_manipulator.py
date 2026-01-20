import datetime

import pytest
import manipulator_scout.units
import manipulator_scout.manipulator as manip

convert_ms2s = manipulator_scout.units.ms2s


def test___evaluate_stress___known_logs___evaluates_expected_values(logs_path):
    filename = "frontend-dark-manipulator-video-a-7987c6f55b-tdn2f-1767626198764915579.log"
    df = manip.parse_logs((logs_path / filename).read_text())
    stress_objects = df.loc[df["object"] == "image"]
    earlist_timestamp_s = convert_ms2s((stress_objects["timestamp"] - stress_objects["time.total"]).min())
    latest_timestamp_s = convert_ms2s(stress_objects["timestamp"].max())
    processing_time_s = latest_timestamp_s - earlist_timestamp_s

    model = manip.evaluate_stress(df)

    assert model is not None
    assert model.info.server == "TwicPics/1.7.67"
    assert model.info.run_at == datetime.datetime.fromtimestamp(earlist_timestamp_s)
    assert model.requests.count == 561
    assert model.requests_per_second == pytest.approx(model.requests.count / processing_time_s)
    assert model.heartbeats is not None
    assert model.heartbeats.count == 182
