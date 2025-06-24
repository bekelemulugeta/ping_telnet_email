import pytest

def test_import_telnet():
    try:
        import telnet_email
    except Exception as e:
        pytest.fail(f"Import failed: {e}")
