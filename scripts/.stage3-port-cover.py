#!/usr/bin/env python3
"""Targeted correction for the bottom-right label of cover 11. No other cover assets are changed."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np, cv2, subprocess, io, re
from pathlib import Path
BASE="ac8169594f47e5e0b73e774852024fc1ef563e51"
root=Path(__file__).resolve().parent.parent
original=subprocess.check_output(["git","show",BASE+":img/cover-11-number-port-og.jpg"])
im=Image.open(io.BytesIO(original)).convert("RGB")
assert im.size==(1254,1254), f"Unexpected image size {im.size}"
arr=np.array(im)
# Only inpaint the existing black letters in the right-hand payment condition chip.
mask=np.zeros((1254,1254),dtype=np.uint8)
x0,y0,x1,y1=954,1127,1220,1197
roi=arr[y0:y1,x0:x1,:]
dark=(np.max(roi,axis=2)<175).astype(np.uint8)*255
dark=cv2.dilate(dark,np.ones((5,5),dtype=np.uint8),iterations=1)
mask[y0:y1,x0:x1]=dark
clean=cv2.inpaint(arr,mask,7,cv2.INPAINT_TELEA)
img=Image.fromarray(clean)
draw=ImageDraw.Draw(img)
f="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
font1=ImageFont.truetype(f,31,index=1)
font2=ImageFont.truetype(f,29,index=1)
# These two phrases together with the already-present '기존 번호 유지' pill
# state that number transfer requires clearing overdue charges.
for txt,font,y in [("번호이동은",font1,1132),("미납요금 정산 후",font2,1168)]:
    box=draw.textbbox((0,0),txt,font=font,stroke_width=0)
    width=box[2]-box[0]
    if width>266: raise RuntimeError(f"Overflow: {txt}, width={width}")
    x=1087-width//2
    draw.text((x,y),txt,font=font,fill=(18,18,18),stroke_width=0)
img.save(root/"img/cover-11-number-port-og.jpg","JPEG",quality=94,optimize=True)
img.resize((640,640),Image.Resampling.LANCZOS).save(root/"img/cover-11-number-port-mobile.jpg","JPEG",quality=91,optimize=True)
print("Generated 11 cover JPEGs, untouched area outside x=954:1220 y=1127:1197")
