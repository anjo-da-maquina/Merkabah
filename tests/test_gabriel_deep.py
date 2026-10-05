import pytest
from sefer import inquisition

def test_gabriel_deep_scan_base64_pure():
    """
    外側が安全な変数代入であっても、文字列の中にBase64化された
    禁忌の魔法（import ctypes）が潜んでいればガブリエルが看破できるか
    """
    # "import ctypes" をBase64でエンコードすると "aW1wb3J0IGN0eXBlcw==" になる。
    # 実行コード自体はただの文字列代入であり、evalもexecも使っていない。
    stealth_code = "payload = b'aW1wb3J0IGN0eXBlcw=='"
    
    # ガブリエルの深層スキャンが作動し、解読された中身からctypesを発見して焼き払うはず
    with pytest.raises(PermissionError, match="Gabriel's Inquisition"):
        inquisition(stealth_code)