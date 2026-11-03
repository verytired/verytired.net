# 写真を、エアブラシで描いた装画のような面にする前処理。輪郭は残して、肌のきめ・髪の筋・ぼけの粒を消す。
# 使い方：uv run --with opencv-python-headless python 023_melt/src/prep.py  → src/woman*_paint.jpg
import cv2, glob, os
d = os.path.dirname(os.path.abspath(__file__))
for f in sorted(glob.glob(os.path.join(d, 'woman*_v1.jpg'))):
    im = cv2.imread(f)
    im = cv2.bilateralFilter(im, 7, 25, 7)   # 色の近い所どうしだけをならす
    im = cv2.edgePreservingFilter(im, flags=1, sigma_s=30, sigma_r=0.18)   # 面を広くなめらかに
    cv2.imwrite(f.replace('_v1.jpg', '_paint.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(os.path.basename(f))
