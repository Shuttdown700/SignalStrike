import os
import pytest
import shutil
import sys
import logging
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from batch_tile_download import delete_small_files_and_empty_dirs, download_tile_batch

# Create a temporary directory for testing
@pytest.fixture(scope="function")
def temp_dir(tmp_path):
    test_dir = tmp_path / "test_directory"
    test_dir.mkdir()
    return test_dir

# Test delete_small_files_and_empty_dirs function
def test_delete_small_files_and_empty_dirs(temp_dir):
    small_file = temp_dir / "small_file.txt"
    small_file.write_text("Test")

    large_file = temp_dir / "large_file.txt"
    large_file.write_text("A" * 1024 * 10)  # 10 KB file

    empty_dir = temp_dir / "empty_subdir"
    empty_dir.mkdir()

    delete_small_files_and_empty_dirs(str(temp_dir), size_limit_kb=5, dry_run=False)

    assert not small_file.exists(), "Small file was not deleted"
    assert large_file.exists(), "Large file was incorrectly deleted"
    assert not empty_dir.exists(), "Empty directory was not deleted"

# Test invalid directory input
def test_invalid_directory():
    with pytest.raises(AssertionError):
        delete_small_files_and_empty_dirs("invalid_dir", size_limit_kb=5)

# Test download_tile_batch assertions
def test_download_tile_batch_invalid_inputs():
    with pytest.raises(AssertionError):
        download_tile_batch([35.0], [40.0, -120.0])
    
    with pytest.raises(AssertionError):
        download_tile_batch("invalid", [40.0, -120.0])
    
    with pytest.raises(AssertionError):
        download_tile_batch([35.0, -115.0], "invalid")
    
    with pytest.raises(AssertionError):
        download_tile_batch([35.0, -115.0], [40.0, -120.0], min_zoom=30)
    
    with pytest.raises(AssertionError):
        download_tile_batch([35.0, -115.0], [40.0, -120.0], parallel_threads=10)

# Test subprocess execution
def test_download_tile_batch_execution():
    with patch("subprocess.run") as mock_subproc:
        download_tile_batch([35.0, -115.0], [40.0, -120.0])
        mock_subproc.assert_called()
