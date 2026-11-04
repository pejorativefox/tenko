# pyenv: initialise shims and completions for bash login shells.
#
# Only users who have started using pyenv (pyenv install creates
# ~/.pyenv, or PYENV_ROOT points at an existing tree) are initialised, so a
# login does not create state in every user's home directory.
#
# Other shells need the equivalent line from pyenv's README in their own
# startup file, for example:  eval "$(pyenv init - zsh)"
if [ -n "${BASH_VERSION:-}" ] && [ -n "${HOME:-}" ] &&
        command -v pyenv >/dev/null 2>&1 &&
        [ -d "${PYENV_ROOT:-$HOME/.pyenv}" ]; then
    eval "$(pyenv init - bash)" || true
fi
