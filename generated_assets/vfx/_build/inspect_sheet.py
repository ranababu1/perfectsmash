import sys, numpy as np
from PIL import Image
sys.path.insert(0, ".")
from vfxlib import composite
p, blend = sys.argv[1], sys.argv[2]
out = sys.argv[3] if len(sys.argv) > 3 else "/tmp/inspect.png"
im = np.asarray(Image.open(p).convert("RGBA"))
c = composite(im, blend)
# checker/grid lines for frame borders
Image.fromarray((c * 255).astype(np.uint8)).resize((min(1600, im.shape[1]), int(min(1600, im.shape[1]) * im.shape[0] / im.shape[1]))).save(out)
print(out)
