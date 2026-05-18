param(
    [string]$Python = "python",
    [string]$FltkVersion = "1.3.11",
    [string]$FltkUrl = "https://github.com/fltk/fltk/releases/download/release-1.3.11/fltk-1.3.11-source.tar.gz",
    [string]$FltkMd5 = "75B2FD1AA2433E13ABCBB311043EAEE0",
    [string]$GccBin = "$env:USERPROFILE\scoop\apps\gcc\current\bin",
    [string]$UnixBin = "$env:USERPROFILE\scoop\apps\git\current\usr\bin"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (Test-Path -LiteralPath $GccBin) {
    $env:PATH = "$GccBin;$env:PATH"
}
if (Test-Path -LiteralPath $UnixBin) {
    $env:PATH = "$UnixBin;$env:PATH"
}

function Invoke-External {
    param(
        [string]$File,
        [string[]]$Arguments,
        [string]$WorkingDirectory = $Root
    )
    Push-Location $WorkingDirectory
    try {
        & $File @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "$File exited with code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found in PATH."
    }
}

function ConvertTo-MsysPath {
    param([string]$Path)
    $full = (Resolve-Path -LiteralPath $Path).Path
    $drive = $full.Substring(0, 1).ToLowerInvariant()
    $rest = $full.Substring(2).Replace("\", "/")
    return "/$drive$rest"
}

function Get-PythonValue {
    param([string]$Code)
    $value = & $Python -c $Code
    if ($LASTEXITCODE -ne 0) {
        throw "Python query failed: $Code"
    }
    return $value.Trim()
}

function Remove-TrailingWhitespace {
    param([string]$Path)
    $text = Get-Content -LiteralPath $Path -Raw
    $text = $text -replace "[ `t]+(?=`r?`n)", ""
    Set-Content -LiteralPath $Path -Value $text -NoNewline
}

Require-Command $Python
Require-Command "swig"
Require-Command "g++"
Require-Command "sh"
Require-Command "make"
Require-Command "curl.exe"
Require-Command "tar"

$pythonInclude = Get-PythonValue "import sysconfig; print(sysconfig.get_path('include').replace('\\', '/'))"
$pythonLib = Get-PythonValue "import sysconfig; print(sysconfig.get_config_var('LIBDIR').replace('\\', '/'))"
$pythonAbi = Get-PythonValue "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')"
$extensionSuffix = Get-PythonValue "import importlib.machinery; print(importlib.machinery.EXTENSION_SUFFIXES[0])"
$pythonLdLibrary = Get-PythonValue "import sysconfig; print(sysconfig.get_config_var('LDLIBRARY') or '')"
if ($pythonLdLibrary -match '^lib(.+)\.dll\.a$') {
    $pythonLibName = $Matches[1]
}
elseif ($pythonLdLibrary -match '^lib(.+)\.a$') {
    $pythonLibName = $Matches[1]
}
elseif ($pythonLdLibrary -match '^(.+)\.lib$') {
    $pythonLibName = $Matches[1]
}
else {
    $pythonLibName = "python$pythonAbi"
}
$rootForward = $Root.Replace("\", "/")

Write-Host "Using Python include: $pythonInclude"
Write-Host "Using Python library: $pythonLib"
Write-Host "Using Python link name: $pythonLibName"
Write-Host "Using extension suffix: $extensionSuffix"

function Ensure-Fltk {
    $extDir = Join-Path $Root "ext"
    $fltkSource = Join-Path $extDir "fltk-$FltkVersion"
    $fltkArchive = Join-Path $extDir "fltk-$FltkVersion-source.tar.gz"
    $fltkConfig = Join-Path $extDir "bin\fltk-config"
    $fltkCoreLib = Join-Path $extDir "lib\libfltk.a"
    $fltkGlLib = Join-Path $extDir "lib\libfltk_gl.a"

    if ((Test-Path -LiteralPath $fltkConfig) -and
        (Test-Path -LiteralPath $fltkCoreLib) -and
        (Test-Path -LiteralPath $fltkGlLib)) {
        Write-Host "FLTK already available in ext/."
        return
    }

    New-Item -ItemType Directory -Force -Path $extDir | Out-Null

    if (-not (Test-Path -LiteralPath $fltkArchive)) {
        Write-Host "Downloading FLTK $FltkVersion..."
        Invoke-External "curl.exe" @("-L", "--fail", "-o", $fltkArchive, $FltkUrl)
    }

    $hash = (Get-FileHash -LiteralPath $fltkArchive -Algorithm MD5).Hash
    if ($hash.ToUpperInvariant() -ne $FltkMd5.ToUpperInvariant()) {
        throw "FLTK archive MD5 mismatch. Expected $FltkMd5, got $hash."
    }

    if (-not (Test-Path -LiteralPath $fltkSource)) {
        Write-Host "Extracting FLTK $FltkVersion..."
        Invoke-External "tar" @("-xf", $fltkArchive, "-C", $extDir)
    }

    Write-Host "Building FLTK $FltkVersion libraries..."
    $sourceMsys = ConvertTo-MsysPath $fltkSource
    $gccMsys = ConvertTo-MsysPath $GccBin
    $unixMsys = ConvertTo-MsysPath $UnixBin
    $prefix = "$rootForward/ext"
    $cmd = "export PATH='${unixMsys}:${gccMsys}:`$PATH'; export CC=gcc CXX=g++ AR=gcc-ar RANLIB=gcc-ranlib; cd '$sourceMsys' && ./configure --enable-gl --prefix='$prefix' && make -C jpeg && make -C zlib && make -C png && make -C src"
    Invoke-External "sh" @("-c", $cmd)

    New-Item -ItemType Directory -Force -Path (Join-Path $extDir "bin"), (Join-Path $extDir "lib"), (Join-Path $extDir "include") | Out-Null
    Copy-Item -LiteralPath (Join-Path $fltkSource "fltk-config") -Destination $fltkConfig -Force
    Copy-Item -Path (Join-Path $fltkSource "lib\*.a") -Destination (Join-Path $extDir "lib") -Force
    Copy-Item -LiteralPath (Join-Path $fltkSource "FL") -Destination (Join-Path $extDir "include") -Recurse -Force
}

function Compile-Objects {
    param(
        [string]$Directory,
        [string[]]$Sources,
        [string[]]$Flags
    )
    Push-Location $Directory
    try {
        foreach ($source in $Sources) {
            $object = [System.IO.Path]::ChangeExtension($source, ".o")
            Write-Host "Compiling $Directory\$source"
            Invoke-External "g++" ($Flags + @("-c", $source, "-o", $object)) $Directory
        }
    }
    finally {
        Pop-Location
    }
}

Ensure-Fltk

$odpDir = Join-Path $Root "odpdom"
$srcDir = Join-Path $Root "src"
$libDir = Join-Path $Root "lib"
New-Item -ItemType Directory -Force -Path $libDir | Out-Null

Write-Host "Generating ODP SWIG wrapper..."
Invoke-External "swig" @("-python", "-c++", '-DPY_DOMEXC_MODULE=\"p4vasp.ODPdom.\"', "-Iinclude", "-o", "cODP_wrap.cpp", "ODP.i") $odpDir

$odpFlags = @(
    "-std=gnu++11", "-w",
    '-DPY_DOMEXC_MODULE=\"p4vasp.ODPdom.\"',
    "-I$pythonInclude", "-Iinclude"
)
$odpSources = @(
    "string.cpp", "markText.cpp", "Exceptions.cpp", "Node.cpp", "NodeSequences.cpp",
    "Document.cpp", "CharacterNodes.cpp", "Element.cpp", "parse.cpp", "cODP_wrap.cpp"
)
Compile-Objects $odpDir $odpSources $odpFlags

Write-Host "Generating p4vasp SWIG wrapper..."
Invoke-External "swig" @(
    "-python", "-c++", "-Wall",
    '-DPY_DOMEXC_MODULE=\"p4vasp.ODPdom.\"',
    "-DCHECK=1", "-DVERBOSE=0", "-DNO_GL_LISTS_S", "-DNO_THREADS",
    "-I../odpdom/include", "-Iinclude",
    "-o", "cp4vasp_wrap.cpp", "cp4vasp.i"
) $srcDir
Remove-TrailingWhitespace (Join-Path $srcDir "cp4vasp_wrap.cpp")

$p4vaspFlags = @(
    "-std=gnu++11", "-w",
    '-DPY_DOMEXC_MODULE=\"p4vasp.ODPdom.\"',
    "-DCHECK=1", "-DVERBOSE=0", "-DNO_GL_LISTS_S", "-DNO_THREADS",
    "-DWIN32", "-DUSE_OPENGL32",
    "-D_LARGEFILE_SOURCE", "-D_LARGEFILE64_SOURCE", "-D_FILE_OFFSET_BITS=64",
    "-I$pythonInclude", "-Iinclude", "-I../odpdom/include", "-I$rootForward/ext/include"
)
$p4vaspSources = @(
    "Exceptions.cpp", "AtomtypesRecord.cpp", "AtomInfo.cpp", "vecutils3d.cpp",
    "vecutils.cpp", "utils.cpp", "domutils.cpp", "FArray.cpp", "Structure.cpp",
    "Chgcar.cpp", "ChgcarSmear.cpp", "Process.cpp", "VisFLWindow.cpp",
    "VisMain.cpp", "VisWindow.cpp", "VisEvent.cpp", "VisDrawer.cpp",
    "VisNavDrawer.cpp", "VisStructureDrawer.cpp", "VisStructureArrowsDrawer.cpp",
    "VisIsosurfaceDrawer.cpp", "ClassInterface.cpp", "VisSlideDrawer.cpp",
    "VisPrimitiveDrawer.cpp", "VisBackEvent.cpp", "cp4vasp_wrap.cpp"
)
Compile-Objects $srcDir $p4vaspSources $p4vaspFlags

$output = Join-Path $libDir "_cp4vasp$extensionSuffix"
$p4vaspObjects = $p4vaspSources | ForEach-Object { Join-Path $srcDir ([System.IO.Path]::ChangeExtension($_, ".o")) }
$odpObjects = @(
    "string.o", "markText.o", "Exceptions.o", "Node.o", "NodeSequences.o",
    "Document.o", "CharacterNodes.o", "Element.o", "parse.o"
) | ForEach-Object { Join-Path $odpDir $_ }
$linkArgs = @(
    "-shared", "-Wl,--enable-auto-import",
    "-o", $output
) + $p4vaspObjects + $odpObjects + @(
    "-L$pythonLib", "-L$rootForward/ext/lib", "-l$pythonLibName",
    "$rootForward/ext/lib/libfltk_gl.a", "-lglu32", "-lopengl32",
    "$rootForward/ext/lib/libfltk.a", "-lole32", "-luuid", "-lcomctl32",
    "-lgdi32", "-lcomdlg32"
)

Write-Host "Linking $output"
Invoke-External "g++" $linkArgs

Copy-Item -LiteralPath (Join-Path $srcDir "cp4vasp.py") -Destination (Join-Path $libDir "cp4vasp.py") -Force
Write-Host "Built $output"
