#!/usr/bin/env python
"""
Script para ejecutar tests de SlangSpot Latino.
Facilita la ejecución de diferentes tipos de tests.
"""
import os
import sys
import subprocess
import argparse


def run_command(command, description):
    """Ejecuta un comando y muestra el resultado."""
    print(f"\n🔍 {description}")
    print("=" * 50)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)

        if result.returncode == 0:
            print(f"✅ {description} - PASÓ")
            return True
        else:
            print(f"❌ {description} - FALLÓ")
            return False

    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Ejecutar tests de SlangSpot Latino')
    parser.add_argument(
        'test_type',
        choices=['all', 'unit', 'integration', 'quality', 'security'],
        default='all',
        nargs='?',
        help='Tipo de tests a ejecutar'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verbose'
    )

    args = parser.parse_args()

    # Configurar variables de entorno para tests
    os.environ.setdefault('SECRET_KEY', 'test-secret-key')
    os.environ.setdefault('DEBUG', 'True')
    os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')

    verbosity = '2' if args.verbose else '1'
    results = []

    if args.test_type in ['all', 'unit']:
        # Tests unitarios
        results.append(run_command(
            f'python manage.py test core.tests.test_models --verbosity={verbosity}',
            'Tests de Modelos'
        ))
        results.append(run_command(
            f'python manage.py test core.tests.test_forms --verbosity={verbosity}',
            'Tests de Formularios'
        ))
        results.append(run_command(
            f'python manage.py test core.tests.test_views --verbosity={verbosity}',
            'Tests de Vistas'
        ))

    if args.test_type in ['all', 'integration']:
        # Tests de integración (requieren Chrome WebDriver)
        print("\n⚠️  Los tests de integración requieren Chrome WebDriver instalado")
        print("   Si no está instalado, estos tests serán omitidos")
        results.append(run_command(
            f'python manage.py test core.tests.test_integration --verbosity={verbosity}',
            'Tests de Integración (Selenium)'
        ))

    if args.test_type in ['all', 'quality']:
        # Calidad de código
        results.append(run_command(
            'flake8 core/ slangspot/ --count --select=E9,F63,F7,F82 --show-source --statistics',
            'Análisis de Errores Críticos (Flake8)'
        ))
        results.append(run_command(
            'flake8 core/ slangspot/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics',
            'Análisis de Estilo (Flake8)'
        ))

    if args.test_type in ['all', 'security']:
        # Seguridad
        results.append(run_command(
            'bandit -r core/ slangspot/ -f txt',
            'Análisis de Seguridad (Bandit)'
        ))

    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)

    passed = sum(results)
    total = len(results)

    if total == 0:
        print("❌ No se ejecutaron tests")
        return 1

    print(f"✅ Pasaron: {passed}/{total}")
    print(f"❌ Fallaron: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests fallaron. Revisa los errores arriba.")
        return 1


if __name__ == '__main__':
    sys.exit(main())