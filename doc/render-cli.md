# 无窗口导出结构图片 / Headless structure images

配置好 `p4v` 别名后，可直接使用以下命令；也可以将 `p4v` 替换为仓库中的 `bash p4v.sh`。
With the `p4v` alias configured, use these commands; otherwise use `bash p4v.sh` from the checkout.

```bash
p4v POSCAR -o top.png
p4v POSCAR -o side.png --view side
p4v POSCAR -o front.png --view front
p4v POSCAR -o rotated.png --rotate=30x,-20y,10z
p4v POSCAR -o transparent.png --transparent --no-cell --size 1600x1200
p4v POSCAR -o top.png --force
```

无需打开窗口，也不需要 DISPLAY、Wayland 或 ASE。需要当前 Python 环境安装 pycairo（Ubuntu 包为 `python3-cairo`，安装流程已包含）。不带 `-o` 时仍正常启动 GUI。输入支持 POSCAR/CONTCAR，输出当前仅支持 PNG，输入结构不会被修改。

No window, display server or ASE is needed. Requires pycairo in the launcher's Python environment (already included by the installer). Without `-o`, the GUI starts as usual. Input is POSCAR/CONTCAR; output is PNG only. The input structure is never modified.

| 参数 / Option | 含义 / Meaning |
| --- | --- |
| `--view top` | 默认从 +z 看向原点，x 向右、y 向上 / Default: look from +z, x right, y up |
| `--view front` | 从 +y 观察，x 向右、z 向下 / Look from +y, x right, z down |
| `--view side` | 从 +x 观察，z 向左、y 向上 / Look from +x, z left, y up |
| `--rotate=30x,-20y,10z` | 在预设视图之后，按书写顺序绕固定笛卡尔轴旋转，单位度、右手规则 / Apply right-handed rotations about fixed Cartesian axes in written order after the view preset |
| `--size 1200x900` | 像素尺寸，默认 1000x1000；每边 32–8192，总计不超过 3200 万像素 / Pixel dimensions and limits |
| `--radius-scale 0.5` | 原子半径倍率，默认 0.5 / Atom radius multiplier |
| `--no-cell` | 隐藏晶胞边框，仅按原子范围适配画面 / Hide cell and fit atoms |
| `--transparent` | 透明背景（默认） / Transparent background (default) |
| `--white-background` | 不透明白色背景 / Opaque white background |
| `--force` | 允许替换已有 PNG，默认拒绝覆盖 / Allow replacing an existing PNG |

旋转角为负数时使用等号，如 `--rotate=-30x`。这里的旋转只影响图片，且采用右手规则；不要与历史 GUI Rotate applet 的角度符号约定混淆。文件名 `top.png` 本身不决定视角。视角对应笛卡尔方向，而不是非正交晶胞的晶格方向。

Use `=` for a negative first angle, e.g. `--rotate=-30x`. These rotations affect only the image and use the right-hand rule, which differs from the historical GUI Rotate applet's sign convention. The output filename does not select the view. Views refer to Cartesian axes, not lattice directions in a nonorthogonal cell.

当前使用 Cairo 正交投影，沿用 `data/atomtypes.xml` 的颜色和半径；未知元素显示为灰色。绘制输入原子和晶胞，不自动复制周期镜像，不绘制化学键或文字标签。球体按中心深度排序，晶胞线先绘制，因此不是完整三维遮挡计算，也不是 OpenGL 窗口的逐像素截图。

This Cairo renderer uses orthographic projection and project element colors/radii. Unknown elements are gray. It draws input atoms and cell edges, without periodic replicas, bonds or labels. Spheres are sorted by center depth and cell lines drawn first; this is approximate occlusion, not a pixel-identical OpenGL screenshot.
