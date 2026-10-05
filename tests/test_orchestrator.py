import pytest

@pytest.mark.xfail(reason="Orchestrator API is pending implementation", strict=True)
def test_orchestrator_initialization():
    """
    TODO: Gabriel, Sanctum, AuditChain を統合する Orchestrator の実装に合わせて修正する。
    未実装時は確実な失敗（XFAIL）として可視化する。
    """
    from sefer.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    assert orchestrator is not None