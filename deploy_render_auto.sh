#!/bin/bash

# Автоматический деплой на Render через API
# Требуется: RENDER_API_KEY

set -e

if [ -z "$RENDER_API_KEY" ]; then
    echo "❌ Ошибка: RENDER_API_KEY не установлен"
    echo ""
    echo "Получите ключ:"
    echo "1. Откройте: https://dashboard.render.com/u/settings#api-keys"
    echo "2. Create API Key → скопируйте"
    echo "3. Выполните: export RENDER_API_KEY='rnd_xxxxx'"
    echo ""
    exit 1
fi

echo "🚀 Создание Blueprint на Render..."
echo ""

# Получаем ID репозитория
REPO_URL="https://github.com/AlexSevryuga/RaddScr"

# Создаём Blueprint
curl -X POST "https://api.render.com/v1/blueprints" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"RaddScr\",
    \"repo\": \"$REPO_URL\",
    \"autoDeploy\": true,
    \"branch\": \"main\"
  }" | jq '.'

echo ""
echo "✅ Blueprint создан!"
echo ""
echo "Проверьте статус:"
echo "https://dashboard.render.com"
echo ""
echo "Деплой займёт 5-10 минут..."
