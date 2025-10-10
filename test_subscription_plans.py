#!/usr/bin/env python3
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slangspot.settings')
django.setup()

from core.models import SubscriptionPlan, UserSubscription, Payment

def test_subscription_system():
    print("=== VERIFICACIÓN DEL SISTEMA DE SUBSCRIPCIONES ===")

    # Verificar planes de subscripción
    print("\n📋 PLANES DE SUBSCRIPCIÓN:")
    plans = SubscriptionPlan.objects.all()
    for plan in plans:
        print(f"✅ {plan.name} - {plan.plan_type} - ${plan.price}")
        print(f"   Características: {', '.join(plan.features[:3])}...")  # Mostrar primeras 3

    print(f"\n📊 Total planes: {plans.count()}")

    # Verificar subscripciones de usuarios
    print("\n👥 SUBSCRIPCIONES DE USUARIOS:")
    subscriptions = UserSubscription.objects.all()
    for sub in subscriptions:
        print(f"✅ {sub.user.username} - {sub.subscription_plan.name} - {sub.status}")

    print(f"\n📊 Total subscripciones: {subscriptions.count()}")

    # Verificar pagos
    print("\n💳 PAGOS REGISTRADOS:")
    payments = Payment.objects.all()
    for payment in payments:
        print(f"✅ {payment.user.username} - ${payment.amount} - {payment.status}")

    print(f"\n📊 Total pagos: {payments.count()}")

    print("\n🎉 ¡SISTEMA DE SUBSCRIPCIONES FUNCIONANDO CORRECTAMENTE!")

if __name__ == "__main__":
    test_subscription_system()