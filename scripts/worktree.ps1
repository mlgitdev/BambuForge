# 3D-Automation Git Worktree Automation for PowerShell
# Usage:
#   .\scripts\worktree.ps1 new <branch-name> [base-branch]
#   .\scripts\worktree.ps1 list
#   .\scripts\worktree.ps1 remove <branch-or-folder> [-Force] [-DeleteBranch]
#   .\scripts\worktree.ps1 merge-back <source-branch> [target-branch]
#   .\scripts\worktree.ps1 finish <source-branch> [target-branch] [-Force]
#   .\scripts\worktree.ps1 sync-remote [remote-name]
#   .\scripts\worktree.ps1 prune
#   .\scripts\worktree.ps1 help

param(
    [Parameter(Position = 0)]
    [ValidateSet("new", "list", "remove", "merge-back", "finish", "sync-remote", "prune", "help")]
    [string]$Action = "help",

    [Parameter(Position = 1)]
    [string]$Branch = "",

    [Parameter(Position = 2)]
    [string]$Base = "main",

    [switch]$Force,

    [switch]$DeleteBranch
)

$GitCommonDir = (git rev-parse --git-common-dir 2>$null)
if (-not $GitCommonDir) {
    Write-Error "Not inside a git repository."
    exit 1
}
$RepoRoot = (Resolve-Path (Join-Path $GitCommonDir "..")).Path
$WorktreesDir = Join-Path $RepoRoot ".worktrees"
$RootVenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

function Show-Usage {
    Write-Host ""
    Write-Host "3D-Automation Git Worktree Manager" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host "Enables multi-agent task isolation without dirtying the root checkout or colliding with concurrent agents."
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\scripts\worktree.ps1 new <branch-name> [base-branch]      Create an isolated worktree under .worktrees/" -ForegroundColor Yellow
    Write-Host "  .\scripts\worktree.ps1 list                                 List all active worktrees" -ForegroundColor Yellow
    Write-Host "  .\scripts\worktree.ps1 remove <branch-or-folder> [-Force] [-DeleteBranch]  Safely remove a worktree (and optional branch)" -ForegroundColor Yellow
    Write-Host "  .\scripts\worktree.ps1 merge-back <source> [target]         Merge feature/sub branch back into target (default: main)" -ForegroundColor Yellow
    Write-Host "  .\scripts\worktree.ps1 finish <source> [target] [-Force]    Merge into target, remove worktree, and delete agent branch" -ForegroundColor Yellow
    Write-Host "  .\scripts\worktree.ps1 sync-remote [remote-name]            Fetch and sync with sibling bambuforge or origin" -ForegroundColor Yellow
    Write-Host "  .\scripts\worktree.ps1 prune                                Prune stale/deleted worktree references" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Naming Conventions:"
    Write-Host "  Models:      model/<short-descriptor>  (e.g. model/pegasus-mouthguard, model/desk-organizer)" -ForegroundColor DarkGray
    Write-Host "  Features:    feat/<short-descriptor>   (e.g. feat/arch-straw-v2, feat/infill-modifier)" -ForegroundColor DarkGray
    Write-Host "  Bug Fixes:   fix/<short-descriptor>    (e.g. fix/rod-socket-clearance)" -ForegroundColor DarkGray
    Write-Host "  Sub-tasks:   sub/<parent>/<task>       (e.g. sub/pegasus/hinge-test)" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Remotes:"
    Write-Host "  bambuforge   Sibling Git repository: ../BambuForge" -ForegroundColor DarkGray
    Write-Host "  origin       GitHub remote repository: https://github.com/mlgitdev/BambuForge.git" -ForegroundColor DarkGray
    Write-Host ""
}

function Sanitize-BranchPath([string]$b) {
    $clean = $b -replace "[/\\:]", "-"
    $clean = $clean -replace "[^a-zA-Z0-9_\.\-]", ""
    return $clean
}

function New-Worktree {
    if (-not $Branch) {
        Write-Error "Missing required branch-name. Example: .\scripts\worktree.ps1 new model/desk-organizer"
        exit 1
    }

    $validPrefixes = @("model/", "feat/", "fix/", "task/", "sub/", "docs/", "perf/", "refactor/", "test/", "chore/")
    $hasValidPrefix = $false
    foreach ($p in $validPrefixes) {
        if ($Branch.StartsWith($p)) {
            $hasValidPrefix = $true
            break
        }
    }

    if (-not $hasValidPrefix) {
        Write-Host "[!] Warning: Branch '$Branch' does not start with standard prefix (model/, feat/, fix/, task/, sub/)." -ForegroundColor Yellow
    }

    $folderName = Sanitize-BranchPath $Branch
    $targetPath = Join-Path $WorktreesDir $folderName

    if (Test-Path $targetPath) {
        Write-Error "Worktree directory already exists: $targetPath"
        exit 1
    }

    if (-not (Test-Path $WorktreesDir)) {
        New-Item -ItemType Directory -Path $WorktreesDir -Force | Out-Null
    }

    # Check if branch exists locally
    $branchExists = (git branch --list $Branch)
    if ($branchExists) {
        Write-Host "[+] Adding worktree for existing branch '$Branch' at $targetPath..." -ForegroundColor Cyan
        git worktree add $targetPath $Branch
    } else {
        # Check if remote branch exists on bambuforge or origin
        $remoteRef = "bambuforge/$Branch"
        $remoteExists = (git branch -r --list $remoteRef)
        if (-not $remoteExists) {
            $remoteRef = "origin/$Branch"
            $remoteExists = (git branch -r --list $remoteRef)
        }

        if ($remoteExists) {
            Write-Host "[+] Creating worktree tracking remote '$remoteRef' at $targetPath..." -ForegroundColor Cyan
            git worktree add -b $Branch $targetPath $remoteRef
        } else {
            Write-Host "[+] Creating new branch '$Branch' from '$Base' in worktree at $targetPath..." -ForegroundColor Cyan
            git worktree add -b $Branch $targetPath $Base
        }
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create git worktree."
        exit $LASTEXITCODE
    }

    Write-Host ""
    Write-Host "Worktree ready!" -ForegroundColor Green
    Write-Host "Location:  $targetPath" -ForegroundColor White
    Write-Host "Branch:    $Branch" -ForegroundColor White
    if (Test-Path $RootVenvPython) {
        Write-Host "Shared Python: $RootVenvPython" -ForegroundColor DarkGray
    }
    Write-Host ""
    Write-Host "To start working in this worktree:"
    Write-Host "  cd `"$targetPath`"" -ForegroundColor Yellow
    Write-Host "  & `"`$RepoRoot\.venv\Scripts\python.exe`" <your_script.py>" -ForegroundColor Yellow
    Write-Host ""
}

function List-Worktrees {
    Write-Host ""
    Write-Host "Active Git Worktrees:" -ForegroundColor Cyan
    git worktree list
    Write-Host ""
}

function Remove-Worktree {
    if (-not $Branch) {
        Write-Error "Missing required branch or folder name. Example: .\scripts\worktree.ps1 remove model-desk-organizer"
        exit 1
    }

    $folderName = Sanitize-BranchPath $Branch
    $targetPath = Join-Path $WorktreesDir $folderName

    if (-not (Test-Path $targetPath)) {
        $candidate = Join-Path $WorktreesDir $Branch
        if (Test-Path $candidate) {
            $targetPath = $candidate
        }
    }

    if (-not (Test-Path $targetPath)) {
        Write-Error "Worktree path not found: $targetPath"
        exit 1
    }

    Write-Host "[+] Removing worktree at $targetPath..." -ForegroundColor Yellow
    if ($Force) {
        git worktree remove --force $targetPath
    } else {
        git worktree remove $targetPath
    }

    git worktree prune
    if ($DeleteBranch -and (git branch --list $Branch)) {
        git branch -d $Branch
        if ($LASTEXITCODE -ne 0 -and $Force) {
            git branch -D $Branch
        }
    }
    Write-Host "[OK] Worktree removed and pruned successfully." -ForegroundColor Green
}

function Finish-Worktree {
    if (-not $Branch) {
        Write-Error "Missing required source branch. Example: .\scripts\worktree.ps1 finish model/desk-organizer main"
        exit 1
    }

    $source = $Branch
    $target = if ($Base) { $Base } else { "main" }

    Push-Location $RepoRoot
    try {
        Merge-Back
        $folderName = Sanitize-BranchPath $source
        $wtPath = Join-Path $WorktreesDir $folderName
        if (Test-Path $wtPath) {
            Write-Host "[+] Removing merged worktree at $wtPath..." -ForegroundColor Yellow
            if ($Force) {
                git worktree remove --force $wtPath
            } else {
                git worktree remove $wtPath
            }
        }
        git worktree prune
        if (git branch --list $source) {
            Write-Host "[+] Deleting merged temporary branch '$source'..." -ForegroundColor Yellow
            git branch -d $source
        }
        Write-Host "[OK] Finished '$source': merged into '$target', worktree removed, and temporary branch deleted." -ForegroundColor Green
    } finally {
        Pop-Location
    }
}

function Merge-Back {
    if (-not $Branch) {
        Write-Error "Missing required source branch. Example: .\scripts\worktree.ps1 merge-back model/desk-organizer main"
        exit 1
    }

    $source = $Branch
    $target = if ($Base) { $Base } else { "main" }

    Write-Host "[+] Merging branch '$source' into target '$target'..." -ForegroundColor Cyan
    git checkout $target
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Could not checkout target branch '$target'."
        exit 1
    }

    git merge --no-ff $source -m "feat(worktree): merge $source into $target"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Successfully merged $source into $target." -ForegroundColor Green
    } else {
        Write-Error "Merge conflicts detected. Please resolve conflicts in $target."
    }
}

function Sync-Remote {
    $remoteName = if ($Branch) { $Branch } else { "bambuforge" }
    Write-Host "[+] Fetching from remote '$remoteName'..." -ForegroundColor Cyan
    git fetch $remoteName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Remote '$remoteName' fetched successfully." -ForegroundColor Green
    } else {
        Write-Error "Failed to fetch from remote '$remoteName'."
    }
}

switch ($Action) {
    "new"         { New-Worktree }
    "list"        { List-Worktrees }
    "remove"      { Remove-Worktree }
    "merge-back"  { Merge-Back }
    "finish"      { Finish-Worktree }
    "sync-remote" { Sync-Remote }
    "prune"       { git worktree prune; Write-Host "[OK] Worktree list pruned." -ForegroundColor Green }
    default       { Show-Usage }
}
