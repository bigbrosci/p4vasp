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

无需打开窗口，也不需要 DISPLAY、Wayland 或 ASE。需要当前 Python 环境安装 NumPy 和 pycairo（Ubuntu 包为 `python3-numpy python3-cairo`，安装流程已包含）。不带 `-o` 时仍正常启动 GUI。输入支持 POSCAR/CONTCAR，输出当前仅支持 PNG，输入结构不会被修改。

No window, display server or ASE is needed. Requires NumPy and pycairo in the launcher's Python environment (already included by the installer). Without `-o`, the GUI starts as usual. Input is POSCAR/CONTCAR; output is PNG only. The input structure is never modified.

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

默认 studio 导出采用逐像素球面光照、表面深度测试、柔和高光和超采样抗锯齿，保持透明背景。元素属性使用 `data/atomtypes.xml` 的颜色、半径和共价半径；未知元素显示为灰色，不自动成键。

The default studio renderer computes per-pixel surface lighting and depth, with soft highlights and supersampling. Transparency remains the default. Colors and radii come from the project table; unknown elements are gray and do not acquire automatic bonds.

仅连接输入文件内的原子，不自动复制周期镜像或跨晶胞连键，不显示标签。studio 对球体和圆头键逐像素求交并选择最近表面；不是 OpenGL 窗口截图。成键搜索为两两比较，超大结构可能较慢。交互模型窗口仍使用轻量原生渲染。

Only atoms present in the input are connected: no periodic replicas, cross-boundary bonds or labels. Studio uses analytic sphere/capsule intersections and nearest-surface depth for occlusion. This is not an OpenGL screenshot. Pairwise bond search can be slow on large structures. The interactive model window retains its lightweight native renderer.

## 材质试用 / Material previews

```bash
p4v POSCAR -o matte.png --view side --model space-filling --material matte --quality 3
p4v POSCAR -o glossy.png --view side --model space-filling --material glossy --quality 3
```

`--material classic|matte|glossy` controls sphere and bond shading. `matte` is the default, selected after the user compared the previews. `matte` reduces white reflection and softens edge shadows; `glossy` uses a smaller, stronger highlight. Compare with the same brightness (start at 1.0), size and view. Studio applies these material presets to linear-space surface lighting. The fast renderer retains the old Cairo gradients.

材质选项：`classic` 提供较强的传统高光（精确保留旧渐变需使用 `--renderer fast`）；`matte` 为默认，减弱白色反光和边缘阴影；`glossy` 使用更小、更强的高光。对比时保持亮度（建议先用 1.0）、尺寸和视角一致。studio 使用表面法线计算光照并加入轻微的局部接触暗化近似；fast 保留旧 Cairo 渐变。未实现物理路径追踪或投射阴影。

## GUI export from the current view / 从当前视角导出

1. Open a structure, then rotate, zoom and position it in the structure window.
2. In **Control** (Structure → Control), click the camera button **Export PNG**. The older combined Structure applet has the same entry.
3. The panel opens with a preview, matte material and transparent background. Choose a model, width, quality or brightness as needed.
4. Click **Export PNG…** and choose a filename. The actual export captures the latest view, even if you rotated after opening the panel. **Refresh preview** updates the preview after changing the view or numeric settings.

在模型窗口调整角度、缩放和平移后，进入 **Control**，点击相机图标（提示为 **Export PNG**）。面板默认哑光、透明背景，选择文件名即可导出，无需重新设置旋转角度。面板打开后继续旋转时，可以点击 **Refresh preview** 更新预览；实际导出始终读取保存时的最新视角。图片高度按模型窗口比例计算。

The exporter copies the native camera matrix, zoom, translation and projection, plus the currently displayed structure/frame, hidden-atom state and cell repetitions. It preserves framing rather than automatically fitting the structure; atoms outside the window remain outside the output. Cell visibility follows the window. No temporary POSCAR or changes to the original structure are needed. Rendering runs in a background worker; errors remain visible in the panel. GUI file selection confirms replacement of existing files.

导出读取当前显示帧、隐藏原子、晶胞复制数量及边框开关，保持窗口构图，不自动重新居中。模型如果在窗口边缘被裁切，导出也会裁切。渲染在后台运行，错误显示在面板中，原结构不变。

This exports atoms, optional inferred bonds and cell edges using the export renderer, not an OpenGL screenshot. Selection markers, arrows and isosurfaces are omitted. Studio computes actual surface depth and perspective sphere intersections with the native clipping planes. Fast retains center-depth sorting and approximate perspective radii. Custom native colors/bond lists are not copied. Transparent pixels may appear white in the GTK preview because the panel behind them is white; saved PNG pixels retain alpha.

当前导出原子、可选的推断键及晶胞，不包括选择标记、箭头、等值面或自定义原生颜色/键列表。studio 使用表面深度及透视球面求交；fast 保留近似绘制。预览背景可能看起来是面板的白色，但 PNG 保留透明通道。

## 交互流畅，图片精细 / Responsive editing, detailed export

- **Interactive window:** existing FLTK/OpenGL rendering stays lightweight. Rotating, selecting and building never invokes the studio renderer; its NumPy code is loaded only on export/preview.
- **GUI preview:** studio at 520-pixel width and 1x sampling, rendered on demand in a worker. Final export uses the chosen width and quality. Closing the panel requests cancellation; failed/cancelled renders do not replace existing output.
- **Final images:** `--renderer studio` is the default, with analytic sphere and round-ended bond intersections, surface-normal lighting, linear/sRGB conversion, smooth highlight rolloff and supersampling. Local contact darkening is a finite-distance heuristic, not physical ambient occlusion or path tracing.
- **Fallback:** `--renderer fast` retains the previous Cairo gradients. This option changes exported images only; it is unrelated to native window quality.
- CPU work is tiled to bound temporary depth/normal memory. Export still consumes CPU and time; very large models or high resolution can take longer and compete for machine resources. GUI event-loop responsiveness is tested, not a guaranteed frame rate on every device.

交互建模以流畅为先，不加载高质量渲染器；只有导出面板预览或实际导出才计算 studio 图像。预览为低分辨率、1 倍采样，最终图片使用所选尺寸和质量。保留当前视角、透明背景、哑光默认值；关闭面板会请求取消，取消或失败不会替换已有图片。CPU 分块处理控制临时内存，但高分辨率/超大模型仍会增加等待时间。

```bash
p4v POSCAR -o model.png --view side --model space-filling --quality 3
p4v POSCAR -o quick.png --renderer fast --quality 1
```

## 生成复现命令与批量导出 / Replay commands and batch export

GUI 导出默认勾选 **Save reusable command, view preset and structure snapshot**。成功后，面板显示最后一次成功导出的命令，点击 **Copy command** 可复制。PNG 旁同时保存：

| 文件示例 / File | 用途 / Purpose |
| --- | --- |
| `model.png.POSCAR` | 当前显示帧的基础几何快照，复制和隐藏由配置重放 / Base geometry of the displayed frame, before replicas/hidden filtering |
| `model.png.view.json` | 相机矩阵、缩放、平移、投影、窗口比例、重复/隐藏及图片设置 / Camera, repetitions/hidden indices and render options |
| `model.png.command.txt` | 可复制运行的完整命令 / Complete replay command |

配套文件若已存在，会采用 `.replay-2` 等新前缀，不覆盖既有文件。取消勾选可仅保存 PNG。几何快照用于图片复现，不保存计算设置或选择性动力学标记。

The checkbox is enabled by default. Copy the last successful export command from the panel, or read its `.command.txt` file later. Existing companions are preserved with a new replay suffix. Uncheck the option to save only a PNG. The snapshot contains rendering geometry, not calculation settings or selective-dynamics flags.

生成的命令优先使用当前 checkout 的绝对 `p4v.sh` 路径，确保从其他目录运行时也能找到程序；已有 `p4v` 别名时可以简写为：

```bash
p4v model.png.POSCAR -o model.png --preset model.png.view.json
```

The generated command uses the absolute launcher/input/preset paths where available and quotes shell arguments safely. With a `p4v` alias, the shorter form above is equivalent. On another machine, copy the snapshot and preset and use that machine's launcher/paths. JSON presets are data only; no command in them is executed.

同一输入快照、同一软件环境及同一配置可复现原图。批量处理类似结构时，替换输入和输出，保留配置文件；显式图片参数可覆盖配置，例如 `--size 1600x1200 --quality 3`。不能将 `--preset` 与 `--view` 或 `--rotate` 混用，因为配置已经保存完整相机。

```bash
for structure in calculations/*/POSCAR; do
    [ -f "$structure" ] || continue
    p4v "$structure" -o "${structure%/POSCAR}/model.png" --preset /path/to/model.png.view.json
done
```

The same snapshot, software environment and preset reproduce the image. For batches, replace only input/output while retaining the preset. Explicit image options override stored settings. `--preset` cannot be combined with `--view`/`--rotate`.

配置保留固定相机和构图，不自动对齐、居中或适配另一结构。批处理输入应采用可比的坐标方向、位置和尺度；隐藏原子按 **0 起始原子索引** 记录，因此应保持相同的原子顺序。越界隐藏索引会报错；需要保留全部原子时，可将配置中的 `display.hidden` 改为空列表。

Presets retain framing rather than aligning or fitting other structures. Use comparable axes, origin and dimensions. Hidden atoms use zero-based indices and require compatible ordering; out-of-range indices fail. Set `display.hidden` to `[]` when all atoms should be included.
