#!/usr/bin/env bash
# 3D-Automation Git Worktree Automation for Bash (Linux & macOS)
# Usage:
#   ./scripts/worktree.sh new <branch-name> [base-branch]
#   ./scripts/worktree.sh list
#   ./scripts/worktree.sh remove <branch-or-folder> [-f|--force] [-d|--delete-branch]
#   ./scripts/worktree.sh merge-back <source-branch> [target-branch]
#   ./scripts/worktree.sh finish <source-branch> [target-branch] [-f|--force]
#   ./scripts/worktree.sh sync-remote [remote-name]
#   ./scripts/worktree.sh prune

set -e

GIT_COMMON_DIR="$(git rev-parse --git-common-dir 2>/dev/null || true)"
if [ -z "$GIT_COMMON_DIR" ]; then
    echo "[-] Error: Not inside a git repository." >&2
    exit 1
fi
REPO_ROOT="$(cd "$GIT_COMMON_DIR/.." && pwd)"
WORKTREES_DIR="$REPO_ROOT/.worktrees"
ROOT_VENV_PYTHON="$REPO_ROOT/.venv/bin/python"

show_usage() {
    echo ""
    echo "3D-Automation Git Worktree Manager (Bash)"
    echo "========================================"
    echo "Enables multi-agent task isolation without dirtying the root checkout or colliding with concurrent agents."
    echo ""
    echo "Usage:"
    echo "  ./scripts/worktree.sh new <branch-name> [base-branch]      Create an isolated worktree under .worktrees/"
    echo "  ./scripts/worktree.sh list                                 List all active worktrees"
    echo "  ./scripts/worktree.sh remove <branch-or-folder> [-f] [-d]  Safely remove a worktree (and optional branch)"
    echo "  ./scripts/worktree.sh merge-back <source> [target]         Merge feature/sub branch back into target (default: main)"
    echo "  ./scripts/worktree.sh finish <source> [target] [-f]        Merge into target, remove worktree, and delete agent branch"
    echo "  ./scripts/worktree.sh sync-remote [remote-name]            Fetch and sync with sibling bambuforge or origin"
    echo "  ./scripts/worktree.sh prune                                Prune stale/deleted worktree references"
    echo ""
    echo "Naming Conventions:"
    echo "  Models:      model/<short-descriptor>  (e.g. model/pegasus-mouthguard, model/desk-organizer)"
    echo "  Features:    feat/<short-descriptor>   (e.g. feat/arch-straw-v2, feat/infill-modifier)"
    echo "  Bug Fixes:   fix/<short-descriptor>    (e.g. fix/rod-socket-clearance)"
    echo "  Sub-tasks:   sub/<parent>/<task>       (e.g. sub/pegasus/hinge-test)"
    echo ""
    echo "Remotes:"
    echo "  bambuforge   Sibling Git repository: ../BambuForge"
    echo "  origin       GitHub remote repository: https://github.com/mlgitdev/BambuForge.git"
    echo ""
}

sanitize_branch() {
    echo "$1" | sed 's|[/\\:]|-|g' | tr -cd '[:alnum:]_.-'
}

ACTION="${1:-help}"
BRANCH="$2"
BASE="${3:-main}"
FORCE=0
DELETE_BRANCH=0

for arg in "$@"; do
    if [ "$arg" = "-f" ] || [ "$arg" = "--force" ]; then
        FORCE=1
    fi
    if [ "$arg" = "-d" ] || [ "$arg" = "--delete-branch" ]; then
        DELETE_BRANCH=1
    fi
done

case "$ACTION" in
    new)
        if [ -z "$BRANCH" ]; then
            echo "[-] Error: Missing required <branch-name>." >&2
            exit 1
        fi
        FOLDER_NAME="$(sanitize_branch "$BRANCH")"
        TARGET_PATH="$WORKTREES_DIR/$FOLDER_NAME"

        if [ -d "$TARGET_PATH" ]; then
            echo "[-] Error: Worktree directory already exists: $TARGET_PATH" >&2
            exit 1
        fi

        mkdir -p "$WORKTREES_DIR"

        if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
            echo "[+] Adding worktree for existing local branch '$BRANCH' at $TARGET_PATH..."
            git worktree add "$TARGET_PATH" "$BRANCH"
        elif git show-ref --verify --quiet "refs/remotes/bambuforge/$BRANCH"; then
            echo "[+] Creating worktree tracking remote 'bambuforge/$BRANCH' at $TARGET_PATH..."
            git worktree add -b "$BRANCH" "$TARGET_PATH" "bambuforge/$BRANCH"
        elif git show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
            echo "[+] Creating worktree tracking remote 'origin/$BRANCH' at $TARGET_PATH..."
            git worktree add -b "$BRANCH" "$TARGET_PATH" "origin/$BRANCH"
        else
            echo "[+] Creating new branch '$BRANCH' from '$BASE' in worktree at $TARGET_PATH..."
            git worktree add -b "$BRANCH" "$TARGET_PATH" "$BASE"
        fi

        echo ""
        echo "Worktree ready!"
        echo "Location:  $TARGET_PATH"
        echo "Branch:    $BRANCH"
        if [ -f "$ROOT_VENV_PYTHON" ]; then
            echo "Shared Python: $ROOT_VENV_PYTHON"
        fi
        echo ""
        echo "To start working in this worktree:"
        echo "  cd \"$TARGET_PATH\""
        echo "  \"$REPO_ROOT/.venv/bin/python\" <your_script.py>"
        echo ""
        ;;

    list)
        echo ""
        echo "Active Git Worktrees:"
        git worktree list
        echo ""
        ;;

    remove)
        if [ -z "$BRANCH" ]; then
            echo "[-] Error: Missing required <branch-or-folder>." >&2
            exit 1
        fi
        FOLDER_NAME="$(sanitize_branch "$BRANCH")"
        TARGET_PATH="$WORKTREES_DIR/$FOLDER_NAME"

        if [ ! -d "$TARGET_PATH" ] && [ -d "$WORKTREES_DIR/$BRANCH" ]; then
            TARGET_PATH="$WORKTREES_DIR/$BRANCH"
        fi

        if [ ! -d "$TARGET_PATH" ]; then
            echo "[-] Error: Worktree directory not found: $TARGET_PATH" >&2
            exit 1
        fi

        echo "[+] Removing worktree at $TARGET_PATH..."
        if [ "$FORCE" -eq 1 ]; then
            git worktree remove --force "$TARGET_PATH"
        else
            git worktree remove "$TARGET_PATH"
        fi
        git worktree prune
        if [ "$DELETE_BRANCH" -eq 1 ] && git show-ref --verify --quiet "refs/heads/$BRANCH"; then
            if [ "$FORCE" -eq 1 ]; then
                git branch -D "$BRANCH"
            else
                git branch -d "$BRANCH"
            fi
        fi
        echo "[✓] Worktree removed and pruned successfully."
        ;;

    finish)
        if [ -z "$BRANCH" ]; then
            echo "[-] Error: Usage: ./scripts/worktree.sh finish <source-branch> [target-branch]" >&2
            exit 1
        fi
        SOURCE="$BRANCH"
        TARGET="${BASE:-main}"
        cd "$REPO_ROOT"
        echo "[+] Merging branch '$SOURCE' into target '$TARGET'..."
        git checkout "$TARGET"
        git merge --no-ff "$SOURCE" -m "feat(worktree): merge $SOURCE into $TARGET"
        FOLDER_NAME="$(sanitize_branch "$SOURCE")"
        WT_PATH="$WORKTREES_DIR/$FOLDER_NAME"
        if [ -d "$WT_PATH" ]; then
            echo "[+] Removing merged worktree at $WT_PATH..."
            if [ "$FORCE" -eq 1 ]; then
                git worktree remove --force "$WT_PATH"
            else
                git worktree remove "$WT_PATH"
            fi
        fi
        git worktree prune
        if git show-ref --verify --quiet "refs/heads/$SOURCE"; then
            echo "[+] Deleting merged temporary branch '$SOURCE'..."
            git branch -d "$SOURCE"
        fi
        echo "[✓] Finished '$SOURCE': merged into '$TARGET', worktree removed, and temporary branch deleted."
        ;;

    merge-back)
        if [ -z "$BRANCH" ]; then
            echo "[-] Error: Usage: ./scripts/worktree.sh merge-back <source-branch> [target-branch]" >&2
            exit 1
        fi
        SOURCE="$BRANCH"
        TARGET="${BASE:-main}"
        echo "[+] Merging branch '$SOURCE' into target '$TARGET'..."
        git checkout "$TARGET"
        git merge --no-ff "$SOURCE" -m "feat(worktree): merge $SOURCE into $TARGET"
        echo "[✓] Successfully merged $SOURCE into $TARGET."
        ;;

    sync-remote)
        REMOTE_NAME="${BRANCH:-bambuforge}"
        echo "[+] Fetching from remote '$REMOTE_NAME'..."
        git fetch "$REMOTE_NAME"
        echo "[✓] Remote '$REMOTE_NAME' fetched successfully."
        ;;

    prune)
        git worktree prune
        echo "[✓] Worktree list pruned."
        ;;

    help|*)
        show_usage
        ;;
esac
