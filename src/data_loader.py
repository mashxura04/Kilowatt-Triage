
import csv
from pathlib import Path


DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "retrofit_data.csv"
)

SOURCE_REGISTER_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "source_register.csv"
)

REQUIRED_COLUMNS = {
    "climate_zone",
    "intervention",
    "reported_energy_saving_kwh",
    "reported_saving_basis",
    "fuel_saved_tonnes",
    "fuel_saved_m3",
    "additional_electricity_kwh",
    "investment_cost_usd",
    "applicability",
    "source_year",
}

SOURCE_REGISTER_REQUIRED_COLUMNS = {
    "intervention",
    "source_document",
    "source_table",
    "source_year",
    "reported_unit",
    "energy_basis",
    "interpretation",
    "limitations",
}

VALID_BASES = {
    "thermal",
    "electrical",
    "fuel_switch_unresolved",
}

OPTIONAL_NUMERIC_COLUMNS = {
    "fuel_saved_tonnes",
    "fuel_saved_m3",
    "additional_electricity_kwh",
}


def parse_optional_number(value):
    if value == "":
        return None

    return float(value)


def load_data(file_path=DATA_FILE):
    rows = []

    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file is empty.")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"Missing CSV columns: {sorted(missing_columns)}"
            )

        for row in reader:
            row["climate_zone"] = int(row["climate_zone"])
            row["reported_energy_saving_kwh"] = float(
                row["reported_energy_saving_kwh"]
            )
            row["investment_cost_usd"] = float(
                row["investment_cost_usd"]
            )
            row["source_year"] = int(row["source_year"])

            for column in OPTIONAL_NUMERIC_COLUMNS:
                row[column] = parse_optional_number(row[column])

            rows.append(row)

    validate_data(rows)

    return rows


def validate_data(rows):
    if len(rows) != 24:
        raise ValueError("Expected exactly 24 records.")

    zones = {row["climate_zone"] for row in rows}

    if zones != {1, 2, 3, 4}:
        raise ValueError("Expected climate zones 1, 2, 3, and 4.")

    seen = set()

    for row in rows:
        key = (row["climate_zone"], row["intervention"])

        if key in seen:
            raise ValueError(f"Duplicate intervention record: {key}")

        seen.add(key)

        if row["reported_saving_basis"] not in VALID_BASES:
            raise ValueError(
                f"Invalid saving basis: {row['reported_saving_basis']}"
            )

        if row["reported_energy_saving_kwh"] < 0:
            raise ValueError("Energy savings cannot be negative.")

        if row["investment_cost_usd"] <= 0:
            raise ValueError("Investment cost must be positive.")

        for column in OPTIONAL_NUMERIC_COLUMNS:
            value = row[column]

            if value is not None and value < 0:
                raise ValueError(f"{column} cannot be negative.")


def load_source_register(
    file_path=SOURCE_REGISTER_FILE,
    data_rows=None,
):
    if data_rows is None:
        data_rows = load_data()

    rows = []

    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("Source register CSV file is empty.")

        missing_columns = (
            SOURCE_REGISTER_REQUIRED_COLUMNS - set(reader.fieldnames)
        )

        if missing_columns:
            raise ValueError(
                "Missing source register columns: "
                f"{sorted(missing_columns)}"
            )

        for row in reader:
            try:
                row["source_year"] = int(row["source_year"])
            except (TypeError, ValueError):
                raise ValueError(
                    "Source register years must be valid integers."
                ) from None

            rows.append(row)

    validate_source_register(rows, data_rows)

    return rows


def validate_source_register(rows, data_rows):
    expected_interventions = {
        row["intervention"] for row in data_rows
    }

    if len(rows) != len(expected_interventions):
        raise ValueError(
            "Source register must contain exactly one entry "
            "for each intervention."
        )

    seen = set()

    dataset_basis = {}
    dataset_year = {}

    for row in data_rows:
        name = row["intervention"]

        dataset_basis.setdefault(
            name,
            set()
        ).add(row["reported_saving_basis"])

        dataset_year.setdefault(
            name,
            set()
        ).add(row["source_year"])

    for row in rows:
        name = row["intervention"]

        if name in seen:
            raise ValueError(
                f"Duplicate source register entry: {name}"
            )

        seen.add(name)

        for column in SOURCE_REGISTER_REQUIRED_COLUMNS:
            if not str(row.get(column, "")).strip():
                raise ValueError(
                    f"Source register field '{column}' "
                    f"cannot be blank for {name}."
                )

        if name not in expected_interventions:
            raise ValueError(
                f"Unexpected source register intervention: {name}"
            )

        if row["energy_basis"] not in VALID_BASES:
            raise ValueError(
                f"Invalid source register energy basis: "
                f"{row['energy_basis']}"
            )

        if dataset_basis[name] != {row["energy_basis"]}:
            raise ValueError(
                f"Energy basis mismatch for {name}."
            )

        if dataset_year[name] != {row["source_year"]}:
            raise ValueError(
                f"Source year mismatch for {name}."
            )

    missing = expected_interventions - seen

    if missing:
        raise ValueError(
            f"Missing source register entries: {sorted(missing)}"
        )


def get_interventions_by_zone(climate_zone):
    if climate_zone not in {1, 2, 3, 4}:
        raise ValueError("Climate zone must be between 1 and 4.")

    rows = load_data()

    return [
        row for row in rows
        if row["climate_zone"] == climate_zone
    ]
