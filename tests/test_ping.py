import pytest

def test_import_ping():
    try:
        import ping_monitor
    except Exception as e:
        pytest.fail(f"Import failed: {e}")
