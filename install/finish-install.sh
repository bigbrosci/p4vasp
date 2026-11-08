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
    local rc_file config_output shell_result='SKIPPED (--deps-only).' configured=0
    rc_file="$HOME/.bashrc"
    # Optional explicit destination for automation; never change HOME for tests.
    if [[ -n "${P4VASP_SHELL_RC:-}" ]]; then
        rc_file="$P4VASP_SHELL_RC"
    fi
    if [[ "${CONFIGURE_SHELL:-1}" -eq 1 ]]; then
        local configure_script
        configure_script="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/configure-shell.py"
        if config_output="$("${PYTHON:-python3}" "$configure_script" "$rc_file" "$alias_definition" 2>&1)"; then
            shell_result='CONFIGURED.'
            configured=1
        else
            printf '%s\n' "$config_output" >&2
            shell_result='NOT CONFIGURED (see the error above).'
        fi
    fi
    echo
    echo '============================================================'
    echo '  p4vasp installation steps completed.'
    printf '  GUI startup check: %s\n' "$gui_result"
    printf '  Command setup: %s\n' "$shell_result"
    echo '============================================================'
    echo
    if [[ "$configured" -eq 1 ]]; then
        echo 'NEXT STEP: Run this command in your terminal:'
        echo '  source ~/.bashrc'
    elif [[ "${CONFIGURE_SHELL:-1}" -eq 1 ]]; then
        echo 'NEXT STEP: Resolve the command-setup error above and rerun the installer.'
    else
        echo 'NEXT STEP: Run bash install.sh to build and configure p4vasp.'
    fi
    echo
    echo '------------------------------------------------------------'
    echo 'Common commands and image export: usage_commands.md'
    echo '------------------------------------------------------------'
    echo '============================================================'
}
