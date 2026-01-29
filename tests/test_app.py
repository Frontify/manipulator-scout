from .client import ClientContext
import pytest
import http


@pytest.mark.parametrize("client_context", ClientContext.all())
@pytest.mark.system
def test___app___stress_logs___extracts_data(client_context: ClientContext, logs_path):
    log_file = logs_path / "frontend-dark-manipulator-video-a-5d4cc5d99d-5cxxt-1767597371903079871.log"
    with client_context as client:
        response = client.post("/manipulator/logs/stress", files={"logs": log_file.read_bytes()})

    assert response.status_code == http.HTTPStatus.OK
