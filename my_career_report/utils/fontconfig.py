import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm


def set_korean_font() -> None:
    """Configure Matplotlib to use a Korean font if available."""
    font_path = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    available = {f.name for f in fm.fontManager.ttflist}

    if font_path.exists():
        fm.fontManager.addfont(str(font_path))
        font_name = fm.FontProperties(fname=str(font_path)).get_name()
        plt.rcParams["font.family"] = font_name
    else:
        for name in [
            "NanumSquareNeo Bold",
            "NanumSquareRound",
            "NanumSquareRoundOTF",
            "Noto Sans CJK KR",
            "NanumGothic",
            "Malgun Gothic",
            "AppleGothic",
        ]:
            if name in available:
                plt.rcParams["font.family"] = name
                break
    plt.rcParams["axes.unicode_minus"] = False
