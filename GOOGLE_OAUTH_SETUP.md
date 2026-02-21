# 🔐 Google OAuth Setup Guide

## Что добавлено:

✅ **Google OAuth2 аутентификация**
- Endpoint: `GET /auth/google/login` - инициирует вход через Google
- Endpoint: `GET /auth/google/callback` - обрабатывает ответ от Google
- Автоматическая регистрация новых пользователей
- Сохранение `google_id` в профиле

---

## 📋 Настройка Google OAuth (обязательно):

### Шаг 1: Создать проект в Google Cloud Console

1. Откройте https://console.cloud.google.com
2. **Create Project** → название: "RaddScr"
3. Выберите созданный проект

### Шаг 2: Включить Google+ API

1. **APIs & Services** → **Library**
2. Найдите "Google+ API"
3. Нажмите **Enable**

### Шаг 3: Создать OAuth2 Credentials

1. **APIs & Services** → **Credentials**
2. **Create Credentials** → **OAuth client ID**
3. Если нужно, настройте **OAuth consent screen**:
   - User Type: **External**
   - App name: **RaddScr**
   - User support email: ваш email
   - Developer contact: ваш email
   - Scopes: `openid`, `email`, `profile`
   - Save and Continue

4. **Create OAuth client ID:**
   - Application type: **Web application**
   - Name: **RaddScr Web Client**
   - Authorized redirect URIs:
     ```
     https://raddscr-vfxb.onrender.com/auth/google/callback
     http://localhost:8000/auth/google/callback  (для локальной разработки)
     ```
   - **Create**

5. Скопируйте:
   - **Client ID** (начинается с `xxxxx.apps.googleusercontent.com`)
   - **Client Secret**

### Шаг 4: Добавить в Render Environment Variables

1. Откройте https://dashboard.render.com
2. Services → **raddscr** → **Environment**
3. Add Environment Variable:
   ```
   GOOGLE_CLIENT_ID = <ваш Client ID>
   GOOGLE_CLIENT_SECRET = <ваш Client Secret>
   ```
4. **Save Changes** → Render автоматически перезапустит сервис

---

## 🚀 Как это работает:

### 1️⃣ **Frontend инициирует вход:**
```javascript
// Редирект на backend
window.location.href = "https://raddscr-vfxb.onrender.com/auth/google/login";
```

### 2️⃣ **Backend редиректит на Google:**
- Пользователь видит экран выбора Google аккаунта
- Подтверждает доступ к email и профилю

### 3️⃣ **Google возвращает код:**
- Google редиректит на `/auth/google/callback`
- Backend получает токен и данные пользователя

### 4️⃣ **Backend создаёт/находит пользователя:**
- Если email новый → создаётся User с `google_id`
- Если email существует → обновляется `google_id`
- Генерируется JWT токен

### 5️⃣ **Редирект на Frontend:**
```
https://your-frontend.com/auth/callback?token=<JWT_TOKEN>
```

Frontend сохраняет токен и использует для всех запросов.

---

## 🧪 Тестирование:

### 1️⃣ **Без настроенного Google OAuth:**
```bash
curl https://raddscr-vfxb.onrender.com/auth/google/login
# → {"detail":"Google OAuth not configured"}
```

### 2️⃣ **После настройки:**
Откройте в браузере:
```
https://raddscr-vfxb.onrender.com/auth/google/login
```

Должно редиректить на Google для входа.

---

## 📱 Frontend интеграция:

### React/Next.js пример:

```typescript
// components/GoogleLoginButton.tsx
export function GoogleLoginButton() {
  const handleGoogleLogin = () => {
    // Редирект на backend OAuth endpoint
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/google/login`;
  };

  return (
    <button onClick={handleGoogleLogin}>
      Sign in with Google
    </button>
  );
}

// pages/auth/callback.tsx
import { useRouter } from 'next/router';
import { useEffect } from 'react';

export default function AuthCallback() {
  const router = useRouter();
  const { token } = router.query;

  useEffect(() => {
    if (token) {
      // Сохранить токен
      localStorage.setItem('token', token as string);
      
      // Редирект на dashboard
      router.push('/dashboard');
    }
  }, [token, router]);

  return <div>Authenticating...</div>;
}
```

---

## 🔒 Безопасность:

✅ **OAuth2 стандарт** - используется официальный протокол Google
✅ **JWT токены** - выдаются после успешной аутентификации
✅ **HTTPS only** - в продакшене работает только через HTTPS
✅ **Session middleware** - защита от CSRF
✅ **Валидация токенов** - Google токены проверяются на backend

---

## ❓ FAQ:

**Q: Нужно ли хранить пароль для OAuth пользователей?**  
A: Нет! Поле `hashed_password` теперь `nullable`. OAuth пользователи не могут войти через обычный `/auth/login`.

**Q: Что если пользователь уже зарегистрирован с email+password?**  
A: При первом входе через Google добавится `google_id`. Пользователь сможет входить обоими способами.

**Q: Можно ли отвязать Google аккаунт?**  
A: Да, нужно добавить endpoint `DELETE /auth/google/unlink` (пока не реализовано).

**Q: Работает ли без настройки?**  
A: Да! Если `GOOGLE_CLIENT_ID` не установлен, OAuth endpoints вернут 503 (не влияет на остальное API).

---

## 🎯 Следующие шаги:

1. ✅ Настроить Google OAuth credentials (5 минут)
2. ✅ Добавить переменные в Render
3. ⏳ Создать кнопку "Sign in with Google" на фронтенде
4. ⏳ Обработать callback на фронтенде
5. ⏳ Протестировать полный flow

---

**Готово!** 🎉

После настройки пользователи смогут входить через Google одним кликом!
