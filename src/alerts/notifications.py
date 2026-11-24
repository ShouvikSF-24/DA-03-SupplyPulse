"""Slack and email notifications for SupplyPulse anomalies."""

import json
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ANOMALY_FILE = (
    PROJECT_ROOT / "data" / "processed" / "anomaly_detection_results.csv"
)
HISTORY_FILE = (
    PROJECT_ROOT / "data" / "processed" / "alert_history.json"
)

REQUIRED_COLUMNS = {
    "anomaly_type", "entity_id", "entity_name",
    "event_date", "observed_value", "z_score",
    "is_anomaly", "severity",
}


def load_anomalies():
    if not ANOMALY_FILE.exists():
        raise FileNotFoundError(
            f"Anomaly results not found: {ANOMALY_FILE}"
        )

    return pd.read_csv(ANOMALY_FILE)


def get_new_anomalies(data, channel):
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Missing anomaly columns: {sorted(missing)}")

    history = {}
    if HISTORY_FILE.exists():
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            history = json.load(file)

    sent_keys = set(history.get(channel, []))

    anomalies = data.copy()
    anomalies["is_anomaly"] = (
        anomalies["is_anomaly"].astype(str).str.lower() == "true"
    )

    anomalies = anomalies[
        anomalies["is_anomaly"]
        & (anomalies["severity"].str.upper() == "HIGH")
    ].copy()

    anomalies["alert_key"] = (
        anomalies["anomaly_type"].astype(str) + "|"
        + anomalies["entity_id"].astype(str) + "|"
        + anomalies["event_date"].astype(str) + "|"
        + anomalies["observed_value"].astype(str)
    )

    return anomalies[
        ~anomalies["alert_key"].isin(sent_keys)
    ], history


def save_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    temporary_file = HISTORY_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)

    temporary_file.replace(HISTORY_FILE)


def format_alert_message(anomalies):
    lines = [
        "SUPPLYPULSE - HIGH SEVERITY ANOMALY ALERT",
        f"New anomalies detected: {len(anomalies)}",
        "",
    ]

    for _, row in anomalies.iterrows():
        lines.extend([
            f"Type: {row['anomaly_type']}",
            f"Entity: {row['entity_name']} (ID: {row['entity_id']})",
            f"Date: {row['event_date']}",
            f"Observed value: {row['observed_value']}",
            f"Z-score: {float(row['z_score']):.2f}",
            f"Severity: {row['severity']}",
            "",
        ])

    return "\n".join(lines)


def send_slack_alert(data, webhook_url=None):
    webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

    if not webhook_url:
        return "SKIPPED: Slack webhook not configured"

    new_anomalies, history = get_new_anomalies(data, "slack")

    if new_anomalies.empty:
        return "NO NEW ANOMALIES: Slack"

    message = format_alert_message(new_anomalies)

    response = requests.post(
        webhook_url,
        json={"text": message},
        timeout=15,
    )
    response.raise_for_status()

    sent_keys = set(history.get("slack", []))
    sent_keys.update(new_anomalies["alert_key"].tolist())
    history["slack"] = sorted(sent_keys)
    save_history(history)

    return f"SENT: Slack ({len(new_anomalies)} anomalies)"


def send_email_alert(data):
    host = os.getenv("SMTP_HOST")
    port = os.getenv("SMTP_PORT", "587")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("ALERT_EMAIL_FROM")
    recipients = [
        address.strip()
        for address in os.getenv("ALERT_EMAIL_TO", "").split(",")
        if address.strip()
    ]

    if not all([host, sender, recipients]):
        return "SKIPPED: Email SMTP configuration incomplete"

    new_anomalies, history = get_new_anomalies(data, "email")

    if new_anomalies.empty:
        return "NO NEW ANOMALIES: Email"

    message = EmailMessage()
    message["Subject"] = (
        f"SupplyPulse: {len(new_anomalies)} High Severity Anomalies"
    )
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(format_alert_message(new_anomalies))

    with smtplib.SMTP(host, int(port), timeout=20) as server:
        server.starttls()
        if username:
            if not password:
                raise ValueError(
                    "SMTP_PASSWORD is required when SMTP_USERNAME is set."
                )
            server.login(username, password)
        server.send_message(message)

    sent_keys = set(history.get("email", []))
    sent_keys.update(new_anomalies["alert_key"].tolist())
    history["email"] = sorted(sent_keys)
    save_history(history)

    return f"SENT: Email ({len(new_anomalies)} anomalies)"


def run_alerts():
    data = load_anomalies()

    print("\n========== SUPPLYPULSE ALERT DISPATCH ==========")
    print("Anomaly records loaded:", len(data))

    slack_result = send_slack_alert(data)
    print(slack_result)

    email_result = send_email_alert(data)
    print(email_result)

    return {
        "slack": slack_result,
        "email": email_result,
    }


if __name__ == "__main__":
    run_alerts()
