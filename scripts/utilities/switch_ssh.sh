#!/usr/bin/env bash
# Select a GitHub SSH identity using native WSL/Linux Git and SSH.
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(CDPATH= cd -- "$script_dir/../.." && pwd)
identity=wdrag
remote=origin
port=22
unlock=false
check=false
https=false

usage() {
    cat <<'HELP'
Usage: bash scripts/utilities/switch_ssh.sh [identity] [options]
  identity        Key filename under ~/.ssh (default: wdrag)
  --unlock        Unlock the key interactively into a persistent SSH agent
  --check         Verify repository access without prompting
  --https         Return to HTTPS and remove this repo's SSH override
  --port 22|443   Select normal or alternate GitHub SSH port
  --repo PATH     Target another checkout
  --remote NAME   Target another remote (default: origin)
  --help          Show this help
HELP
}

die() { printf '%s\n' "$*" >&2; exit 1; }

while (($#)); do
    case "$1" in
        --help|-h) usage; exit 0 ;;
        --unlock) unlock=true; shift ;;
        --check) check=true; shift ;;
        --https) https=true; shift ;;
        --port|--repo|--remote)
            (($# >= 2)) || die "Missing value for $1"
            case "$1" in
                --port) port=$2 ;;
                --repo) repo=$2 ;;
                --remote) remote=$2 ;;
            esac
            shift 2 ;;
        -*) die "Unknown option: $1" ;;
        *) identity=$1; shift ;;
    esac
done
[[ "$identity" =~ ^[a-zA-Z0-9_-]+$ ]] || die 'Invalid SSH identity filename.'
[[ "$remote" =~ ^[a-zA-Z0-9_.-]+$ && "$remote" != -* ]] || die 'Invalid remote name.'
[[ "$port" == 22 || "$port" == 443 ]] || die 'Port must be 22 or 443.'
$https && $unlock && die '--unlock cannot be used with --https.'
if ! $https; then
    [[ -z "${GIT_SSH_COMMAND:-}" ]] || die 'Unset GIT_SSH_COMMAND before switching; it overrides local SSH settings.'
    [[ -z "${GIT_SSH_VARIANT:-}" || "$GIT_SSH_VARIANT" == ssh ]] || die 'Unset GIT_SSH_VARIANT before switching.'
fi

url=$(git -C "$repo" remote get-url "$remote")
case "$url" in
    https://github.com/*) project=${url#https://github.com/} ;;
    git@github.com:*|git@github-*:*) project=${url#*:} ;;
    ssh://git@github.com/*) project=${url#ssh://git@github.com/} ;;
    ssh://git@ssh.github.com:443/*) project=${url#ssh://git@ssh.github.com:443/} ;;
    *) die "Expected a GitHub remote; found: $url" ;;
esac
project=${project%.git}
[[ "$project" =~ ^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$ ]] || die 'Invalid GitHub repository path.'

unset_local() {
    local status=0
    git -C "$repo" config --local --unset-all "$1" || status=$?
    [[ "$status" == 0 || "$status" == 5 ]] || return "$status"
}

if $https; then
    git -C "$repo" remote set-url "$remote" "https://github.com/$project.git"
    unset_local core.sshCommand
    unset_local ssh.variant
    printf 'Selected HTTPS for %s.\n' "$remote"
else
    key="$HOME/.ssh/$identity"
    [[ -f "$key" ]] || die "SSH key not found: $key"
    # Login shells launched by tools may not inherit the interactive shell's
    # agent. Prefer an agent that already holds this key, then a live agent.
    fingerprint=''
    if [[ -f "$key.pub" ]]; then
        fingerprint=$(ssh-keygen -lf "$key.pub" | awk '{print $2}')
    fi
    selected_agent=''
    fallback_agent=''
    candidates=("${SSH_AUTH_SOCK:-}" "$HOME/.ssh/git-identity-agent.sock"
        "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/openssh_agent"
        "$HOME"/.ssh/agent/s.*.agent.* /tmp/ssh-*/agent.*)
    for candidate in "${candidates[@]}"; do
        [[ -S "$candidate" && -O "$candidate" ]] || continue
        status=0
        identities=$(SSH_AUTH_SOCK="$candidate" ssh-add -l 2>/dev/null) || status=$?
        [[ "$status" == 0 || "$status" == 1 ]] || continue
        if [[ -n "$fingerprint" && "$identities" == *"$fingerprint"* ]]; then
            selected_agent=$candidate
            break
        fi
        if [[ -z "$fallback_agent" ]]; then fallback_agent=$candidate; fi
    done
    export SSH_AUTH_SOCK="${selected_agent:-${fallback_agent:-$HOME/.ssh/git-identity-agent.sock}}"
    ssh_arguments=(ssh -F none -i "$key" -o IdentitiesOnly=yes
        -o "IdentityAgent=$SSH_AUTH_SOCK" -o ConnectTimeout=10 -p "$port")
    if [[ "$port" == 443 ]]; then ssh_arguments+=(-o HostName=ssh.github.com); fi
    printf -v ssh_command '%q ' "${ssh_arguments[@]}"
    git -C "$repo" config --local core.sshCommand "$ssh_command"
    git -C "$repo" config --local ssh.variant ssh
    git -C "$repo" remote set-url "$remote" "git@github.com:$project.git"
    printf 'Selected native SSH key %s (port %s) for %s.\n' "$key" "$port" "$remote"

    if $unlock; then
        status=0
        ssh-add -l >/dev/null 2>&1 || status=$?
        if [[ "$status" == 2 ]]; then
            if [[ -S "$SSH_AUTH_SOCK" ]]; then rm -- "$SSH_AUTH_SOCK"; fi
            # Explicitly requested persistent agent for subsequent Git commands.
            ssh-agent -a "$SSH_AUTH_SOCK" >/dev/null
        elif [[ "$status" != 0 && "$status" != 1 ]]; then
            die "SSH agent check failed (exit $status)."
        fi
        ssh-add "$key"
    fi
fi

if $check; then
    if $https; then
        git -C "$repo" ls-remote --exit-code "$remote" HEAD
    else
        git -C "$repo" -c "core.sshCommand=$ssh_command -o BatchMode=yes" ls-remote --exit-code "$remote" HEAD ||
            die 'SSH access failed. If the key is locked, run this script with --unlock --check in your WSL terminal.'
    fi
    printf 'Repository access verified.\n'
fi
