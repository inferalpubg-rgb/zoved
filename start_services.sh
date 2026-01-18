#!/bin/bash

# Остановка старых процессов
pkill -9 -f "python3 app.py" 2>/dev/null
pkill -9 -f "python3 bot.py" 2>/dev/null
pkill -9 -f "ngrok" 2>/dev/null

cd /workspaces/zoved/edprog

# Запуск Flask
echo "Запуск Flask на порту 8000..."
/bin/python3 app.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!
sleep 3

# Запуск ngrok и получение URL
echo "Запуск ngrok туннеля..."
ngrok http 8000 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!
sleep 5

# Получение публичного URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*' | head -1)

if [ -z "$NGROK_URL" ]; then
    echo "Ошибка: ngrok не инициализирован. Проверьте интернет-соединение."
    tail /tmp/ngrok.log
    exit 1
fi

echo "✅ Публичный URL: $NGROK_URL"

# Обновляем URL в bot.py
WEBAPP_URL="${NGROK_URL}/auth_start.html"
sed -i "s|WEBAPP_URL = .*|WEBAPP_URL = '$WEBAPP_URL'|" bot.py
echo "✅ Обновлен URL в bot.py: $WEBAPP_URL"

# Запуск бота
echo "Запуск Telegram бота..."
/bin/python3 bot.py > /tmp/bot.log 2>&1 &
BOT_PID=$!
sleep 2

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🚀 ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ И ГОТОВЫ К РАБОТЕ            ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║ Flask:        http://localhost:8000                            ║"
echo "║ ngrok:        $NGROK_URL         ║"
echo "║ Web App URL:  $WEBAPP_URL ║"
echo "║                                                                ║
echo "║ Bot Token:    $(grep BOT_TOKEN config.py | cut -d"'" -f2 | cut -c1-30)...║"
echo "║ Admin ID:     $(grep ADMIN_ID config.py | grep -o '[0-9]*$')                    ║"
echo "║                                                                ║"
echo "║ Процессы:                                                      ║"
echo "║ - Flask (PID: $FLASK_PID)                                     ║"
echo "║ - ngrok (PID: $NGROK_PID)                                     ║"
echo "║ - Bot   (PID: $BOT_PID)                                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Логи:"
echo "- Flask:  tail -f /tmp/flask.log"
echo "- ngrok:  tail -f /tmp/ngrok.log"
echo "- Bot:    tail -f /tmp/bot.log"
echo ""
echo "Нажмите Ctrl+C для остановки всех сервисов"
echo ""

# Ждем Ctrl+C
wait
