#!/usr/bin/env bash
# Shared by Unix installers; ROOT and APP_ARGS are provided by the backend.
finish_install() {
    if [[ "$LAUNCH" -eq 1 ]]; then
        if [[ "$(uname -s)" != Darwin && -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
            echo '未检测到图形显示环境，已跳过界面预览；GUI 尚未验证。'
        else
            echo '正在启动 p4vasp，界面显示约 2 秒后自动关闭……'
            if [[ "${APP_ARGS+x}" ]] && ((${#APP_ARGS[@]})); then
                P4VASP_INSTALL_PREVIEW=1 bash "$ROOT/p4v.sh" "${APP_ARGS[@]}" || return $?
            else
                P4VASP_INSTALL_PREVIEW=1 bash "$ROOT/p4v.sh" || return $?
            fi
            echo 'p4vasp 已顺利完成安装，界面启动检查通过。'
        fi
    fi
    echo '安装步骤已完成。日常启动请设置以下别名：'
    echo '将下面这一行添加到 ~/.bashrc 文件中：'
    local launch_command alias_definition
    printf -v launch_command 'bash %q' "$ROOT/p4v.sh"
    # Quote the alias value as literal shell text, including unusual path names.
    alias_definition="${launch_command//\'/\'\\\'\'}"
    alias_definition="alias p4v='$alias_definition'"
    printf '%s\n' "$alias_definition"
    echo '保存后执行：source ~/.bashrc'
    echo '以后输入 p4v 即可打开；也可执行 p4v POSCAR。'
    if [[ "$(uname -s)" == Darwin ]]; then
        echo '若使用 macOS 默认 zsh，请改为写入 ~/.zshrc，并执行 source ~/.zshrc。'
    fi
}
