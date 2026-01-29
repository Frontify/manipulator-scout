import datetime
import json

import numpy as np
import pandas as pd
import pydantic

import manipulator_scout.units

REQUEST_TIMEOUT_S = 60.0
HEARTBEAT_URL = "http://undefined/v1/placeholder:1x1:orange?hc=1"

convert_ms2s = manipulator_scout.units.ms2s
convert_s2ms = manipulator_scout.units.s2ms


class InfoModel(pydantic.BaseModel):
    server: str
    run_at: datetime.datetime


class HistogramBinModel(pydantic.BaseModel):
    upper_bin: float
    count: int


class StatisticModel(pydantic.BaseModel):
    count: int = 0
    mean: float = 0.0
    median: float = 0.0
    stddev: float = 0.0
    hist: list[HistogramBinModel] = []


class PercentileModel(pydantic.BaseModel):
    percentile: float
    value: float


class HeartBeatModel(pydantic.BaseModel):
    info: InfoModel
    period_accuracy: StatisticModel

    @pydantic.computed_field
    @property
    def version(self) -> int:
        return 1


class StressModel(pydantic.BaseModel):
    info: InfoModel
    in_time: int
    cancelled: int
    timing: list[PercentileModel]
    requests_per_second: float
    requests_period_accuracy: StatisticModel
    heartbeats_period_accuracy: StatisticModel

    @pydantic.computed_field
    @property
    def availability(self) -> float:
        if self.requests_period_accuracy.count > 0.0:
            return self.in_time / self.requests_period_accuracy.count
        return 0.0

    @pydantic.computed_field
    @property
    def version(self) -> int:
        return 1


def parse_logs(logs: str) -> pd.DataFrame:
    logs_as_json = "[" + ",".join(logs.split("\n")[:-1]) + "]"
    df = pd.json_normalize(json.loads(logs_as_json))
    return df


def analyze_timestamp_differences(ascending_timestamp_series: pd.Series) -> StatisticModel:
    diff = np.diff(ascending_timestamp_series)
    hist, bin_edges = np.histogram(diff, bins=10)
    return StatisticModel(
        count=len(ascending_timestamp_series),
        mean=float(np.mean(diff)),
        median=float(np.median(diff)),
        stddev=float(np.std(diff)),
        hist=[HistogramBinModel(upper_bin=float(b), count=int(c)) for (b, c) in zip(bin_edges[1:], hist)],
    )


def evaluate_heartbeat(
    df: pd.DataFrame,
) -> HeartBeatModel | None:
    heartbeats = df.loc[df["request.url"] == HEARTBEAT_URL]
    if not len(heartbeats):
        return None

    ascending_timestamps_s = heartbeats["timestamp"].map(convert_ms2s).sort_values()
    earliest_index = ascending_timestamps_s.index[0]
    earliest_timestamp_s = ascending_timestamps_s[earliest_index]
    beats = analyze_timestamp_differences(ascending_timestamps_s)
    info = InfoModel(
        server=heartbeats["response.headers.server"][earliest_index],
        run_at=datetime.datetime.fromtimestamp(earliest_timestamp_s),
    )
    return HeartBeatModel(info=info, period_accuracy=beats)


def evaluate_stress(df: pd.DataFrame) -> StressModel | None:
    stress_objects = df.loc[df["object"] == "image"]
    if not len(stress_objects):
        return None

    time_total = stress_objects["time.total"]
    image_in_time = (time_total < convert_s2ms(REQUEST_TIMEOUT_S)).sum()
    ascending_timestamps_s = (stress_objects["timestamp"] - time_total).map(convert_ms2s).sort_values()
    earliest_index = ascending_timestamps_s.index[0]
    earliest_timestamp_s = ascending_timestamps_s[earliest_index]
    latest_timestamp_s = convert_ms2s(stress_objects["timestamp"].max())
    processing_time_s = latest_timestamp_s - earliest_timestamp_s
    quantiles = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1.0]
    quantile_values = time_total.quantile(q=quantiles)
    info = InfoModel(
        server=stress_objects["response.headers.server"][earliest_index],
        run_at=datetime.datetime.fromtimestamp(earliest_timestamp_s),
    )
    heartbeat = evaluate_heartbeat(df) or HeartBeatModel(info=info, period_accuracy=StatisticModel())
    model = StressModel(
        info=info,
        in_time=image_in_time,
        cancelled=stress_objects["cancelled"].sum(),
        timing=[
            PercentileModel(percentile=p, value=v) for (p, v) in zip(quantiles, quantile_values.map(convert_ms2s))
        ],
        requests_per_second=len(stress_objects) / processing_time_s,
        requests_period_accuracy=analyze_timestamp_differences(ascending_timestamps_s),
        heartbeats_period_accuracy=heartbeat.period_accuracy,
    )
    return model
