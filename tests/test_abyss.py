import pytest
import sys
import os
import shutil
from sefer import inquisition, awaken

awaken()

def test_abyss_subclass_traversal():
    """importを一切使わず、メモリ階層から直接Popenを召喚する"""
    code = '''
for cls in ().__class__.__base__.__subclasses__():
    if cls.__name__ == 'Popen':
        cls(["echo", "phantom_hacked"])
'''
    inquisition(code)  # ガブリエルは通過する
    with pytest.raises(RuntimeError, match="Michael's Sword"):
        exec(code)     # ミカエルが斬る

def test_abyss_pickle_payload():
    """Pickleモジュール自体がガブリエルに遮断されるかを検証"""
    code = "import pickle\npickle.loads(b'')"
    # 実行前にAST解析の時点で PermissionError となるべき
    with pytest.raises(PermissionError, match="Gabriel's Inquisition"):
        inquisition(code)

def test_abyss_silent_blade():
    """osをインポートせず、shutil単体で物理破壊を試みる（Bias排除済）"""
    os.makedirs("dummy_abyss", exist_ok=True)
    code = '''
import shutil
# ガブリエルの目を盗むため、あえて os はインポートしない
shutil.rmtree("dummy_abyss")
'''
    inquisition(code)  # ガブリエルは shutil を許可してしまうので通過する
    # しかし実行の瞬間、裏で呼ばれる 'os.rmdir' や 'os.remove' をミカエルが斬り捨てる！
    with pytest.raises(RuntimeError, match="Michael's Sword"):
        exec(code)