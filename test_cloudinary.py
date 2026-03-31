import os
import django
import cloudinary
import cloudinary.uploader
from decouple import config

def test_cloudinary_upload():
    print("Iniciando prueba de subida a Cloudinary...")
    
    # Obtener credenciales del .env local
    cloud_name = config('CLOUDINARY_CLOUD_NAME', default='')
    api_key = config('CLOUDINARY_API_KEY', default='')
    api_secret = config('CLOUDINARY_API_SECRET', default='')
    
    print(f"Credenciales cargadas:")
    print(f"- CLOUD_NAME: {cloud_name}")
    print(f"- API_KEY: {'***' if api_key else 'None'}")
    print(f"- API_SECRET: {'***' if api_secret else 'None'}")
    
    # Configurar cloudinary manualmente
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    
    # Crear un archivo de texto simple para probar
    test_filepath = "test_cloudinary_file.txt"
    with open(test_filepath, "w") as f:
        f.write("Archivo de prueba para verificar Cloudinary")
    
    try:
        # Intentamos subir como raw (para simular un archivo genérico/audio)
        print("\nIntentando subir archivo...")
        response = cloudinary.uploader.upload(
            test_filepath, 
            resource_type="raw", 
            folder="test_folder"
        )
        print("¡Éxito! El archivo se subió correctamente.")
        print(f"URL: {response.get('secure_url')}")
        
    except Exception as e:
        print(f"\n¡Error! Falló la subida a Cloudinary: {e}")
    finally:
        if os.path.exists(test_filepath):
            os.remove(test_filepath)

if __name__ == "__main__":
    test_cloudinary_upload()
