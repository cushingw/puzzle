import pytest
import subprocess

# These are some tests just to verify basic sanity checks on the major function points.
# They are by no means exhaustive

def test_help(capfd):
    result = subprocess.run(['python','match_homeowners.py','-h'], text=True)
    assert result.returncode == 0
    cap = capfd.readouterr()
    assert 'usage' in cap.out

def test_full_run(capfd):
    result = subprocess.run(['python','match_homeowners.py','sample_input.txt'], text=True)
    assert result.returncode == 0
    cap = capfd.readouterr()
    assert 'N1: H1(18) H7(20) H9(23) H8(21)' in cap.out

def test_bad_homeowner_range(capfd):
    result = subprocess.run(['python','match_homeowners.py','test_fixtures/bad_homeowner_range.txt'], text=True)
    assert result.returncode == 1
    cap = capfd.readouterr()
    assert 'Error: malformed input' in cap.err

def test_no_homeowner_id(capfd):
    result = subprocess.run(['python','match_homeowners.py','test_fixtures/no_homeowner_id.txt'], text=True)
    assert result.returncode == 1
    cap = capfd.readouterr()
    assert 'Error: malformed input' in cap.err

def test_no_homeowner_prefs(capfd):
    result = subprocess.run(['python','match_homeowners.py','test_fixtures/no_homeowner_prefs.txt'], text=True)
    assert result.returncode == 1
    cap = capfd.readouterr()
    assert 'Error: malformed input' in cap.err

def test_bad_homeowner_prefs(capfd):
    result = subprocess.run(['python','match_homeowners.py','test_fixtures/bad_homeowner_prefs.txt'], text=True)
    assert result.returncode == 1
    cap = capfd.readouterr()
    assert 'Error: found neighborhood preferences for non-present neighborhoods' in cap.err

def test_bad_neighborhood_range(capfd):
    result = subprocess.run(['python','match_homeowners.py','test_fixtures/bad_neighborhood_range.txt'], text=True)
    assert result.returncode == 1
    cap = capfd.readouterr()
    assert 'Error: malformed input' in cap.err

def test_no_neighborhood_id(capfd):
    result = subprocess.run(['python','match_homeowners.py','test_fixtures/no_neighborhood_id.txt'], text=True)
    assert result.returncode == 1
    cap = capfd.readouterr()
    assert 'Error: malformed input' in cap.err
