import json
from datetime import datetime, timezone
from pathlib import Path

RAW_PATH = Path(__file__).parent.parent / "leads_raw.json"
BRONZE_DIR = Path(__file__).parent
BRONZE_PATH = BRONZE_DIR / "leads_bronze.json"


def load_raw(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def unified_columns(records):
    columns = []
    seen = set()
    for record in records:
        for key in record:
            if key not in seen:
                seen.add(key)
                columns.append(key)
    return columns


def to_text(value):
    if value is None:
        return None
    return str(value)


def build_bronze(records):
    columns = unified_columns(records)
    ingested_at = datetime.now(timezone.utc).isoformat()
    bronze_rows = []
    for row_id, record in enumerate(records):
        row = {"_row_id": row_id, "_ingested_at": ingested_at}
        for col in columns:
            row[col] = to_text(record.get(col))
        bronze_rows.append(row)
    return bronze_rows


def validate_bronze(raw, bronze):
    assert len(raw) == len(bronze), "bronze deve ter uma linha por registro raw"
    expected_keys = set(bronze[0].keys())
    for row in bronze:
        assert set(row.keys()) == expected_keys, "schema inconsistente entre linhas"
        for key, value in row.items():
            if key in ("_row_id",):
                continue
            assert value is None or isinstance(value, str), f"coluna {key} não é text: {value!r}"


if __name__ == "__main__":
    raw = load_raw(RAW_PATH)
    bronze = build_bronze(raw)
    validate_bronze(raw, bronze)

    BRONZE_DIR.mkdir(exist_ok=True)
    with open(BRONZE_PATH, "w", encoding="utf-8") as f:
        json.dump(bronze, f, ensure_ascii=False, indent=2)

    print(f"raw: {len(raw)} registros | bronze: {len(bronze)} linhas | colunas: {list(bronze[0].keys())}")
    print(json.dumps(bronze[:3], ensure_ascii=False, indent=2))
