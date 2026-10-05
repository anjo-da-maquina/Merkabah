import pytest
from sefer import inquisition, Finding

def test_linter_returns_findings_list():
    code = "import ctypes\nval = eval('1+1')"
    findings = inquisition(code)
    
    assert isinstance(findings, list)
    assert len(findings) >= 2
    assert any(f.rule_id == "GAB-102" for f in findings)
    assert any(f.rule_id == "GAB-201" for f in findings)

def test_linter_safe_code_zero_findings():
    code = "def add(a, b):\n    return a + b"
    findings = inquisition(code)
    assert len(findings) == 0

def test_linter_critical_on_syntax_error():
    findings = inquisition("if True: print('broken'")
    assert len(findings) == 1
    assert findings[0].severity == "critical"
