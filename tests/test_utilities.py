import pytest
import socket
import os
import csv
import json
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from utilities import (
    is_port_in_use,
    read_csv,
    write_csv,
    read_json,
    generate_DTG,
    format_readable_DTG
)

def test_is_port_in_use():
    with patch("socket.socket.connect_ex", return_value=0):
        assert is_port_in_use(80) is True
    with patch("socket.socket.connect_ex", return_value=1):
        assert is_port_in_use(80) is False

def test_read_csv(tmp_path):
    test_file = tmp_path / "test.csv"
    with open(test_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'age'])
        writer.writeheader()
        writer.writerow({'name': 'John', 'age': '30'})
        writer.writerow({'name': 'Jane', 'age': '25'})
    data = read_csv(str(test_file))
    assert data == [{'name': 'John', 'age': '30'}, {'name': 'Jane', 'age': '25'}]

def test_write_csv(tmp_path):
    test_file = tmp_path / "test.csv"
    data = [{'name': 'John', 'age': '30'}, {'name': 'Jane', 'age': '25'}]
    write_csv(str(test_file), data)
    with open(test_file, newline='') as file:
        reader = csv.DictReader(file)
        assert list(reader) == data

def test_read_json(tmp_path):
    test_file = tmp_path / "test.json"
    test_data = {"name": "John", "age": 30}
    test_file.write_text(json.dumps(test_data))
    assert read_json(str(test_file)) == test_data

def test_generate_DTG():
    dtg = generate_DTG()
    assert len(dtg) == 14  # Ensuring it follows DDTTTTXMMMYYYY format

def test_format_readable_DTG():
    dtg = "011530LFEB2025"
    assert format_readable_DTG(dtg) == "1530L on 01 FEB 2025"
