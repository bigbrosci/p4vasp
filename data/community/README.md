# 交流二维码

用户于2026-11-01提供原始JPG，按字节保存在 `figures/` 目录，未重新编码：

- `QQ.jpg`：p4vasp QQ群，群号1131610080。
- `WeChat.jpg`：昵称BigBroSci的微信二维码；昵称不作为微信号。
- `public-account.jpg`：微信公众号二维码。

入口：Database → Resources → Help and Support。点击图片可放大、按100%查看或勾选查看原图；QQ群号可复制。界面只在内存中截取二维码区域和缩放显示，完整原图保留。未实测手机扫码或账号有效期；二维码过期时应由维护者替换图片。若新图尺寸或排版改变，同时调整 `lib/p4vasp/gtk3/community.py` 中的裁剪区域，并核验完整二维码及边缘没有被裁掉。不要重新生成或描画二维码。

2026-11-11：图片移至仓库根目录 `figures/`，新增用户提供的 `QQgroup_V.jpg`（大师兄科研群-V，群号1012023869）。本目录仅保留迁移说明，维护入口见 `figures/README.md`。
