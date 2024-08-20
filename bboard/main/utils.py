import jwt
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from .models import CustomUser


def user_view(request) :
    token = request.GET.get("token")

    try :
        # Декодируем токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        # Получаем данные пользователя из токена
        telegram_id = payload.get('telegram_id')
        username = payload.get('user_name')
        tg_name = payload.get('tg_name')

        if not telegram_id or not username :
            return render(request, 'main/invalid_signature.html')

        user = CustomUser.objects.filter(telegram_id=telegram_id).first()

        if not user :
            # Создаем нового пользователя, если он не существует
            user = CustomUser.objects.create(
                telegram_id=telegram_id,
                username=username,
                tg_name=tg_name,
            )

            user.save()

        # Логиним пользователя и создаем новую сессию
        login(request, user)

        # Перенаправление на главную страницу или другую защищенную страницу
        return redirect(reverse('index'))

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) :
        return render(request, 'main/invalid_signature.html', {"message" : "Неверный или истекший токен"})

    except Exception as e :
        print(f"Unexpected error: {e}")
        return render(request, 'main/invalid_signature.html', {"message" : "Произошла ошибка, попробуйте снова"})
