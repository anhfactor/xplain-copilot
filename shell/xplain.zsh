# xplain shell integration for zsh
# Add this to your ~/.zshrc:
#   source /path/to/xplain/shell/xplain.zsh

# Auto-explain on command failure
# After any command fails, type `wtf` to explain what went wrong
alias wtf='xplain wtf'

# Auto-explain command-not-found errors
command_not_found_handler() {
    echo "zsh: command not found: $1"
    echo ""
    echo "💡 Run 'xplain error \"command not found: $1\"' for help"
    return 127
}

# Quick aliases
alias xc='xplain cmd'
alias xe='xplain error'
alias xd='xplain diff'
alias xw='xplain wtf'
