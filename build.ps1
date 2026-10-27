# 3D-Automation Build & Worktree Task Runner
# Usage:
#   .\build.ps1 -Task worktree-new -Branch model/pegasus-mouthguard
#   .\build.ps1 -Task worktree-list
#   .\build.ps1 -Task worktree-remove -Branch model/pegasus-mouthguard
#   .\build.ps1 -Task worktree-merge -Branch model/pegasus-mouthguard -Base main
#   .\build.ps1 -Task worktree-sync
#   .\build.ps1 -Task worktree-prune
#   .\build.ps1 -Task env

param(
    [Parameter(Position = 0)]
    [ValidateSet("worktree-new", "worktree-list", "worktree-remove", "worktree-merge", "worktree-sync", "worktree-prune", "env", "help")]
    [string]$Task = "help",

    [Parameter(Position = 1)]
    [string]$Branch = "",

    [Parameter(Position = 2)]
    [string]$Base = "main",

    [switch]$Force
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# If running inside a .worktrees subdirectory, resolve root
$WorktreeScript = Join-Path $ScriptDir "scripts\worktree.ps1"
if (-not (Test-Path $WorktreeScript)) {
    $ParentScript = Join-Path $ScriptDir "..\..\scripts\worktree.ps1"
    if (Test-Path $ParentScript) {
        $WorktreeScript = (Resolve-Path $ParentScript).Path
    }
}

$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    $ParentVenv = Join-Path $ScriptDir "..\..\.venv\Scripts\python.exe"
    if (Test-Path $ParentVenv) {
        $VenvPython = (Resolve-Path $ParentVenv).Path
    }
}

function Show-Help {
    Write-Host ""
    Write-Host "3D-Automation Build & Worktree Manager" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "Usage: .\build.ps1 [-Task <Task>] [-Branch <branch>] [-Base <base>]"
    Write-Host ""
    Write-Host "Git Worktree Tasks (Multi-Agent Task Isolation):"
    Write-Host "  worktree-new    -Branch <b-name> [-Base <base>]   Create an isolated worktree under .worktrees/" -ForegroundColor Yellow
    Write-Host "  worktree-list                                     List all active worktrees" -ForegroundColor Yellow
    Write-Host "  worktree-remove -Branch <b-name> [-Force]         Safely remove a worktree and prune metadata" -ForegroundColor Yellow
    Write-Host "  worktree-merge  -Branch <src> [-Base <target>]    Merge worktree branch back into target (default: main)" -ForegroundColor Yellow
    Write-Host "  worktree-sync   [-Branch <remote>]                Fetch updates from sibling bambuforge or origin" -ForegroundColor Yellow
    Write-Host "  worktree-prune                                    Prune stale worktree references" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Environment Tasks:"
    Write-Host "  env                                               Audit Python virtual environment and tools" -ForegroundColor Yellow
    Write-Host "  help                                              Show this help message" -ForegroundColor Yellow
    Write-Host ""
}

function Verify-Env {
    Write-Host ""
    Write-Host "[+] Verifying 3D-Automation Environment..." -ForegroundColor Cyan
    if (Test-Path $VenvPython) {
        Write-Host "  [OK] Python Venv: $VenvPython" -ForegroundColor Green
        & $VenvPython -c "import build123d, trimesh; print('  [OK] build123d ' + build123d.__version__ + ' & trimesh loaded')"
    } else {
        Write-Host "  [!] Python Venv not found at $VenvPython" -ForegroundColor Yellow
    }

    $bambu = "C:\Program Files\Bambu Studio\bambu-studio.exe"
    if (Test-Path $bambu) {
        Write-Host "  [OK] Bambu Studio CLI: $bambu" -ForegroundColor Green
    } else {
        Write-Host "  [!] Bambu Studio not found at default location" -ForegroundColor Yellow
    }

    $freecad = Join-Path $env:LOCALAPPDATA "Programs\FreeCAD 1.1\bin\freecad.exe"
    if (-not (Test-Path $freecad)) {
        $freecad = "C:\Program Files\FreeCAD 1.1\bin\freecad.exe"
    }
    if (Test-Path $freecad) {
        Write-Host "  [OK] FreeCAD 1.1: $freecad" -ForegroundColor Green
    }
    Write-Host ""
}

if ($Task -eq "worktree-new") {
    & $WorktreeScript new $Branch $Base
} elseif ($Task -eq "worktree-list") {
    & $WorktreeScript list
} elseif ($Task -eq "worktree-remove") {
    if ($Force) {
        & $WorktreeScript remove $Branch -Force
    } else {
        & $WorktreeScript remove $Branch
    }
} elseif ($Task -eq "worktree-merge") {
    & $WorktreeScript merge-back $Branch $Base
} elseif ($Task -eq "worktree-sync") {
    & $WorktreeScript sync-remote $Branch
} elseif ($Task -eq "worktree-prune") {
    & $WorktreeScript prune
} elseif ($Task -eq "env") {
    Verify-Env
} else {
    Show-Help
}
