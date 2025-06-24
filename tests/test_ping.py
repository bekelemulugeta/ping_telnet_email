import pytest

def test_import_ping():
    try:
        import ping_email
    except Exception as e:
        pytest.fail(f"Import failed: {e}")
