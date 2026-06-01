import os
import torch

BATCH_SIZE     = 4
IMG_SIZE       = 256   # Random crop size from 400×600
FULL_SIZE      = (400, 600) 
EVAL_SIZE      = (400, 600) 
TOTAL_EPOCHS   = 300
LR_PEAK        = 2e-4
LR_MIN         = 1e-6
WARMUP_EPOCHS  = 10
WEIGHT_DECAY   = 1e-4
NUM_WORKERS    = 2
EVAL_EVERY     = 5
SAVE_EVERY     = 10
PATIENCE       = 50

# Loss weights 
LAMBDA_CHAR   = 1.0
LAMBDA_PERCEP = 0.1
LAMBDA_SSIM   = 0.2
LAMBDA_ILLUM  = 0.15
MU_SMOOTH     = 0.05  # Decomposition smoothness weight


# ── CELL 4 : Architecture  ────
import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange

class DepthwiseSeparableConv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, padding=1):
        super().__init__()
        self.depthwise = nn.Conv2d(in_channels, in_channels, kernel_size=kernel_size,
                                   padding=padding, groups=in_channels, bias=False)
        self.pointwise = nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)

    def forward(self, x):
        return self.pointwise(self.depthwise(x))

class RDN(nn.Module):
    """Retinex Decomposition Network — hidden_dim=48 (paper spec)"""
    def __init__(self, in_channels=3, hidden_dim=48):
        super().__init__()
        self.net = nn.Sequential(
            DepthwiseSeparableConv(in_channels, hidden_dim),
            nn.InstanceNorm2d(hidden_dim), nn.ReLU(inplace=True),
            DepthwiseSeparableConv(hidden_dim, hidden_dim),
            nn.InstanceNorm2d(hidden_dim), nn.ReLU(inplace=True),
            DepthwiseSeparableConv(hidden_dim, hidden_dim),
            nn.InstanceNorm2d(hidden_dim), nn.ReLU(inplace=True),
            DepthwiseSeparableConv(hidden_dim, 4)  # 3 (R) + 1 (L)
        )

    def forward(self, I_low):
        out = self.net(I_low)
        return torch.sigmoid(out[:, :3]), torch.sigmoid(out[:, 3:])

class IFE(nn.Module):
    """Illumination Factor Estimator — hidden_dim=24 (paper spec)"""
    def __init__(self, hidden_dim=24):
        super().__init__()
        self.net = nn.Sequential(
            DepthwiseSeparableConv(1, hidden_dim), nn.ReLU(inplace=True),
            DepthwiseSeparableConv(hidden_dim, hidden_dim), nn.ReLU(inplace=True),
            DepthwiseSeparableConv(hidden_dim, 1), nn.Sigmoid()
        )

    def forward(self, L_hat):
        return self.net(L_hat)

class IGSA(nn.Module):
    """Illumination-Guided Self-Attention — dim=320 (paper spec)"""
    def __init__(self, dim=320, num_heads=8):
        super().__init__()
        self.num_heads = num_heads
        self.scale = (dim // num_heads) ** -0.5
        self.qkv  = nn.Linear(dim, dim * 3, bias=False)
        self.proj = nn.Linear(dim, dim)

    def forward(self, x, alpha_pooled):
        B, N, C = x.shape
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        # Alpha-conditioned attention (Paper Equation 5)
        q = q * alpha_pooled.unsqueeze(1)
        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        out  = (attn @ v).transpose(1, 2).reshape(B, N, C)
        return self.proj(out)

class IGTEBlock(nn.Module):
    def __init__(self, dim=320, num_heads=8):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn  = IGSA(dim, num_heads)
        self.norm2 = nn.LayerNorm(dim)
        self.ffn   = nn.Sequential(
            nn.Linear(dim, dim * 2), nn.GELU(), nn.Linear(dim * 2, dim)
        )

    def forward(self, x, alpha_pooled):
        x = x + self.attn(self.norm1(x), alpha_pooled)
        x = x + self.ffn(self.norm2(x))
        return x

class IGTE(nn.Module):
    """Illumination-Guided Transformer Enhancer — dim=320, depth=6"""
    def __init__(self, dim=320, depth=6, patch_size=8):
        super().__init__()
        self.patch_size = patch_size
        self.conv1x1    = nn.Conv2d(1, 1, kernel_size=1)
        self.patch_embed = nn.Conv2d(1, dim, kernel_size=patch_size, stride=patch_size)
        self.blocks     = nn.ModuleList([IGTEBlock(dim=dim) for _ in range(depth)])
        self.patch_reconstruct = nn.ConvTranspose2d(dim, 1, kernel_size=patch_size, stride=patch_size)
        self.conv3x3    = nn.Conv2d(1, 1, kernel_size=3, padding=1)

    def forward(self, L_hat, alpha):
        x = self.conv1x1(L_hat)
        x = self.patch_embed(x)
        B, C, H_p, W_p = x.shape
        x = rearrange(x, 'b c h w -> b (h w) c')
        alpha_pooled = F.avg_pool2d(alpha, kernel_size=self.patch_size, stride=self.patch_size)
        alpha_pooled = rearrange(alpha_pooled, 'b c h w -> b (h w) c')

        for block in self.blocks:
            x = block(x, alpha_pooled)

        x = rearrange(x, 'b (h w) c -> b c h w', h=H_p, w=W_p)
        L_enh = self.patch_reconstruct(x)
        L_enh = self.conv3x3(L_enh)
        return L_hat + L_enh  # Paper Equation 6

class MDTA(nn.Module):
    """Multi-Dconv Head Transposed Attention (from Restormer)"""
    def __init__(self, dim, num_heads):
        super().__init__()
        self.num_heads   = num_heads
        self.temperature = nn.Parameter(torch.ones(num_heads, 1, 1))
        self.qkv         = nn.Conv2d(dim, dim * 3, kernel_size=1, bias=False)
        self.qkv_dwconv  = nn.Conv2d(dim * 3, dim * 3, kernel_size=3, padding=1, groups=dim * 3, bias=False)
        self.project_out = nn.Conv2d(dim, dim, kernel_size=1, bias=False)

    def forward(self, x):
        b, c, h, w = x.shape
        qkv = self.qkv_dwconv(self.qkv(x))
        q, k, v = qkv.chunk(3, dim=1)

        q = rearrange(q, 'b (head c) h w -> b head c (h w)', head=self.num_heads)
        k = rearrange(k, 'b (head c) h w -> b head c (h w)', head=self.num_heads)
        v = rearrange(v, 'b (head c) h w -> b head c (h w)', head=self.num_heads)

        q = F.normalize(q, dim=-1)
        k = F.normalize(k, dim=-1)

        attn = (q @ k.transpose(-2, -1)) * self.temperature
        attn = attn.softmax(dim=-1)
        out  = (attn @ v)
        out  = rearrange(out, 'b head c (h w) -> b (head c) h w', head=self.num_heads, h=h, w=w)
        return self.project_out(out)

def window_partition(x, window_size):
    B, H, W, C = x.shape
    x = x.view(B, H // window_size, window_size, W // window_size, window_size, C)
    return x.permute(0, 1, 3, 2, 4, 5).contiguous().view(-1, window_size, window_size, C)

def window_reverse(windows, window_size, H, W):
    B = int(windows.shape[0] / (H * W / window_size / window_size))
    x = windows.view(B, H // window_size, W // window_size, window_size, window_size, -1)
    return x.permute(0, 1, 3, 2, 4, 5).contiguous().view(B, H, W, -1)

def get_window_mask(window_size, shift_size, H, W, device):
    img_mask = torch.zeros((1, H, W, 1), device=device)
    h_slices = (slice(0, -window_size), slice(-window_size, -shift_size), slice(-shift_size, None))
    w_slices = (slice(0, -window_size), slice(-window_size, -shift_size), slice(-shift_size, None))
    cnt = 0
    for h in h_slices:
        for w in w_slices:
            img_mask[:, h, w, :] = cnt
            cnt += 1
    mask_windows = window_partition(img_mask, window_size)
    mask_windows = mask_windows.view(-1, window_size * window_size)
    attn_mask = mask_windows.unsqueeze(1) - mask_windows.unsqueeze(2)
    return attn_mask.masked_fill(attn_mask != 0, float(-100.0)).masked_fill(attn_mask == 0, 0.0)

class SwinTransformerBlock(nn.Module):
    def __init__(self, dim, num_heads, window_size=8, shift_size=0):
        super().__init__()
        self.dim = dim
        self.num_heads   = num_heads
        self.window_size = window_size
        self.shift_size  = shift_size
        self.norm1 = nn.LayerNorm(dim)
        self.qkv   = nn.Linear(dim, dim * 3, bias=True)
        self.proj  = nn.Linear(dim, dim)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp   = nn.Sequential(nn.Linear(dim, dim * 4), nn.GELU(), nn.Linear(dim * 4, dim))

    def forward(self, x):
        B, C, H, W = x.shape
        x = x.permute(0, 2, 3, 1)
        shortcut = x
        x = self.norm1(x)

        if self.shift_size > 0:
            shifted_x  = torch.roll(x, shifts=(-self.shift_size, -self.shift_size), dims=(1, 2))
            attn_mask  = get_window_mask(self.window_size, self.shift_size, H, W, x.device)
        else:
            shifted_x = x
            attn_mask = None

        x_windows = window_partition(shifted_x, self.window_size)
        x_windows = x_windows.view(-1, self.window_size * self.window_size, self.dim)

        qkv = self.qkv(x_windows).reshape(
            -1, self.window_size * self.window_size, 3, self.num_heads, self.dim // self.num_heads
        ).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        q = q * (self.dim // self.num_heads) ** -0.5
        attn = q @ k.transpose(-2, -1)

        if attn_mask is not None:
            nW   = x_windows.shape[0] // B
            attn = attn.view(B, nW, self.num_heads,
                             self.window_size * self.window_size,
                             self.window_size * self.window_size)
            attn = attn + attn_mask.unsqueeze(1).unsqueeze(0)
            attn = attn.view(-1, self.num_heads,
                             self.window_size * self.window_size,
                             self.window_size * self.window_size)

        attn = attn.softmax(dim=-1)
        attn_windows = (attn @ v).transpose(1, 2).reshape(
            -1, self.window_size * self.window_size, self.dim)
        attn_windows = self.proj(attn_windows).view(-1, self.window_size, self.window_size, self.dim)

        shifted_x = window_reverse(attn_windows, self.window_size, H, W)
        if self.shift_size > 0:
            x = torch.roll(shifted_x, shifts=(self.shift_size, self.shift_size), dims=(1, 2))
        else:
            x = shifted_x

        x = shortcut + x
        x = x + self.mlp(self.norm2(x))
        return x.permute(0, 3, 1, 2)

class ReflectanceUNet(nn.Module):
    """Reflectance Refinement U-Net — base_dim=48 (paper spec)"""
    def __init__(self, in_channels=3, base_dim=48):
        super().__init__()
        self.proj_in = nn.Conv2d(in_channels, base_dim, 3, 1, 1)

        self.enc1 = nn.Sequential(
            nn.Conv2d(base_dim, base_dim * 2, 4, 2, 1),
            SwinTransformerBlock(base_dim * 2, num_heads=4, shift_size=0)
        )
        self.enc2 = nn.Sequential(
            nn.Conv2d(base_dim * 2, base_dim * 4, 4, 2, 1),
            SwinTransformerBlock(base_dim * 4, num_heads=8, shift_size=4)
        )
        self.enc3 = nn.Sequential(
            nn.Conv2d(base_dim * 4, base_dim * 8, 4, 2, 1),
            SwinTransformerBlock(base_dim * 8, num_heads=16, shift_size=0)
        )
        self.enc4 = nn.Sequential(
            nn.Conv2d(base_dim * 8, base_dim * 16, 4, 2, 1),
            SwinTransformerBlock(base_dim * 16, num_heads=32, shift_size=4)
        )

        self.up4  = nn.ConvTranspose2d(base_dim * 16, base_dim * 8, 2, 2)
        self.dec4 = MDTA(base_dim * 16, num_heads=8)
        self.up3  = nn.ConvTranspose2d(base_dim * 16, base_dim * 4, 2, 2)
        self.dec3 = MDTA(base_dim * 8, num_heads=4)
        self.up2  = nn.ConvTranspose2d(base_dim * 8, base_dim * 2, 2, 2)
        self.dec2 = MDTA(base_dim * 4, num_heads=2)
        self.up1  = nn.ConvTranspose2d(base_dim * 4, base_dim, 2, 2)
        self.dec1 = nn.Conv2d(base_dim * 2, base_dim, 3, 1, 1)
        self.proj_out = nn.Conv2d(base_dim, in_channels, 3, 1, 1)

    def forward(self, R_hat):
        x  = self.proj_in(R_hat)
        e1 = self.enc1(x)
        e2 = self.enc2(e1)
        e3 = self.enc3(e2)
        e4 = self.enc4(e3)

        d4 = self.dec4(torch.cat([self.up4(e4), e3], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d4), e2], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e1], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), x],  dim=1))

        return R_hat + self.proj_out(d1)

class RITformer(nn.Module):
    """Complete RITformer — Paper spec: ~18.4M parameters"""
    def __init__(self):
        super().__init__()
        self.rdn         = RDN(hidden_dim=48)
        self.ife         = IFE(hidden_dim=24)
        self.igte        = IGTE(dim=320, depth=6, patch_size=8)
        self.ref_refiner = ReflectanceUNet(base_dim=48)

    def forward(self, I_low):
        R_hat, L_hat = self.rdn(I_low)
        alpha  = self.ife(L_hat)
        L_star = self.igte(L_hat, alpha)
        R_star = self.ref_refiner(R_hat)
        I_enh  = R_star * L_star

        # Global residual connection
        return torch.clamp(I_enh + I_low, 0, 1)

# Sanity check
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Using device: {device}')
model = RITformer().to(device)
total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f'Model parameters: {total_params / 1e6:.2f}M (Target: 18.4M)')

with torch.no_grad():
    test_input = torch.randn(1, 3, IMG_SIZE, IMG_SIZE).to(device)
    test_output = model(test_input)
    print(f'Sanity check passed — Output shape: {test_output.shape}')





# ── CELL 6 : Loss Functions (Paper-Spec) ─────────────────────
import math
import torch.optim as optim
import torchvision.models as tv_models
from torchmetrics import PeakSignalNoiseRatio, StructuralSimilarityIndexMeasure

class CharbonnierLoss(nn.Module):
    """L_char from paper — Charbonnier loss for pixel reconstruction"""
    def __init__(self, eps=1e-3):
        super().__init__()
        self.eps = eps

    def forward(self, pred, target):
        diff = pred - target
        return torch.mean(torch.sqrt(diff * diff + self.eps ** 2))

class PerceptualLoss(nn.Module):
    """L_perceptual from paper — VGG-19 feature matching"""
    def __init__(self):
        super().__init__()
        vgg = tv_models.vgg19(weights=tv_models.VGG19_Weights.DEFAULT).features

        # Extract multiple layers for better feature matching
        self.slice1 = nn.Sequential(*list(vgg.children())[:2]).eval()   # relu1_1
        self.slice2 = nn.Sequential(*list(vgg.children())[:7]).eval()   # relu2_1
        self.slice3 = nn.Sequential(*list(vgg.children())[:12]).eval()  # relu3_1
        self.slice4 = nn.Sequential(*list(vgg.children())[:21]).eval()  # relu4_1

        for p in self.parameters():
            p.requires_grad = False

    def forward(self, pred, target):
        # ImageNet normalization
        mean = torch.tensor([0.485, 0.456, 0.406], device=pred.device).view(1, 3, 1, 1)
        std  = torch.tensor([0.229, 0.224, 0.225], device=pred.device).view(1, 3, 1, 1)
        pred_n   = (pred - mean) / std
        target_n = (target - mean) / std

        loss = 0
        for slice_fn in [self.slice1, self.slice2, self.slice3, self.slice4]:
            loss += F.l1_loss(slice_fn(pred_n), slice_fn(target_n))

        return loss / 4

class MSSSIMLoss(nn.Module):
    """Multi-Scale SSIM Loss with numerical stability"""
    def __init__(self, window_size=11):
        super().__init__()
        self.window_size = window_size
        self.window = None

    def _create_gaussian_window(self, size, channels, device):
        coords = torch.arange(size, dtype=torch.float32, device=device)  # Force FP32
        coords -= size // 2
        g = torch.exp(-(coords ** 2) / (2 * 1.5 ** 2))
        g = g / g.sum()
        g_2d = g.unsqueeze(0) * g.unsqueeze(1)
        window = g_2d.expand(channels, 1, size, size).contiguous()
        return window

    def _ssim(self, pred, target, window):
        C1 = 0.01 ** 2
        C2 = 0.03 ** 2

        # ADD: Clamp inputs to avoid extreme values
        pred = torch.clamp(pred, min=1e-8, max=1.0 - 1e-8)
        target = torch.clamp(target, min=1e-8, max=1.0 - 1e-8)

        mu_pred = F.conv2d(pred, window, padding=self.window_size//2, groups=pred.size(1))
        mu_target = F.conv2d(target, window, padding=self.window_size//2, groups=pred.size(1))

        mu_pred_sq = mu_pred ** 2
        mu_target_sq = mu_target ** 2
        mu_pred_target = mu_pred * mu_target

        sigma_pred_sq = F.conv2d(pred * pred, window, padding=self.window_size//2, groups=pred.size(1)) - mu_pred_sq
        sigma_target_sq = F.conv2d(target * target, window, padding=self.window_size//2, groups=pred.size(1)) - mu_target_sq
        sigma_pred_target = F.conv2d(pred * target, window, padding=self.window_size//2, groups=pred.size(1)) - mu_pred_target

        # ADD: Clamp negative variances
        sigma_pred_sq = torch.clamp(sigma_pred_sq, min=1e-10)
        sigma_target_sq = torch.clamp(sigma_target_sq, min=1e-10)

        ssim_map = ((2 * mu_pred_target + C1) * (2 * sigma_pred_target + C2)) / \
                   ((mu_pred_sq + mu_target_sq + C1) * (sigma_pred_sq + sigma_target_sq + C2))

        return ssim_map.mean([1, 2, 3])

    def forward(self, pred, target):
        if self.window is None or self.window.device != pred.device:
            self.window = self._create_gaussian_window(self.window_size, 3, pred.device)

        weights = [0.0448, 0.2856, 0.3001, 0.2363, 0.1333]
        levels = [pred, target]
        msssim = 0.0

        for i in range(5):
            ssim_val = self._ssim(levels[0], levels[1], self.window)

            # ADD: Check for NaN and skip
            if torch.isnan(ssim_val).any():
                return torch.tensor(0.0, device=pred.device, requires_grad=True)

            msssim += weights[i] * ssim_val

            if i < 4:
                levels[0] = F.avg_pool2d(levels[0], 2)
                levels[1] = F.avg_pool2d(levels[1], 2)

        return (1.0 - msssim).mean()

class IlluminationConsistencyLoss(nn.Module):
    """L_illum from paper — penalizes deviation between L_hat and target illumination"""
    def forward(self, L_hat, high_img):
        L_target = high_img.max(dim=1, keepdim=True).values
        return F.l1_loss(L_hat, L_target)

class DecompositionLoss(nn.Module):
    """L_decomp from paper Equation 3"""
    def __init__(self, mu=0.05):
        super().__init__()
        self.mu = mu

    def forward(self, R_hat, L_hat, I_low):
        # Reconstruction consistency
        recon_loss = F.l1_loss(R_hat * L_hat, I_low)

        # Spatial smoothness on illumination (TV regularization)
        grad_h = torch.abs(L_hat[:, :, 1:, :] - L_hat[:, :, :-1, :])
        grad_w = torch.abs(L_hat[:, :, :, 1:] - L_hat[:, :, :, :-1])
        smooth_loss = grad_h.mean() + grad_w.mean()

        return recon_loss + self.mu * smooth_loss

class RITformerLoss(nn.Module):
    """Complete loss function — Paper Equation 1"""
    def __init__(self, lambda1=1.0, lambda2=0.1, lambda3=0.2, lambda4=0.15, mu=0.05):
        super().__init__()
        self.char_loss    = CharbonnierLoss()
        self.percept_loss = PerceptualLoss()
        self.ssim_loss    = MSSSIMLoss()
        self.illum_loss   = IlluminationConsistencyLoss()
        self.decomp_loss  = DecompositionLoss(mu=mu)

        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.lambda3 = lambda3
        self.lambda4 = lambda4

    def forward(self, pred, target, L_hat, R_hat, I_low):
        loss  = self.lambda1 * self.char_loss(pred, target)
        loss += self.lambda2 * self.percept_loss(pred, target)
        loss += self.lambda3 * self.ssim_loss(pred, target)
        loss += self.lambda4 * self.illum_loss(L_hat, target)
        loss += self.decomp_loss(R_hat, L_hat, I_low)

        return loss

# ── Build optimizer and scheduler ──────────────────────────────
model     = RITformer().to(device)
criterion = RITformerLoss(
    lambda1=LAMBDA_CHAR, lambda2=LAMBDA_PERCEP,
    lambda3=LAMBDA_SSIM, lambda4=LAMBDA_ILLUM, mu=MU_SMOOTH
).to(device)

optimizer = optim.AdamW(model.parameters(), lr=LR_PEAK, weight_decay=WEIGHT_DECAY)

def lr_lambda(epoch):
    """Cosine annealing with warmup"""
    if epoch < WARMUP_EPOCHS:
        return (epoch + 1) / WARMUP_EPOCHS
    progress = (epoch - WARMUP_EPOCHS) / max(1, TOTAL_EPOCHS - WARMUP_EPOCHS)
    cosine   = 0.5 * (1 + math.cos(math.pi * progress))
    return LR_MIN / LR_PEAK + (1 - LR_MIN / LR_PEAK) * cosine

scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

# Metrics
psnr_metric = PeakSignalNoiseRatio(data_range=1.0).to(device)
ssim_metric = StructuralSimilarityIndexMeasure(data_range=1.0).to(device)

total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f'Model parameters: {total_params / 1e6:.2f}M (Target: 18.4M)')
print('Loss / optimizer / scheduler ready')
