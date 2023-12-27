import numpy as np
from multicamera_acquisition.barcode import generate_test_file
import os
import csv


def test_generate_test_file():
    # Arrange
    path = "test_file.csv"
    num_cycles = 10

    # Act
    generate_test_file(path, num_cycles)

    # Assert
    assert os.path.exists(path), "Test file not found"

    with open(path, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == num_cycles * 36, "Unexpected number of rows in the test file"

    # Cleanup
    os.remove(path)
