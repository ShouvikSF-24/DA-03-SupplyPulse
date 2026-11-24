import pandas as pd
import pytest

from src.alerts import notifications


@pytest.fixture
def anomaly_data():
    return pd.DataFrame({
        "anomaly_type": ["DEMAND_SPIKE", "DEMAND_SPIKE"],
        "entity_id": [235, 564],
        "entity_name": ["Product A", "Product B"],
        "event_date": ["2015-04-01", "2016-03-01"],
        "observed_value": [66, 72],
        "z_score": [3.16, 3.24],
        "is_anomaly": [True, True],
        "severity": ["HIGH", "HIGH"],
    })


def test_slack_skips_without_webhook(anomaly_data, monkeypatch):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)

    result = notifications.send_slack_alert(anomaly_data)

    assert result.startswith("SKIPPED")


def test_email_skips_without_configuration(anomaly_data, monkeypatch):
    for key in [
        "SMTP_HOST", "ALERT_EMAIL_FROM", "ALERT_EMAIL_TO"
    ]:
        monkeypatch.delenv(key, raising=False)

    result = notifications.send_email_alert(anomaly_data)

    assert result.startswith("SKIPPED")


def test_slack_sends_new_anomalies(
    anomaly_data, monkeypatch, tmp_path
):
    monkeypatch.setattr(notifications, "HISTORY_FILE", tmp_path / "history.json")
    monkeypatch.setattr(notifications, "save_history", lambda history: None)

    class FakeResponse:
        def raise_for_status(self):
            pass

    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["payload"] = json
        return FakeResponse()

    monkeypatch.setattr(notifications.requests, "post", fake_post)

    result = notifications.send_slack_alert(
        anomaly_data,
        webhook_url="https://example.com/webhook",
    )

    assert result == "SENT: Slack (2 anomalies)"
    assert "Product A" in captured["payload"]["text"]


def test_sent_anomalies_are_not_repeated(
    anomaly_data, monkeypatch, tmp_path
):
    history_file = tmp_path / "history.json"
    history_file.write_text(
        '{"slack": ["DEMAND_SPIKE|235|2015-04-01|66"]}',
        encoding="utf-8",
    )

    monkeypatch.setattr(notifications, "HISTORY_FILE", history_file)

    new_anomalies, _ = notifications.get_new_anomalies(
        anomaly_data, "slack"
    )

    assert len(new_anomalies) == 1
    assert new_anomalies.iloc[0]["entity_id"] == 564


def test_normal_records_do_not_trigger_alerts(
    anomaly_data, monkeypatch, tmp_path
):
    monkeypatch.setattr(notifications, "HISTORY_FILE", tmp_path / "history.json")

    anomaly_data["is_anomaly"] = False

    new_anomalies, _ = notifications.get_new_anomalies(
        anomaly_data, "slack"
    )

    assert new_anomalies.empty
