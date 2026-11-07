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
    echo
    echo '============================================================'
    echo '  p4vasp installation steps completed.'
    printf '  GUI startup check: %s\n' "$gui_result"
    echo '============================================================'
    echo
    echo 'NEXT STEP: Enable the p4v command in Bash'
    echo 'Copy and run all four lines below in your terminal:'
    echo
    echo "cat >> ~/.bashrc <<'P4VASP_ALIAS'"
    printf '%s\n' "$alias_definition"
    echo 'P4VASP_ALIAS'
    echo 'source ~/.bashrc'
    echo
    echo '------------------------------------------------------------'
    echo 'START p4vasp:'
    echo '  p4v          # Open the application'
    echo '  p4v POSCAR   # Open a structure file'
    echo '------------------------------------------------------------'
    if [[ "$(uname -s)" == Darwin ]]; then
        echo
        echo 'macOS zsh users: run this block INSTEAD of the Bash block:'
        echo
        echo "cat >> ~/.zshrc <<'P4VASP_ALIAS'"
        printf '%s\n' "$alias_definition"
        echo 'P4VASP_ALIAS'
        echo 'source ~/.zshrc'
    fi
    echo '============================================================'
}
