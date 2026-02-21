# 🚀 Deployment Guide

## Deploy Landing Page на Vercel (2 минуты)

### 1. Подготовка

```bash
cd reddit-saas-validator
git init
git add .
git commit -m "Initial commit"
```

### 2. Push на GitHub

```bash
# Создайте репозиторий на GitHub
# Затем:
git remote add origin https://github.com/your-username/reddit-saas-validator.git
git branch -M main
git push -u origin main
```

### 3. Deploy на Vercel

**Вариант A: Через веб-интерфейс**

1. Зайдите на https://vercel.com
2. New Project → Import Git Repository
3. Выберите ваш репозиторий
4. Framework Preset: Other
5. Root Directory: `./` (корень)
6. Deploy!

**Вариант B: Через Vercel CLI**

```bash
npm install -g vercel
vercel login
vercel --prod
```

### 4. Готово!

Ваш landing page будет доступен по адресу:
```
https://reddit-saas-validator.vercel.app
```

---

## 🔧 Настройка Custom Domain (опционально)

1. В Vercel dashboard: Settings → Domains
2. Добавьте ваш домен
3. Настройте DNS записи (Vercel покажет инструкции)

---

## 📦 Структура для Vercel

```
reddit-saas-validator/
├── index.html          # Landing page
├── style.css           # Стили
├── script.js           # JavaScript
├── vercel.json         # Конфигурация (опционально)
└── src/                # Python скрипты (не деплоятся)
```

---

## ⚙️ vercel.json (опционально)

Если нужны редиректы или custom headers:

```json
{
  "rewrites": [
    {
      "source": "/",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ]
}
```

---

## 🎯 Обновления

После изменений:

```bash
git add .
git commit -m "Update landing page"
git push
```

Vercel автоматически задеплоит изменения!

---

## 📊 Analytics

Добавьте Vercel Analytics:

```html
<!-- Вставьте перед </body> в index.html -->
<script src="/_vercel/insights/script.js" defer></script>
```

---

## 💡 Tips

- **Preview Deployments**: Каждая ветка создаёт preview URL
- **Environment Variables**: Для API ключей (но landing page статический)
- **Edge Functions**: Если нужен backend (см. Vercel Serverless Functions)

---

**Вопросы?** Смотрите: https://vercel.com/docs
