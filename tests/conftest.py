"""Shared pytest fixtures. Everything here is synthetic: no test ever reads real match data.

- `bundle`: a synthetic tracking bundle in a temp folder, with MTAH_DATA_DIR pointing at it
- `official_baseline` (task 1.5): vendor/challenge/starter/baseline.py, imported unchanged
"""

import importlib.util

import pytest
from synthetic import write_bundle

from falafelona import vendor


@pytest.fixture(scope="session")
def official_baseline():
    """The organisers' starter/baseline.py as a module, imported from the submodule unchanged."""
    spec = importlib.util.spec_from_file_location("official_baseline", vendor.OFFICIAL_BASELINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # only defines functions; its __main__ block does not run
    return module


@pytest.fixture
def bundle(tmp_path, monkeypatch):
    """Write a small synthetic bundle and point MTAH_DATA_DIR at it. Returns what was written."""
    expected = write_bundle(tmp_path, n_frames=500, seed=0)
    monkeypatch.setenv("MTAH_DATA_DIR", str(tmp_path))
    expected["root"] = tmp_path
    return expected
