# 写真ごとに、ページと同じ 720x1280 の切り抜きで顔の目印を測り、JSON で出す（座標は 0..1、上が 0）
import sys, json, mediapipe as mp
from PIL import Image
import numpy as np
from mediapipe.tasks.python import vision, BaseOptions
det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=sys.argv[1]), num_faces=1))
out = []
for f in sys.argv[2:]:
    im = Image.open(f).convert('RGB'); W, H = 720, 1280
    s = max(W / im.width, H / im.height); im = im.resize((round(im.width * s), round(im.height * s)))
    l, t = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((l, t, l + W, t + H))
    r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(im)))
    if not r.face_landmarks: out.append(None); print(f, 'no face', file=sys.stderr); continue
    p = lambda i: [round(r.face_landmarks[0][i].x, 3), round(r.face_landmarks[0][i].y, 3)]
    out.append({'top': p(10), 'nose': p(1), 'chin': p(152), 'eyeL': p(33), 'eyeR': p(263), 'cheekL': p(234), 'cheekR': p(454)})
print(json.dumps(out))
