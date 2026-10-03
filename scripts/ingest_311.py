"""
NYC311 Service Request ingestion pipeline.

Downloads a configurable date range from NYC Open Data, validates the
dataset schema, normalizes timestamp fields, and writes the result to
Parquet along with a lightweight data-quality report.

Dataset:
    NYC 311 Service Requests from 2020 to Present
    https://data.cityofnewyork.us/resource/erm2-nwe9.json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


DATASET_ID = "erm2-nwe9"

API_URL = (
    f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json"
)

METADATA_URL = (
    f"https://data.cityofnewyork.us/api/views/{DATASET_ID}"
)

DEFAULT_PAGE_SIZE = 50_000

REQUIRED_COLUMNS = {
    "unique_key",
    "created_date",
    "agency",
    "complaint_type",
    "status",
}


class RetryableAPIError(Exception):
    """API error that should be retried."""


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_cli_date(value: str) -> date:
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Use YYYY-MM-DD."
        ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download NYC311 service request data."
    )

    parser.add_argument(
        "--start",
        required=True,
        type=parse_cli_date,
        help="Inclusive start date: YYYY-MM-DD",
    )

    parser.add_argument(
        "--end",
        required=True,
        type=parse_cli_date,
        help="Inclusive end date: YYYY-MM-DD",
    )

    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"Rows per API page. Default: {DEFAULT_PAGE_SIZE}",
    )

    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Directory for downloaded data.",
    )

    return parser.parse_args()


def build_session(
    app_token: str | None,
) -> requests.Session:
    session = requests.Session()

    session.headers.update(
        {
            "Accept": "application/json",
            "User-Agent": "nyc311-fde-lab/1.0",
        }
    )

    if app_token:
        session.headers[
            "X-App-Token"
        ] = app_token

    else:
        logging.warning(
            "NYC_OPEN_DATA_APP_TOKEN is not configured. "
            "Requests may be subject to stricter rate limits."
        )

    return session


@retry(
    retry=retry_if_exception_type(
        (
            requests.RequestException,
            RetryableAPIError,
        )
    ),
    wait=wait_exponential(
        multiplier=2,
        min=2,
        max=30,
    ),
    stop=stop_after_attempt(5),
    reraise=True,
)
def api_get(
    session: requests.Session,
    url: str,
    params: dict[str, Any] | None = None,
) -> requests.Response:
    response = session.get(
        url,
        params=params,
        timeout=90,
    )

    if (
        response.status_code == 429
        or response.status_code >= 500
    ):
        raise RetryableAPIError(
            "Retryable API response: "
            f"HTTP {response.status_code}"
        )

    response.raise_for_status()

    return response


def get_dataset_metadata(
    session: requests.Session,
) -> tuple[list[str], set[str]]:
    logging.info(
        "Fetching NYC311 dataset metadata..."
    )

    response = api_get(
        session,
        METADATA_URL,
    )

    metadata = response.json()

    columns = metadata.get(
        "columns",
        [],
    )

    if not columns:
        raise RuntimeError(
            "Dataset metadata did not contain "
            "column definitions."
        )

    field_names: list[str] = []

    timestamp_columns: set[str] = set()

    timestamp_types = {
        "floating_timestamp",
        "fixed_timestamp",
        "calendar_date",
    }

    for column in columns:
        field_name = column.get(
            "fieldName"
        )

        if not field_name:
            continue

        field_names.append(
            field_name
        )

        datatype = column.get(
            "dataTypeName"
        )

        if datatype in timestamp_types:
            timestamp_columns.add(
                field_name
            )

    missing_required = (
        REQUIRED_COLUMNS
        - set(field_names)
    )

    if missing_required:
        raise RuntimeError(
            "Dataset schema is missing "
            "required columns: "
            + ", ".join(
                sorted(
                    missing_required
                )
            )
        )

    logging.info(
        "Dataset schema validated: %s columns",
        len(field_names),
    )

    logging.info(
        "Timestamp columns detected: %s",
        ", ".join(
            sorted(
                timestamp_columns
            )
        ),
    )

    return (
        field_names,
        timestamp_columns,
    )


def build_where_clause(
    start_date: date,
    end_date: date,
) -> str:
    """
    User-provided end date is inclusive.

    Socrata query uses:
        start <= created_date < day_after_end
    """

    end_exclusive = (
        end_date
        + timedelta(days=1)
    )

    start_string = (
        start_date.strftime(
            "%Y-%m-%dT00:00:00"
        )
    )

    end_string = (
        end_exclusive.strftime(
            "%Y-%m-%dT00:00:00"
        )
    )

    return (
        f"created_date >= '{start_string}' "
        f"AND created_date < '{end_string}'"
    )


def get_expected_row_count(
    session: requests.Session,
    where_clause: str,
) -> int:
    logging.info(
        "Requesting expected row count..."
    )

    params = {
        "$select": "count(*) as total",
        "$where": where_clause,
    }

    response = api_get(
        session,
        API_URL,
        params=params,
    )

    records = response.json()

    if not records:
        raise RuntimeError(
            "Row count query returned no result."
        )

    total = int(
        records[0]["total"]
    )

    logging.info(
        "Expected rows: %s",
        f"{total:,}",
    )

    return total


def fetch_page(
    session: requests.Session,
    where_clause: str,
    page_size: int,
    offset: int,
) -> list[dict[str, Any]]:
    params = {
        "$where": where_clause,
        "$limit": page_size,
        "$offset": offset,
        "$order": (
            "created_date ASC, "
            "unique_key ASC"
        ),
    }

    response = api_get(
        session,
        API_URL,
        params=params,
    )

    return response.json()


def serialize_nested_value(
    value: Any,
) -> Any:
    if isinstance(
        value,
        (
            dict,
            list,
        ),
    ):
        return json.dumps(
            value,
            sort_keys=True,
        )

    return value


def normalize_page(
    records: list[dict[str, Any]],
    field_names: list[str],
    timestamp_columns: set[str],
    invalid_timestamp_counts: dict[
        str,
        int,
    ],
) -> pd.DataFrame:
    dataframe = (
        pd.DataFrame.from_records(
            records
        )
    )

    # Ensure every official dataset
    # field exists in every page.
    dataframe = dataframe.reindex(
        columns=field_names
    )

    for column in field_names:
        if column in timestamp_columns:
            original_not_null = (
                dataframe[
                    column
                ].notna()
            )

            parsed = pd.to_datetime(
                dataframe[column],
                errors="coerce",
            )

            invalid = (
                original_not_null
                & parsed.isna()
            ).sum()

            invalid_timestamp_counts[
                column
            ] += int(
                invalid
            )

            dataframe[
                column
            ] = parsed

        else:
            dataframe[
                column
            ] = (
                dataframe[
                    column
                ].map(
                    serialize_nested_value
                )
            )

            dataframe[
                column
            ] = (
                dataframe[
                    column
                ].astype(
                    "string"
                )
            )

    return dataframe


def create_arrow_schema(
    field_names: list[str],
    timestamp_columns: set[str],
) -> pa.Schema:
    fields: list[
        pa.Field
    ] = []

    for column in field_names:
        if column in timestamp_columns:
            fields.append(
                pa.field(
                    column,
                    pa.timestamp(
                        "ns"
                    ),
                )
            )

        else:
            fields.append(
                pa.field(
                    column,
                    pa.string(),
                )
            )

    return pa.schema(
        fields
    )


def run_ingestion(
    start_date: date,
    end_date: date,
    page_size: int,
    output_dir: Path,
) -> None:
    if end_date < start_date:
        raise ValueError(
            "--end must be on or after --start"
        )

    if page_size <= 0:
        raise ValueError(
            "--page-size must be greater than zero"
        )

    load_dotenv()

    app_token = os.getenv(
        "NYC_OPEN_DATA_APP_TOKEN"
    )

    session = build_session(
        app_token
    )

    (
        field_names,
        timestamp_columns,
    ) = get_dataset_metadata(
        session
    )

    where_clause = (
        build_where_clause(
            start_date,
            end_date,
        )
    )

    expected_rows = (
        get_expected_row_count(
            session,
            where_clause,
        )
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    basename = (
        f"nyc311_"
        f"{start_date.isoformat()}_"
        f"{end_date.isoformat()}"
    )

    output_path = (
        output_dir
        / f"{basename}.parquet"
    )

    temporary_path = (
        output_dir
        / f"{basename}.tmp.parquet"
    )

    quality_report_path = (
        output_dir
        / f"{basename}_quality.json"
    )

    schema = create_arrow_schema(
        field_names,
        timestamp_columns,
    )

    writer: (
        pq.ParquetWriter
        | None
    ) = None

    rows_downloaded = 0

    offset = 0

    missing_counts: dict[
        str,
        int,
    ] = defaultdict(
        int
    )

    invalid_timestamp_counts: dict[
        str,
        int,
    ] = defaultdict(
        int
    )

    try:
        while True:
            upper_row = min(
                offset + page_size,
                expected_rows,
            )

            logging.info(
                "Fetching rows %s through %s...",
                f"{offset + 1:,}",
                f"{upper_row:,}",
            )

            records = fetch_page(
                session=session,
                where_clause=where_clause,
                page_size=page_size,
                offset=offset,
            )

            if not records:
                break

            dataframe = normalize_page(
                records=records,
                field_names=field_names,
                timestamp_columns=timestamp_columns,
                invalid_timestamp_counts=(
                    invalid_timestamp_counts
                ),
            )

            for column in field_names:
                missing_counts[
                    column
                ] += int(
                    dataframe[
                        column
                    ].isna().sum()
                )

            table = (
                pa.Table.from_pandas(
                    dataframe,
                    schema=schema,
                    preserve_index=False,
                    safe=False,
                )
            )

            if writer is None:
                writer = (
                    pq.ParquetWriter(
                        temporary_path,
                        schema,
                        compression="snappy",
                    )
                )

            writer.write_table(
                table
            )

            page_rows = len(
                dataframe
            )

            rows_downloaded += (
                page_rows
            )

            offset += (
                page_rows
            )

            progress = (
                rows_downloaded
                / expected_rows
                * 100
                if expected_rows
                else 100
            )

            logging.info(
                "Downloaded %s / %s rows (%.1f%%)",
                f"{rows_downloaded:,}",
                f"{expected_rows:,}",
                progress,
            )

            if page_rows < page_size:
                break

    finally:
        if writer is not None:
            writer.close()

    if (
        rows_downloaded
        != expected_rows
    ):
        logging.warning(
            "Downloaded row count (%s) "
            "does not match expected "
            "API count (%s).",
            f"{rows_downloaded:,}",
            f"{expected_rows:,}",
        )

    if not temporary_path.exists():
        # Handle an empty date range by
        # creating an empty parquet file
        # with the proper schema.
        empty_table = (
            pa.Table.from_arrays(
                [
                    pa.array(
                        [],
                        type=field.type,
                    )
                    for field
                    in schema
                ],
                schema=schema,
            )
        )

        pq.write_table(
            empty_table,
            temporary_path,
        )

    temporary_path.replace(
        output_path
    )

    quality_report = {
        "dataset_id": DATASET_ID,
        "source": API_URL,
        "generated_at_utc": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
        "start_date": (
            start_date.isoformat()
        ),
        "end_date": (
            end_date.isoformat()
        ),
        "expected_rows": (
            expected_rows
        ),
        "downloaded_rows": (
            rows_downloaded
        ),
        "row_count_matches": (
            expected_rows
            == rows_downloaded
        ),
        "column_count": len(
            field_names
        ),
        "columns": (
            field_names
        ),
        "timestamp_columns": sorted(
            timestamp_columns
        ),
        "invalid_timestamps": dict(
            sorted(
                invalid_timestamp_counts.items()
            )
        ),
        "missing_values": {
            column: {
                "count": (
                    missing_counts[
                        column
                    ]
                ),
                "percentage": round(
                    (
                        missing_counts[
                            column
                        ]
                        / rows_downloaded
                        * 100
                    )
                    if rows_downloaded
                    else 0,
                    2,
                ),
            }
            for column
            in field_names
        },
    }

    with (
        quality_report_path.open(
            "w",
            encoding="utf-8",
        )
    ) as handle:
        json.dump(
            quality_report,
            handle,
            indent=2,
        )

    logging.info("")

    logging.info(
        "NYC311 INGESTION COMPLETE"
    )

    logging.info(
        "----------------------------------------"
    )

    logging.info(
        "Date range: %s -> %s",
        start_date,
        end_date,
    )

    logging.info(
        "Expected rows:   %s",
        f"{expected_rows:,}",
    )

    logging.info(
        "Downloaded rows: %s",
        f"{rows_downloaded:,}",
    )

    logging.info(
        "Columns:         %d",
        len(field_names),
    )

    logging.info(
        "Parquet:         %s",
        output_path,
    )

    logging.info(
        "Quality report:  %s",
        quality_report_path,
    )


def main() -> int:
    configure_logging()

    args = parse_args()

    try:
        run_ingestion(
            start_date=args.start,
            end_date=args.end,
            page_size=args.page_size,
            output_dir=Path(
                args.output_dir
            ),
        )

        return 0

    except KeyboardInterrupt:
        logging.warning(
            "Ingestion cancelled by user."
        )

        return 130

    except Exception:
        logging.exception(
            "NYC311 ingestion failed."
        )

        return 1


if __name__ == "__main__":
    sys.exit(
        main()
    )