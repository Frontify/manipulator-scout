import typing
import fastapi

from manipulator_scout import manipulator

app = fastapi.FastAPI()


@app.post("/manipulator/logs/stress")
async def post_stress_logs(logs: fastapi.UploadFile):
    df = manipulator.parse_logs((await logs.read()).decode())
    return manipulator.evaluate_stress(df)
