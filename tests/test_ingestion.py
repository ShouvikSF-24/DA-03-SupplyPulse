import sys
import csv
import json
import copy

import pytest

from src.ingestion import load_dataco
from src.ingestion import load_olist


class FakeResult:
    def __init__(self, rowcount):
        self.rowcount = rowcount


class FakeConnection:
    def __init__(self, fake_engine):
        self.fake_engine = fake_engine

   
    def execute(self, statement, parameters=None):
        if isinstance(parameters, list):
            rowcount = len(parameters)
        else:
            rowcount = 1

        # Store an independent snapshot of the parameters.
        # This prevents later batch.clear() calls from
        # changing the recorded test execution.
        self.fake_engine.executions.append(
            (statement, copy.deepcopy(parameters))
        )

        return FakeResult(rowcount)



class FakeTransaction:
    def __init__(self, fake_engine):
        self.fake_engine = fake_engine

    def __enter__(self):
        return FakeConnection(self.fake_engine)

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakeEngine:
    def __init__(self):
        self.executions = []

    def begin(self):
        return FakeTransaction(self)


def create_dataco_csv(path, rows):
    with open(
        path,
        mode="w",
        encoding="cp1250",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=load_dataco.ALLOWED_COLUMNS,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def create_olist_csv(path, rows):
    with open(
        path,
        mode="w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=load_olist.EXPECTED_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(rows)


def test_dataco_parse_integer():
    result = load_dataco.parse_value(
        "Order Id",
        "5001",
    )

    assert result == 5001
    assert isinstance(result, int)


def test_dataco_parse_float():
    result = load_dataco.parse_value(
        "Sales",
        "125.50",
    )

    assert result == 125.50
    assert isinstance(result, float)


def test_dataco_parse_empty_value():
    result = load_dataco.parse_value(
        "Product Name",
        "",
    )

    assert result is None


def test_dataco_loader_uses_batches_and_parses_records(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "dataco_test.csv"

    rows = []

    for index in range(1, 4):
        row = {
            column: ""
            for column in load_dataco.ALLOWED_COLUMNS
        }

        row["Order Item Id"] = str(1000 + index)
        row["Order Id"] = str(5000 + index)
        row["Sales"] = "125.50"
        row["Late_delivery_risk"] = "0"

        rows.append(row)

    create_dataco_csv(csv_path, rows)

    fake_engine = FakeEngine()

    monkeypatch.setattr(
        load_dataco,
        "DATA_FILE",
        csv_path,
    )

    monkeypatch.setattr(
        load_dataco,
        "engine",
        fake_engine,
    )

    monkeypatch.setattr(
        load_dataco,
        "BATCH_SIZE",
        2,
    )

    inserted = load_dataco.load_dataco()

    assert inserted == 3
    assert len(fake_engine.executions) == 2

    first_batch = fake_engine.executions[0][1]

    assert len(first_batch) == 2

    first_record = json.loads(
        first_batch[0]["source_data"]
    )

    assert first_record["Order Id"] == 5001
    assert first_record["Sales"] == 125.50
    assert first_record["Late_delivery_risk"] == 0


def test_dataco_rejects_missing_file(
    tmp_path,
    monkeypatch,
):
    missing_file = tmp_path / "missing_dataco.csv"

    monkeypatch.setattr(
        load_dataco,
        "DATA_FILE",
        missing_file,
    )

    with pytest.raises(FileNotFoundError):
        load_dataco.load_dataco()


def test_dataco_rejects_invalid_limit(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "dataco_test.csv"

    create_dataco_csv(csv_path, [])

    monkeypatch.setattr(
        load_dataco,
        "DATA_FILE",
        csv_path,
    )

    with pytest.raises(ValueError):
        load_dataco.load_dataco(limit=0)


def test_olist_loader_uses_batches(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "olist_test.csv"

    rows = [
        {
            "customer_id": f"customer_{index}",
            "customer_unique_id": f"unique_{index}",
            "customer_zip_code_prefix": str(10000 + index),
            "customer_city": "sao paulo",
            "customer_state": "SP",
        }
        for index in range(1, 4)
    ]

    create_olist_csv(csv_path, rows)

    fake_engine = FakeEngine()

    monkeypatch.setattr(
        load_olist,
        "DATA_FILE",
        csv_path,
    )

    monkeypatch.setattr(
        load_olist,
        "engine",
        fake_engine,
    )

    monkeypatch.setattr(
        load_olist,
        "BATCH_SIZE",
        2,
    )

    inserted = load_olist.load_olist()

    assert inserted == 3
    assert len(fake_engine.executions) == 2

    first_batch = fake_engine.executions[0][1]

    assert len(first_batch) == 2
    assert first_batch[0]["customer_id"] == "customer_1"
    assert first_batch[0]["customer_zip_code_prefix"] == 10001


def test_olist_rejects_missing_customer_identifier(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "olist_invalid.csv"

    rows = [
        {
            "customer_id": "",
            "customer_unique_id": "unique_1",
            "customer_zip_code_prefix": "10001",
            "customer_city": "sao paulo",
            "customer_state": "SP",
        }
    ]

    create_olist_csv(csv_path, rows)

    fake_engine = FakeEngine()

    monkeypatch.setattr(
        load_olist,
        "DATA_FILE",
        csv_path,
    )

    monkeypatch.setattr(
        load_olist,
        "engine",
        fake_engine,
    )

    with pytest.raises(ValueError, match="Missing customer identifier"):
        load_olist.load_olist()

    assert len(fake_engine.executions) == 0


def test_olist_rejects_invalid_limit(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "olist_test.csv"

    create_olist_csv(csv_path, [])

    monkeypatch.setattr(
        load_olist,
        "DATA_FILE",
        csv_path,
    )

    with pytest.raises(ValueError):
        load_olist.load_olist(limit=0)


def test_dataco_rejects_invalid_integer():
    with pytest.raises(ValueError):
        load_dataco.parse_value(
            "Order Id",
            "not_an_integer",
        )


def test_dataco_rejects_invalid_float():
    with pytest.raises(ValueError):
        load_dataco.parse_value(
            "Sales",
            "not_a_decimal",
        )


def test_dataco_rejects_missing_csv_columns(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "dataco_missing_columns.csv"

    with open(
        csv_path,
        mode="w",
        encoding="cp1250",
        newline="",
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(load_dataco.ALLOWED_COLUMNS[:-1])

    monkeypatch.setattr(
        load_dataco,
        "DATA_FILE",
        csv_path,
    )

    with pytest.raises(ValueError, match="Missing expected columns"):
        load_dataco.load_dataco()


def test_olist_rejects_unexpected_csv_columns(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "olist_wrong_columns.csv"

    with open(
        csv_path,
        mode="w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(load_olist.EXPECTED_COLUMNS[:-1])

    monkeypatch.setattr(
        load_olist,
        "DATA_FILE",
        csv_path,
    )

    with pytest.raises(ValueError, match="Unexpected CSV columns"):
        load_olist.load_olist()


def test_olist_rejects_invalid_zip_code(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "olist_invalid_zip.csv"

    rows = [
        {
            "customer_id": "customer_1",
            "customer_unique_id": "unique_1",
            "customer_zip_code_prefix": "invalid_zip",
            "customer_city": "sao paulo",
            "customer_state": "SP",
        }
    ]

    create_olist_csv(csv_path, rows)

    fake_engine = FakeEngine()

    monkeypatch.setattr(
        load_olist,
        "DATA_FILE",
        csv_path,
    )

    monkeypatch.setattr(
        load_olist,
        "engine",
        fake_engine,
    )

    with pytest.raises(ValueError):
        load_olist.load_olist()

    assert len(fake_engine.executions) == 0


class FailingConnection:
    def execute(self, statement, parameters=None):
        raise RuntimeError("Simulated database insertion failure")


class FailingTransaction:
    def __init__(self, engine):
        self.engine = engine

    def __enter__(self):
        return FailingConnection()

    def __exit__(self, exc_type, exc_value, traceback):
        self.engine.observed_exception = exc_type
        return False


class FailingEngine:
    def __init__(self):
        self.observed_exception = None

    def begin(self):
        return FailingTransaction(self)


def test_dataco_propagates_database_failure(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "dataco_failure.csv"

    row = {
        column: ""
        for column in load_dataco.ALLOWED_COLUMNS
    }

    row["Order Item Id"] = "1001"
    row["Order Id"] = "5001"
    row["Sales"] = "125.50"

    create_dataco_csv(csv_path, [row])

    failing_engine = FailingEngine()

    monkeypatch.setattr(
        load_dataco,
        "DATA_FILE",
        csv_path,
    )

    monkeypatch.setattr(
        load_dataco,
        "engine",
        failing_engine,
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated database insertion failure",
    ):
        load_dataco.load_dataco()

    assert failing_engine.observed_exception is RuntimeError


def test_olist_propagates_database_failure(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "olist_failure.csv"

    rows = [
        {
            "customer_id": "customer_1",
            "customer_unique_id": "unique_1",
            "customer_zip_code_prefix": "10001",
            "customer_city": "sao paulo",
            "customer_state": "SP",
        }
    ]

    create_olist_csv(csv_path, rows)

    failing_engine = FailingEngine()

    monkeypatch.setattr(
        load_olist,
        "DATA_FILE",
        csv_path,
    )

    monkeypatch.setattr(
        load_olist,
        "engine",
        failing_engine,
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated database insertion failure",
    ):
        load_olist.load_olist()

    assert failing_engine.observed_exception is RuntimeError


def test_dataco_cli_default_arguments(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["load_dataco.py"])

    args = load_dataco.parse_arguments()

    assert args.limit is None
    assert args.reset is False


def test_dataco_cli_custom_arguments(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["load_dataco.py", "--limit", "100", "--reset"],
    )

    args = load_dataco.parse_arguments()

    assert args.limit == 100
    assert args.reset is True


def test_olist_cli_default_arguments(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["load_olist.py"])

    args = load_olist.parse_arguments()

    assert args.limit is None
    assert args.reset is False


def test_olist_cli_custom_arguments(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["load_olist.py", "--limit", "100", "--reset"],
    )

    args = load_olist.parse_arguments()

    assert args.limit == 100
    assert args.reset is True


def test_dataco_rejects_empty_csv(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "empty_dataco.csv"
    csv_path.write_text("", encoding="cp1250")

    monkeypatch.setattr(
        load_dataco,
        "DATA_FILE",
        csv_path,
    )

    with pytest.raises(ValueError, match="CSV file has no header"):
        load_dataco.load_dataco()


def test_olist_rejects_empty_csv(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "empty_olist.csv"
    csv_path.write_text("", encoding="utf-8-sig")

    monkeypatch.setattr(
        load_olist,
        "DATA_FILE",
        csv_path,
    )

    with pytest.raises(ValueError, match="CSV file has no header"):
        load_olist.load_olist()


def test_dataco_reset_uses_mocked_database(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "dataco_reset.csv"
    create_dataco_csv(csv_path, [])

    fake_engine = FakeEngine()

    monkeypatch.setattr(load_dataco, "DATA_FILE", csv_path)
    monkeypatch.setattr(load_dataco, "engine", fake_engine)

    inserted = load_dataco.load_dataco(reset=True)

    assert inserted == 0
    assert len(fake_engine.executions) == 1

    reset_statement = str(fake_engine.executions[0][0])

    assert "TRUNCATE TABLE staging.dataco_raw" in reset_statement


def test_olist_reset_uses_mocked_database(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "olist_reset.csv"
    create_olist_csv(csv_path, [])

    fake_engine = FakeEngine()

    monkeypatch.setattr(load_olist, "DATA_FILE", csv_path)
    monkeypatch.setattr(load_olist, "engine", fake_engine)

    inserted = load_olist.load_olist(reset=True)

    assert inserted == 0
    assert len(fake_engine.executions) == 1

    reset_statement = str(fake_engine.executions[0][0])

    assert "TRUNCATE TABLE staging.olist_customers_raw" in reset_statement


def test_dataco_respects_record_limit(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "dataco_limit.csv"

    rows = []

    for index in range(1, 4):
        row = {
            column: ""
            for column in load_dataco.ALLOWED_COLUMNS
        }

        row["Order Item Id"] = str(1000 + index)
        row["Order Id"] = str(5000 + index)
        row["Sales"] = "125.50"

        rows.append(row)

    create_dataco_csv(csv_path, rows)

    fake_engine = FakeEngine()

    monkeypatch.setattr(load_dataco, "DATA_FILE", csv_path)
    monkeypatch.setattr(load_dataco, "engine", fake_engine)

    inserted = load_dataco.load_dataco(limit=1)

    assert inserted == 1
    assert len(fake_engine.executions) == 1

    payload = fake_engine.executions[0][1]

    assert len(payload) == 1


def test_olist_respects_record_limit(
    tmp_path,
    monkeypatch,
):
    csv_path = tmp_path / "olist_limit.csv"

    rows = [
        {
            "customer_id": f"customer_{index}",
            "customer_unique_id": f"unique_{index}",
            "customer_zip_code_prefix": str(10000 + index),
            "customer_city": "sao paulo",
            "customer_state": "SP",
        }
        for index in range(1, 4)
    ]

    create_olist_csv(csv_path, rows)

    fake_engine = FakeEngine()

    monkeypatch.setattr(load_olist, "DATA_FILE", csv_path)
    monkeypatch.setattr(load_olist, "engine", fake_engine)

    inserted = load_olist.load_olist(limit=1)

    assert inserted == 1
    assert len(fake_engine.executions) == 1

    payload = fake_engine.executions[0][1]

    assert len(payload) == 1
