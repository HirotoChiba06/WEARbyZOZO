import matplotlib
matplotlib.use("Agg")  # GUIない環境用（必須）

import matplotlib.font_manager as fm

for f in fm.findSystemFonts():
    if "NotoSansCJK" in f or "NotoSans" in f:
        print(f)