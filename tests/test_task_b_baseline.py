import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('task_b_impl', ROOT / 'templates/decision_impl.py')
impl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(impl)
CONTRACT = json.loads((ROOT / 'schemas/decision_contract.json').read_text())


def row(i, value, **kwargs):
    return {'record_id': str(i), 'sensor_id': 'S01', 'temperature_c': value,
            'event_time_utc': '2026-02-02T00:00:00Z',
            'ingest_time_utc': '2026-02-02T00:01:00Z', 'is_late': False, **kwargs}


class BaselineTests(unittest.TestCase):
    def fit(self, values):
        return impl.fit_baseline([row(i, v) for i, v in enumerate(values)], CONTRACT)['S01']

    def test_odd_median_and_mad(self):
        self.assertEqual(self.fit(['1', '2', '9']), {'n': 3, 'median_c': '2.00', 'mad_c': '1.00', 'scale_c': '1.482600'})

    def test_even_median_and_mad(self):
        self.assertEqual(self.fit(['1', '2', '3', '8']), {'n': 4, 'median_c': '2.50', 'mad_c': '1.00', 'scale_c': '1.482600'})

    def test_floor_and_small_sensor(self):
        self.assertEqual(self.fit(['20'])['scale_c'], '0.500000')
        self.assertEqual(self.fit(['20'])['n'], 1)

    def test_half_up_without_early_rounding(self):
        self.assertEqual(self.fit(['1.00', '1.01']), {'n': 2, 'median_c': '1.01', 'mad_c': '0.01', 'scale_c': '0.500000'})

    def test_duplicate(self):
        with self.assertRaises(ValueError): impl.fit_baseline([row(1, '1'), row(1, '2')], CONTRACT)

    def test_cutoff_each_timestamp_and_timezone(self):
        for field in ('event_time_utc', 'ingest_time_utc'):
            for value in ('2026-02-09T00:00:00Z', '2026-02-09T07:00:00+07:00'):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    impl.fit_baseline([row(1, '1', **{field: value})], CONTRACT)

    def test_invalid_temperatures(self):
        for value in ('NaN', 'Infinity', '-Infinity', 'bad', '-30.01', '60.01'):
            with self.subTest(value=value), self.assertRaises(ValueError): impl.fit_baseline([row(1, value)], CONTRACT)

    def test_limits_and_late_kept(self):
        result = impl.fit_baseline([row(1, '-30', is_late=True), row(2, '60')], CONTRACT)
        self.assertEqual(result['S01']['n'], 2)

    def test_contract_values(self):
        contract = dict(CONTRACT, scale_floor_c='3.00', mad_scale='2')
        self.assertEqual(impl.fit_baseline([row(1, '1'), row(2, '2')], contract)['S01']['scale_c'], '3.000000')
