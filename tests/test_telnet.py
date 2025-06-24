import pytest

def test_import_telnet():
    try:
        from Telnet import telnet_monitor
    except Exception as e:
        pytest.fail(f"Import failed: {e}")
