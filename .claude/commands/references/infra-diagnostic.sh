#!/bin/bash
# InfraLearn — Диагностика AI-инфраструктуры
# Использование: bash infra-diagnostic.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check() {
    if eval "$2" > /dev/null 2>&1; then
        echo -e "  ${GREEN}[OK]${NC} $1"
    else
        echo -e "  ${RED}[--]${NC} $1"
    fi
}

echo ""
echo "========================================="
echo "  InfraLearn — Диагностика сервера"
echo "========================================="
echo ""

echo "--- Система ---"
check "Ubuntu/Debian" "cat /etc/os-release | grep -qi ubuntu"
check "Node.js 22+"  "node -v 2>/dev/null | grep -q 'v2[2-9]'"
check "npm"          "npm -v"
check "Python 3"     "python3 --version"
check "Git"          "git --version"
check "tmux"         "tmux -V"
check "jq"           "jq --version"
check "htop"         "which htop"

echo ""
echo "--- AI-инструменты ---"
check "Claude Code"  "claude --version"
check "Codex CLI"    "which codex"

echo ""
echo "--- Claude Code конфигурация ---"
check "CLAUDE.md (глобальный)"  "test -f ~/.claude/CLAUDE.md"
check "Skills директория"       "test -d ~/.claude/skills && ls ~/.claude/skills/ | head -1"
check "Hooks директория"        "test -d ~/.claude/hooks && ls ~/.claude/hooks/*.sh 2>/dev/null | head -1"
check "settings.local.json"     "test -f ~/.claude/settings.local.json"
check "settings.json"           "test -f ~/.claude/settings.json"
check "statusline.js"           "test -f ~/.claude/statusline.js"

echo ""
echo "--- MCP-серверы ---"
if command -v claude > /dev/null 2>&1; then
    MCP_LIST=$(claude mcp list 2>/dev/null)
    check "memory MCP"     "echo '$MCP_LIST' | grep -qi memory"
    check "filesystem MCP" "echo '$MCP_LIST' | grep -qi filesystem"
    check "github MCP"     "echo '$MCP_LIST' | grep -qi github"
    check "context7 MCP"   "echo '$MCP_LIST' | grep -qi context7"
    check "exa MCP"        "echo '$MCP_LIST' | grep -qi exa"
else
    echo -e "  ${RED}[--]${NC} Claude Code не установлен — MCP не проверить"
fi

echo ""
echo "--- Рабочее окружение ---"
check "/opt/workspace"          "test -d /opt/workspace"
check "Vault"                   "test -d /opt/workspace/vault"
check "InfraLearn репо"         "test -d /opt/workspace/infralearn"

echo ""
echo "--- Безопасность ---"
check "fail2ban"                "systemctl is-active fail2ban"
check "UFW файрвол"             "ufw status 2>/dev/null | grep -q 'Status: active'"
check "Автообновления"          "systemctl is-active unattended-upgrades"

echo ""
echo "========================================="
echo "  Диагностика завершена"
echo "========================================="
echo ""
