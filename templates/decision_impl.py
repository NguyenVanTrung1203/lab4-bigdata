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

    # Step 1: missing sensor or too little history.
    stats = baseline.get(event["sensor_id"])
    if stats is None or stats["n"] < contract["min_baseline_rows"]:
        return {"score": None, "route": "HOLD", "reason": "INSUFFICIENT_BASELINE"}

    # Step 2: unparseable, non-finite, or out-of-range temperature.
    minimum = Decimal(str(contract["min_temperature_c"]))
    maximum = Decimal(str(contract["max_temperature_c"]))
    try:
        value = Decimal(str(event["temperature_c"]))
        valid = value.is_finite() and minimum <= value <= maximum
    except (InvalidOperation, TypeError, ValueError):
        valid = False
    if not valid:
        return {"score": None, "route": "HOLD", "reason": "INVALID_VALUE"}

    # Step 3: robust z-score, rounded half-up to 6 decimals BEFORE any comparison.
    places = Decimal(1).scaleb(-int(contract["score_decimal_places"]))
    raw = abs(value - Decimal(stats["median_c"])) / Decimal(stats["scale_c"])
    score = format(raw.quantize(places, rounding=ROUND_HALF_UP), f".{int(contract['score_decimal_places'])}f")

    # Step 4: arrival lag (score is kept for late rows).
    lag = (timestamp(event["ingest_time_utc"]) - timestamp(event["event_time_utc"])).total_seconds()
    if lag > contract["late_limit_seconds"]:
        return {"score": score, "route": "HOLD", "reason": "LATE_FOR_ACTION"}

    # Steps 5-6: timely rows are compared with the threshold (score >= threshold).
    if Decimal(score) >= Decimal(str(threshold)):
        return {"score": score, "route": "ALERT", "reason": "THRESHOLD"}
    return {"score": score, "route": "NORMAL", "reason": "BELOW_THRESHOLD"}


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
    ids = [item["record_id"] for item in predictions]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate prediction record_id")
    if set(ids) != set(labels):
        raise ValueError("predictions and labels do not match 1-to-1")
    if any(value not in (0, 1) for value in labels.values()):
        raise ValueError("labels must be 0 or 1")

    tp = fp = tn = fn = hold = held_positive = 0
    for item in predictions:
        route = item["route"]
        positive = labels[item["record_id"]] == 1
        if route == "ALERT":
            tp, fp = tp + positive, fp + (not positive)
        elif route == "NORMAL":
            fn, tn = fn + positive, tn + (not positive)
        elif route == "HOLD":
            hold += 1
            held_positive += positive
        else:
            raise ValueError("unknown route")

    def ratio(numerator, denominator):
        return numerator / denominator if denominator else None

    n = len(predictions)
    eligible = tp + fp + tn + fn
    alerts = tp + fp
    positive_total = sum(labels.values())
    weights = contract["cost_units"]
    cost_units = (
        weights["false_negative"] * fn
        + weights["false_positive"] * fp
        + weights["alert_review"] * alerts
        + weights["hold_review"] * hold
    )
    return {
        "n": n,
        "eligible": eligible,
        "hold": hold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "alerts": alerts,
        "positive_total": positive_total,
        "held_positive": held_positive,
        "precision": ratio(tp, tp + fp),
        "recall": ratio(tp, tp + fn),
        "f1": ratio(2 * tp, 2 * tp + fp + fn),
        "coverage": ratio(eligible, n),
        "end_to_end_recall": ratio(tp, positive_total),
        "cost_units": cost_units,
        "cost": cost_units / contract["cost_display_divisor"],
    }


def make_action_key(team_id: str, event: dict, policy_id: str) -> str:
    """Build a deterministic SHA-256 semantic idempotency key for an event and policy.

    Hash UTF-8 json.dumps of:
        [team_id, event["source_object"], int(event["source_row"]),
         event["source_sha256"], event["record_id"], policy_id]
    with ensure_ascii=False and separators=(",", ":").
    Never include batch_id, checkpoint path, arrival order, or wall-clock timestamps.
    """
    raise NotImplementedError("T3: implement make_action_key")
