import jwt
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from .models import CustomUser


def user_view(request) :
    token = request.GET.get("token")

    try :
        # Декодируем токен JWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        telegram_id = payload.get('telegram_id')
        username = payload.get('user_name')
        tg_name = payload.get('tg_name')

        if not telegram_id or not username :
            return render(request, 'main/invalid_signature.html', {"message" : "Некорректные данные пользователя"})

        # Поиск или создание пользователя
        user, created = CustomUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'username' : username, 'tg_name' : tg_name}
        )

        # Авторизация пользователя
        login(request, user)

        return redirect(reverse('index'))

    except jwt.ExpiredSignatureError :
        return render(request, 'main/invalid_signature.html', {"message" : "Срок действия токена истек"})

    except jwt.InvalidTokenError :
        return render(request, 'main/invalid_signature.html', {"message" : "Неверный токен"})

    except Exception as e :
        # Логируем неожиданную ошибку для отладки
        print(f"Unexpected error: {e}")
        return render(request, 'main/invalid_signature.html', {"message" : "Произошла ошибка, попробуйте снова"})
