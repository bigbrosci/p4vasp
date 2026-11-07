#!/usr/bin/env bash
# Shared by Unix installers; ROOT and APP_ARGS are provided by the backend.
finish_install() {
    local gui_result='SKIPPED (not requested; GUI not verified).'
    if [[ "$LAUNCH" -eq 1 ]]; then
        if [[ "$(uname -s)" != Darwin && -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
            gui_result='SKIPPED (no graphical display; GUI not verified).'
        else
            echo 'Launching p4vasp; the GUI will close automatically after about 2 seconds...'
            if [[ "${APP_ARGS+x}" ]] && ((${#APP_ARGS[@]})); then
                P4VASP_INSTALL_PREVIEW=1 bash "$ROOT/p4v.sh" "${APP_ARGS[@]}" || return $?
            else
                P4VASP_INSTALL_PREVIEW=1 bash "$ROOT/p4v.sh" || return $?
            fi
            gui_result='PASSED (GUI displayed and closed successfully).'
        fi
    fi
    local launch_command alias_definition
    printf -v launch_command 'bash %q' "$ROOT/p4v.sh"
    # Quote the alias value as literal shell text, including unusual path names.
    alias_definition="${launch_command//\'/\'\\\'\'}"
    alias_definition="alias p4v='$alias_definition'"
    local rc_file rc_display shell_kind='Bash' shell_result='SKIPPED (--deps-only).' configured=0
    rc_file="$HOME/.bashrc"
    rc_display='~/.bashrc'
    if [[ "${P4VASP_CALLER_SHELL:-}" != bash && ( "${SHELL:-}" == */zsh || "${SHELL:-}" == zsh ) ]]; then
        shell_kind='zsh'
        rc_file="${ZDOTDIR:-$HOME}/.zshrc"
        if [[ -z "${ZDOTDIR:-}" ]]; then rc_display='~/.zshrc'; else printf -v rc_display '%q' "$rc_file"; fi
    fi
    # Optional explicit destination for automation; never change HOME for tests.
    if [[ -n "${P4VASP_SHELL_RC:-}" ]]; then
        rc_file="$P4VASP_SHELL_RC"
        printf -v rc_display '%q' "$rc_file"
    fi
    if [[ "${CONFIGURE_SHELL:-1}" -eq 1 ]]; then
        local configure_script
        configure_script="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/configure-shell.py"
        if "${PYTHON:-python3}" "$configure_script" "$rc_file" "$alias_definition"; then
            shell_result="CONFIGURED ($rc_file)."
            configured=1
        else
            shell_result='NOT CONFIGURED (see the error above).'
        fi
    fi
    if [[ "$configured" -eq 1 && -n "${P4VASP_RELOAD_RECEIPT:-}" ]]; then
        printf '%s\0' "$rc_file" > "$P4VASP_RELOAD_RECEIPT" || return $?
    fi
    echo
    echo '============================================================'
    echo '  p4vasp installation steps completed.'
    printf '  GUI startup check: %s\n' "$gui_result"
    printf '  Shell alias: %s\n' "$shell_result"
    echo '============================================================'
    echo
    if [[ "$configured" -eq 1 ]]; then
        if [[ -n "${P4VASP_RELOAD_RECEIPT:-}" ]]; then
            echo 'NEXT STEP: The calling Bash terminal will reload automatically.'
        else
            printf 'NEXT STEP: Reload this %s terminal (or open a new one)\n' "$shell_kind"
            echo
            printf 'source %s\n' "$rc_display"
            echo 'Tip for Bash: use source install.sh next time to reload automatically.'
        fi
    elif [[ "${CONFIGURE_SHELL:-1}" -eq 1 ]]; then
        echo 'NEXT STEP: Resolve the shell-config error, then run:'
        echo
        printf "cat >> %s <<'P4VASP_ALIAS'\n" "$rc_display"
        printf '%s\n' "$alias_definition"
        echo 'P4VASP_ALIAS'
        printf 'source %s\n' "$rc_display"
    else
        echo 'NEXT STEP: Run bash install.sh to build and configure p4vasp.'
    fi
    echo
    echo '------------------------------------------------------------'
    echo 'START p4vasp:'
    echo '  p4v          # Open the application'
    echo '  p4v POSCAR   # Open a structure file'
    echo '------------------------------------------------------------'
    echo '============================================================'
}
