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
| `--view front` | 从 +y 观察，x 向右、z 向上（与 side 相同） / Look from +y, x right, z up (same as side) |
| `--view side` | 绕 x 轴旋转 −90°，从 +y 观察，x 向右、z 向上 / Rotate −90° about x; look from +y, x right, z up |
| `--rotate=30x,-20y,10z` | 在预设视图之后，按书写顺序绕固定笛卡尔轴旋转，单位度、右手规则 / Apply right-handed rotations about fixed Cartesian axes in written order after the view preset |
| `--size 1200x900` | 像素尺寸，默认 1000x1000；每边 32–8192，总计不超过 3200 万像素 / Pixel dimensions and limits |
| `--radius-scale 0.5` | 原子半径倍率，默认 0.5 / Atom radius multiplier |
| `--no-cell` | 隐藏晶胞边框，仅按原子范围适配画面 / Hide cell and fit atoms |
| `--transparent` | 透明背景（默认） / Transparent background (default) |
| `--white-background` | 不透明白色背景 / Opaque white background |
| `--no-clobber` | 已有文件时拒绝覆盖 / Refuse to overwrite an existing file |
| `--force` | 替换已有 PNG（默认） / Replace an existing PNG (default) |

旋转角为负数时使用等号，如 `--rotate=-30x`。这里的旋转只影响图片，且采用右手规则；不要与历史 GUI Rotate applet 的角度符号约定混淆。文件名 `top.png` 本身不决定视角。视角对应笛卡尔方向，而不是非正交晶胞的晶格方向。

Use `=` for a negative first angle, e.g. `--rotate=-30x`. These rotations affect only the image and use the right-hand rule, which differs from the historical GUI Rotate applet's sign convention. The output filename does not select the view. Views refer to Cartesian axes, not lattice directions in a nonorthogonal cell.

## 模型和画质 / Models and image quality

```bash
p4v POSCAR -o molecule.png --model ball-stick --no-cell --quality 3
p4v POSCAR -o sticks.png --model stick --bond-radius 0.08
p4v POSCAR -o bright.png --model ball-stick --brightness 1.15 --size 1600x1200
```

- `--model spheres`：默认球体模式，保留原有大小。Original sphere sizes (default).
- `--model ball-stick`：较小球体＋按两端元素着色的键。Smaller spheres with two-color bonds.
- `--model stick`：棍状模型，原子位置使用与棍等半径的小球连接。Sticks with small spherical joints.
- `--model space-filling`：使用项目半径表的较大球体；这是视觉填充模式，并非经过校准的范德华半径模型。Larger project-radius spheres, not a calibrated van der Waals model.
- `--radius-scale`：所有球体模式的大小倍率；stick 模式由 `--bond-radius` 控制。Sphere size multiplier; stick joints follow bond radius.
- `--bond-radius`：键半径，默认 0.10 Å。Bond radius in angstroms.
- `--bond-factor`：成键距离上限为共价半径之和乘此倍率，默认 1.15；仅是显示启发式。Distance cutoff multiplier (default 1.15), a visualization heuristic.
- `--brightness`：亮度倍率，默认 1.0；提高会逐渐截断高亮颜色。Brightness multiplier; high values clip colors.
- `--quality 1|2|3|4`：超采样倍率，默认 2；改善球体与键边缘。工作图最多 6400 万像素，超限会提示降低质量或尺寸。Supersampling factor, default 2, limited to 64 million working pixels.

采用较集中的柔和高光、渐变阴影和超采样抗锯齿，默认透明背景。Cairo 正交投影使用 `data/atomtypes.xml` 的颜色、半径和共价半径；未知元素显示为灰色，不自动成键。

Soft localized highlights, shaded bonds and supersampling improve appearance. Transparency remains the default. Colors and radii come from the project table; unknown elements are gray and do not acquire automatic bonds.

仅连接输入文件内的原子，不自动复制周期镜像或跨晶胞连键，不显示标签。使用深度排序近似遮挡，复杂交叠可能存在绘制瑕疵，不是 OpenGL 窗口截图。成键搜索为两两比较，超大结构可能较慢。GUI 未改动。

Only atoms present in the input are connected: no periodic replicas, cross-boundary bonds or labels. Depth sorting approximates occlusion and can show artifacts at complex intersections. This is not an OpenGL screenshot. Pairwise bond search can be slow on large structures. The GUI is unchanged.

## 材质试用 / Material previews

```bash
p4v POSCAR -o matte.png --view side --model space-filling --material matte --quality 3
p4v POSCAR -o glossy.png --view side --model space-filling --material glossy --quality 3
```

`--material classic|matte|glossy` controls sphere and bond shading. `matte` is the default, selected after the user compared the previews. `matte` reduces white reflection and softens edge shadows; `glossy` uses a smaller, stronger highlight. Compare with the same brightness (start at 1.0), size and view. These are Cairo shading presets, not physical materials or ambient occlusion.

材质选项：`classic` 保留旧版效果；`matte` 为默认，减弱白色反光和边缘阴影；`glossy` 使用更小、更强的高光。对比时保持亮度（建议先用 1.0）、尺寸和视角一致。这仍是 Cairo 渐变着色，未新增真实三维光照或接触阴影。

## GUI export from the current view / 从当前视角导出

1. Open a structure, then rotate, zoom and position it in the structure window.
2. In **Control** (Structure → Control), click the camera button **Export PNG**. The older combined Structure applet has the same entry.
3. The panel opens with a preview, matte material and transparent background. Choose a model, width, quality or brightness as needed.
4. Click **Export PNG…** and choose a filename. The actual export captures the latest view, even if you rotated after opening the panel. **Refresh preview** updates the preview after changing the view or numeric settings.

在模型窗口调整角度、缩放和平移后，进入 **Control**，点击相机图标（提示为 **Export PNG**）。面板默认哑光、透明背景，选择文件名即可导出，无需重新设置旋转角度。面板打开后继续旋转时，可以点击 **Refresh preview** 更新预览；实际导出始终读取保存时的最新视角。图片高度按模型窗口比例计算。

The exporter copies the native camera matrix, zoom, translation and projection, plus the currently displayed structure/frame, hidden-atom state and cell repetitions. It preserves framing rather than automatically fitting the structure; atoms outside the window remain outside the output. Cell visibility follows the window. No temporary POSCAR or changes to the original structure are needed. Rendering runs in a background worker; errors remain visible in the panel. GUI file selection confirms replacement of existing files.

导出读取当前显示帧、隐藏原子、晶胞复制数量及边框开关，保持窗口构图，不自动重新居中。模型如果在窗口边缘被裁切，导出也会裁切。渲染在后台运行，错误显示在面板中，原结构不变。

This exports atoms, optional inferred bonds and cell edges using the Cairo renderer, not an OpenGL screenshot. Selection markers, arrows and isosurfaces are omitted. Depth ordering remains approximate; perspective atom radii use center-depth scaling and near/far clipping is approximate. Custom native colors/bond lists are not copied. Transparent pixels may appear white in the GTK preview because the panel behind them is white; saved PNG pixels retain alpha.

当前导出原子、可选的推断键及晶胞，不包括选择标记、箭头、等值面或自定义原生颜色/键列表。遮挡和透视球体轮廓仍为近似。预览背景可能看起来是面板的白色，但 PNG 保留透明通道。
