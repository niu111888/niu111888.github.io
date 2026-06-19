#!/usr/bin/env python3
"""
ロゴ画像の背景（白/単色の明るい背景）を透明に切り抜き、余白をトリミングするツール。

使い方:
    python3 tools/cutout_logo.py 入力画像.png 出力.png

例:
    python3 tools/cutout_logo.py 新しいロゴ.png logo.png

仕組み:
    紫のロゴ × 白背景、のように「ロゴが暗い色 / 背景が明るい」画像で有効。
    各ピクセルの「白からの距離」をもとに透明度を決め、ロゴ本体は不透明のまま、
    アンチエイリアスの細い縁だけを羽化してきれいに抜く。

必要なもの:
    Pillow  ->  pip3 install pillow
"""

import sys
import numpy as np
from PIL import Image

# 抜け具合の調整つまみ（小さいほどシビアに白だけ抜く / 大きいほど淡い色まで抜く）
THRESHOLD = 40       # 「白からの距離」何ピクセル分で完全不透明にするか
ALPHA_FLOOR = 20     # トリミング範囲を決めるときの不透明判定のしきい値
PADDING = 10         # 切り抜き後に残す余白(px)


def cutout(in_path: str, out_path: str) -> None:
    src = Image.open(in_path).convert("RGBA")
    a = np.asarray(src).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]

    # 白(255,255,255)からの距離。白=0、濃いインクほど大きい
    mn = np.minimum(np.minimum(r, g), b)
    dist = 255 - mn
    alpha = np.clip(dist / float(THRESHOLD) * 255.0, 0, 255)

    out = a.copy()
    out[..., 3] = alpha
    img = Image.fromarray(out.astype("uint8"), "RGBA")

    # 不透明部分の外接矩形に余白を足してトリミング
    ys, xs = np.where(alpha > ALPHA_FLOOR)
    if len(xs) and len(ys):
        x0 = max(int(xs.min()) - PADDING, 0)
        y0 = max(int(ys.min()) - PADDING, 0)
        x1 = min(int(xs.max()) + PADDING, img.width)
        y1 = min(int(ys.max()) + PADDING, img.height)
        img = img.crop((x0, y0, x1, y1))

    img.save(out_path)
    print(f"完了: {out_path}  size={img.size}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python3 tools/cutout_logo.py 入力画像 出力画像")
        sys.exit(1)
    cutout(sys.argv[1], sys.argv[2])
