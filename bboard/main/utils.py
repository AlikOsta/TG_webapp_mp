import jwt
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from .models import CustomUser


def user_view(request) :
    token = request.GET.get("token")

    try :
        # Декодируем токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        user_name = payload.get('user_name')  # Имя пользователя из ТГ
        telegram_id = payload.get('telegram_id')  # ТГ ID
        tg_name = payload.get('tg_name')  # Ник в ТГ

        # Проверяем, существует ли пользователь с таким telegram_id
        user = CustomUser.objects.filter(telegram_id=telegram_id).first()

        if not user :
            # Создаем нового пользователя
            user = CustomUser.objects.create(
                telegram_id=telegram_id,
                username=user_name,
                tg_name=tg_name,
            )

        # Логиним пользователя
        login(request, user)

        return HttpResponseRedirect(reverse('index'))

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) :
        return render(request, 'main/invalid_signature.html')

    except Exception as e :
        print(f"Unexpected error: {e}")
        return render(request, 'main/invalid_signature.html')
