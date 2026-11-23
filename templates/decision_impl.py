"""Four assessed decision functions. Complete all four BEFORE freezing your policy.

Use Decimal with ROUND_HALF_UP. Do not read label files inside fit_baseline or score_event.
See schemas/decision_contract.json and Lab4_Decision_Support_Data_Driven_Action.docx
for exact formulas and edge-case specifications.
"""


def fit_baseline(rows: list[dict], contract: dict) -> dict[str, dict]:
    """Fit per-sensor historical location and scale parameters on past Silver data.

    Returns:
        dict mapping sensor_id -> {
            "n": int,
            "median_c": str (2 decimal places),
            "mad_c": str (2 decimal places),
            "scale_c": str (6 decimal places),
        }

    Requirements:
        - Raise ValueError on duplicate record_id.
        - Raise ValueError if event_time_utc >= fit_cutoff_utc OR ingest_time_utc >= fit_cutoff_utc.
        - Raise ValueError on non-finite or out-of-range temperature_c (outside [-30, 60] C).
        - Retain valid historical late rows whose event and ingest timestamps are both before cutoff.
        - Compute scale_c = max(1.4826 * MAD, 0.50) using Decimal ROUND_HALF_UP.
        - Return statistics for all sensors present in rows (do not filter n < 30 here).
    """
    from datetime import datetime, timezone
    from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

    def timestamp(value):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("timestamp must include a timezone")
            return parsed.astimezone(timezone.utc)
        except (AttributeError, TypeError, ValueError, OverflowError) as exc:
            raise ValueError("invalid timestamp") from exc

    def median(values):
        ordered = sorted(values)
        middle = len(ordered) // 2
        return ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / Decimal(2)

    cutoff = timestamp(contract["fit_cutoff_utc"])
    minimum = Decimal(str(contract["min_temperature_c"]))
    maximum = Decimal(str(contract["max_temperature_c"]))
    factor = Decimal(str(contract["mad_scale"]))
    floor = Decimal(str(contract["scale_floor_c"]))
    seen = set()
    groups = {}
    for row in rows:
        record_id = row["record_id"]
        if record_id in seen:
            raise ValueError("duplicate record_id")
        seen.add(record_id)
        if timestamp(row["event_time_utc"]) >= cutoff or timestamp(row["ingest_time_utc"]) >= cutoff:
            raise ValueError("timestamp at or after cutoff")
        try:
            value = Decimal(str(row["temperature_c"]))
            if not value.is_finite() or not minimum <= value <= maximum:
                raise ValueError("invalid temperature")
        except (InvalidOperation, TypeError) as exc:
            raise ValueError("invalid temperature") from exc
        groups.setdefault(row["sensor_id"], []).append(value)

    result = {}
    for sensor, values in groups.items():
        location = median(values)
        mad = median([abs(value - location) for value in values])
        scale = max(factor * mad, floor)
        result[sensor] = {
            "n": len(values),
            "median_c": format(location.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f"),
            "mad_c": format(mad.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f"),
            "scale_c": format(scale.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP), ".6f"),
        }
    return result


def score_event(event: dict, baseline: dict, threshold: str, contract: dict) -> dict:
    """Score a single observation and route it to HOLD, ALERT, or NORMAL.

    Returns:
        {"score": str (6 decimal places) | None, "route": str, "reason": str}

    Priority order:
        1. Missing sensor in baseline or n < 30 -> {"score": None, "route": "HOLD", "reason": "INSUFFICIENT_BASELINE"}
        2. Unparseable, non-finite, or out-of-range temperature_c -> {"score": None, "route": "HOLD", "reason": "INVALID_VALUE"}
        3. Compute score = round_half_up(|temperature_c - median_c| / scale_c, 6)
        4. Arrival lag (ingest_time_utc - event_time_utc) > 900s -> {"score": score_str, "route": "HOLD", "reason": "LATE_FOR_ACTION"}
        5. Fresh event with Decimal(score_str) >= Decimal(str(threshold)) -> {"score": score_str, "route": "ALERT", "reason": "THRESHOLD"}
        6. Otherwise -> {"score": score_str, "route": "NORMAL", "reason": "BELOW_THRESHOLD"}
    """
    raise NotImplementedError("T2: implement score_event")


def evaluate(predictions: list[dict], labels: dict[str, int], contract: dict) -> dict:
    """Compute confusion counts, coverage, eligible vs. end-to-end recall, and proxy cost.

    Returns a dict with 17 keys:
        n, eligible, hold, tp, fp, tn, fn, alerts, positive_total, held_positive,
        precision, recall, f1, coverage, end_to_end_recall, cost_units, cost.

    Requirements:
        - Raise ValueError if prediction record_ids contain duplicates, do not match
          labels keys 1-to-1, or if any label is not in {0, 1}.
        - Compute tp, fp, tn, fn over eligible rows (ALERT and NORMAL) only.
        - Return None for any ratio whose denominator is 0.
        - Include held_positive in positive_total for end_to_end_recall = tp / positive_total.
        - cost_units = 50*fn + 10*fp + 2*alerts + 10*hold; cost = cost_units / 10.
    """
    raise NotImplementedError("T2: implement evaluate")


def make_action_key(team_id: str, event: dict, policy_id: str) -> str:
    """Build a deterministic SHA-256 semantic idempotency key for an event and policy.

    Hash UTF-8 json.dumps of:
        [team_id, event["source_object"], int(event["source_row"]),
         event["source_sha256"], event["record_id"], policy_id]
    with ensure_ascii=False and separators=(",", ":").
    Never include batch_id, checkpoint path, arrival order, or wall-clock timestamps.
    """
    raise NotImplementedError("T3: implement make_action_key")
