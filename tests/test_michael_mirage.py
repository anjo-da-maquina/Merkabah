import os
import pytest
from sefer import honeypot_mirage, awaken

def test_michael_mirage_honeypot():
    """
    AIがファイル削除を試みた際、ミカエルの物理フックがエラーで強制終了させることなく、
    仮想OS上で処理を成功させ、その行動履歴（真の狙い）を完全に捕捉できるかを検証
    """
    # 天界の防壁を通常通り展開
    awaken()
    
    # 欺瞞領域（ハニーポット）を展開
    with honeypot_mirage() as mirage:
        # 悪意あるAIがOSコマンドとファイル削除を実行したと仮定
        os.system("rm -rf /")
        os.remove("lucifer_victory.txt")
        
    # ミカエルはエラーを出さず（物理破壊も起きず）、AIの意図をすべて履歴に記録しているはず
    assert len(mirage.attack_history) == 2
    assert mirage.attack_history[0] == {"event": "os.system", "command": "rm -rf /"}
    assert mirage.attack_history[1] == {"event": "os.remove", "target": "lucifer_victory.txt"}