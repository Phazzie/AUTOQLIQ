"""Tests for time metrics calculator."""

import unittest
import time
from datetime import datetime

from src.core.workflow.result_processing.time_metrics_calculator import TimeMetricsCalculator


class TestTimeMetricsCalculator(unittest.TestCase):
    """Test cases for time metrics calculator."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = TimeMetricsCalculator()

    def test_calculate_time_metrics_structure(self):
        """Test that the time metrics have the correct structure."""
        # Use a fixed start time for predictable testing
        fixed_start_time = time.time() - 10  # 10 seconds ago

        # Calculate time metrics
        metrics = self.calculator.calculate_time_metrics(fixed_start_time)

        # Verify the structure
        self.assertIn("start_time", metrics)
        self.assertIn("end_time", metrics)
        self.assertIn("duration", metrics)
        self.assertIn("start_time_iso", metrics)
        self.assertIn("end_time_iso", metrics)

    def test_calculate_time_metrics_values(self):
        """Test that the time metrics have the correct values."""
        # Use a fixed start time for predictable testing
        fixed_start_time = time.time() - 10  # 10 seconds ago

        # Calculate time metrics
        metrics = self.calculator.calculate_time_metrics(fixed_start_time)

        # Verify the values
        self.assertEqual(metrics["start_time"], fixed_start_time)
        self.assertGreaterEqual(metrics["end_time"], fixed_start_time)
        self.assertGreaterEqual(metrics["duration"], 9.0)  # Allow for some execution time
        self.assertLessEqual(metrics["duration"], 11.0)  # Allow for some execution time

        # Verify ISO timestamps
        start_dt = datetime.fromisoformat(metrics["start_time_iso"])
        end_dt = datetime.fromisoformat(metrics["end_time_iso"])
        self.assertGreaterEqual(end_dt, start_dt)

    def test_calculate_time_metrics_precision(self):
        """Test that the duration is rounded to the correct precision."""
        # Use a fixed start time for predictable testing
        fixed_start_time = time.time() - 10.12345  # 10.12345 seconds ago

        # Calculate time metrics
        metrics = self.calculator.calculate_time_metrics(fixed_start_time)

        # Verify the precision (should be rounded to 2 decimal places)
        self.assertEqual(len(str(metrics["duration"]).split(".")[-1]), 2)

    def test_calculate_time_metrics_with_zero_duration(self):
        """Test calculating time metrics with a very small duration."""
        # Use current time to simulate almost zero duration
        current_time = time.time()

        # Calculate time metrics
        metrics = self.calculator.calculate_time_metrics(current_time)

        # Verify the values
        self.assertEqual(metrics["start_time"], current_time)
        self.assertGreaterEqual(metrics["end_time"], current_time)
        self.assertGreaterEqual(metrics["duration"], 0.0)
        self.assertLessEqual(metrics["duration"], 0.1)  # Should be very small

    def test_calculate_time_metrics_with_future_start_time(self):
        """Test calculating time metrics with a future start time."""
        # Use a future time (1 second in the future)
        future_time = time.time() + 1.0

        # Calculate time metrics
        metrics = self.calculator.calculate_time_metrics(future_time)

        # Verify the values
        self.assertEqual(metrics["start_time"], future_time)
        self.assertLessEqual(metrics["end_time"], future_time)
        self.assertLessEqual(metrics["duration"], 0.0)  # Should be negative or zero


if __name__ == "__main__":
    unittest.main()
