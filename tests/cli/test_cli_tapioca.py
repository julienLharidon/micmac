import subprocess
import sys


def test_tapioca_cli_help():
    result = subprocess.run([sys.executable, "tapioca.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Tapioca" in result.stdout

def test_tapioca_cli_execution():
    result = subprocess.run([sys.executable, "tapioca.py", "img1.tif", "img2.tif"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Traitement de img1.tif" in result.stdout
    assert "Image img2.tif: 1000 points extraits" in result.stdout
