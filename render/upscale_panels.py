import sys, os, glob
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from PIL import Image

# RRDBNet (Real-ESRGAN x4plus architecture), minimal self-contained implementation
class RDB(nn.Module):
    def __init__(self, nf=64, gc=32):
        super().__init__()
        self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1); self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1)
        self.conv3 = nn.Conv2d(nf + 2*gc, gc, 3, 1, 1); self.conv4 = nn.Conv2d(nf + 3*gc, gc, 3, 1, 1)
        self.conv5 = nn.Conv2d(nf + 4*gc, nf, 3, 1, 1); self.lrelu = nn.LeakyReLU(0.2, True)
    def forward(self, x):
        x1 = self.lrelu(self.conv1(x)); x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
        x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1))); x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
        x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1)); return x5 * 0.2 + x
class RRDB(nn.Module):
    def __init__(self, nf, gc=32):
        super().__init__(); self.rdb1 = RDB(nf, gc); self.rdb2 = RDB(nf, gc); self.rdb3 = RDB(nf, gc)
    def forward(self, x):
        out = self.rdb3(self.rdb2(self.rdb1(x))); return out * 0.2 + x
class RRDBNet(nn.Module):
    def __init__(self, nf=64, nb=23, gc=32):
        super().__init__()
        self.conv_first = nn.Conv2d(3, nf, 3, 1, 1)
        self.body = nn.Sequential(*[RRDB(nf, gc) for _ in range(nb)])
        self.conv_body = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_up1 = nn.Conv2d(nf, nf, 3, 1, 1); self.conv_up2 = nn.Conv2d(nf, nf, 3, 1, 1)
        self.conv_hr = nn.Conv2d(nf, nf, 3, 1, 1); self.conv_last = nn.Conv2d(nf, 3, 3, 1, 1)
        self.lrelu = nn.LeakyReLU(0.2, True)
    def forward(self, x):
        feat = self.conv_first(x); feat = feat + self.conv_body(self.body(feat))
        feat = self.lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode='nearest')))
        feat = self.lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode='nearest')))
        return self.conv_last(self.lrelu(self.conv_hr(feat)))

def load_model(path):
    sd = torch.load(path, map_location='cpu')
    sd = sd.get('params_ema', sd.get('params', sd))
    m = RRDBNet(); m.load_state_dict(sd, strict=True); m.eval(); return m

@torch.no_grad()
def upscale(model, img, tile=256, pad=16):
    x = torch.from_numpy(np.array(img).astype(np.float32) / 255.).permute(2, 0, 1).unsqueeze(0)
    _, _, h, w = x.shape; out = torch.zeros(1, 3, h*4, w*4)
    for y in range(0, h, tile):
        for xx in range(0, w, tile):
            y0, y1 = max(0, y-pad), min(h, y+tile+pad); x0, x1 = max(0, xx-pad), min(w, xx+tile+pad)
            o = model(x[:, :, y0:y1, x0:x1])
            ty, tx = (y-y0)*4, (xx-x0)*4; hh, ww = min(tile, h-y)*4, min(tile, w-xx)*4
            out[:, :, y*4:y*4+hh, xx*4:xx*4+ww] = o[:, :, ty:ty+hh, tx:tx+ww]
    arr = (out.squeeze(0).permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype(np.uint8)
    return Image.fromarray(arr)

if __name__ == '__main__':
    src_dir, dst_dir, weights = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(dst_dir, exist_ok=True); torch.set_num_threads(os.cpu_count() or 4)
    model = load_model(weights)
    for p in sorted(glob.glob(os.path.join(src_dir, 'panel*.png'))):
        img = Image.open(p).convert('RGB'); out = upscale(model, img)
        out.save(os.path.join(dst_dir, os.path.basename(p))); print(os.path.basename(p), img.size, '->', out.size, flush=True)
