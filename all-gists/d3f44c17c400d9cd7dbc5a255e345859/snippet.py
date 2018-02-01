import pytest

def pytest_runtest_makereport(item, call):
      if call.excinfo is not None:
        if item.name == 'expected_test':
          setattr(item.session, 'skiprest', True)

def pytest_runtest_setup(item):
      skiprest = getattr(item.session, "skiprest", False)
      if skiprest:
          pytest.skip("First test failed, skipping rest")