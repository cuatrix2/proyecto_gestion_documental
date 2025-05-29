from django.shortcuts import render  # No se utiliza en esta APIView, se puede eliminar si no se usa en otra parte
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
import PyPDF2
import docx
import io
import uuid
import os  
# Mantener 'os' si se usa para otros propósitos; de lo contrario, principalmente se usa en db_configuration ahora

# Asegúrate de que sea supabase-py v2 o superior para obtener la URL pública directamente con get_public_url
# La importación de 'supabase' ahora está principalmente manejada por db_configuration.py,
# pero si usas directamente 'Client' o 'create_client' en este archivo, consérvalo.
# from supabase import Client  # Ya no es necesario aquí si client_supabase es la única interacción

try:
    from .db_configuration import client_supabase
except ImportError:
    # Alternativa en caso de que el script se ejecute directamente o '.' no sea apropiado
    from db_configuration import client_supabase


class TextExtractionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        if not client_supabase:
            return Response(
                {"error": "Configuración del cliente Supabase incompleta o fallida en el servidor (desde db_configuration)."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Obtener id_organization del cuerpo de la solicitud (campo de formulario)
        id_organization = request.data.get('id_organization')
        if not id_organization:
            return Response(
                {"error": "El parámetro 'id_organization' es requerido en el cuerpo de la solicitud."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener bucket_name del cuerpo de la solicitud (campo de formulario)
        bucket_name = request.data.get('bucket_name')
        if not bucket_name:
            return Response(
                {"error": "El parámetro 'bucket_name' es requerido en el cuerpo de la solicitud."},
                status=status.HTTP_400_BAD_REQUEST
            )

        archivo = request.FILES.get('file')
        if not archivo:
            return Response({"error": "No se envió ningún archivo ('file')"}, status=status.HTTP_400_BAD_REQUEST)

        # Calcular el tamaño del archivo en GB
        file_size_bytes = archivo.size
        # 1 GB = 1024 * 1024 * 1024 bytes
        file_size_gb = file_size_bytes / (1024 * 1024 * 1024)

        response_table = client_supabase.table("storage_organization").select("*").eq("organization", id_organization).execute()

        # Agregar una verificación para datos vacíos o errores desde la consulta a Supabase
        if not response_table.data:
            error_message = "No se encontró información de almacenamiento para la organización."
            if hasattr(response_table, 'error') and response_table.error:
                error_message += f" Error de Supabase: {response_table.error.message}"
            return Response({
                "message": error_message,
                "error_details": "Verifique el id_organization proporcionado.",
                "public_url": "",
                "bucket_name": bucket_name,
                "id_organization": id_organization,
                "file_size_gb": f"{file_size_gb:.6f}",
                "texto": ""
            }, status=status.HTTP_404_NOT_FOUND)

        data = response_table.data[0]
        new_value = data["storage_used"] + file_size_gb
        if new_value > data["available_storage"]:
            return Response({
                "message": f"Ya no te queda espacio disponible, el archivo no ha sido subido.",
                "error_details": f"Error al procesar el contenido del archivo: Espacio insuficiente.",
                "public_url": "",
                "bucket_name": bucket_name,
                "id_organization": id_organization,
                "file_size_gb": f"{file_size_gb:.6f}",
                "texto": ""
            }, status=status.HTTP_402_PAYMENT_REQUIRED)  # O HTTP_207_MULTI_STATUS si prefieres el código original
        else:
            client_supabase.table("storage_organization").update({"storage_used": new_value}).eq("organization", id_organization).execute()

        # Asegurarse de que el bucket de Supabase existe, si no, crearlo
        try:
            client_supabase.storage.get_bucket(bucket_name)
        except Exception as e:
            try:
                client_supabase.storage.create_bucket(
                    bucket_name,
                    options={
                        "public": True,  # Considerar si siempre debe ser público o configurable
                        "allowed_mime_types": ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain", "text/csv"],  # Más general
                        "file_size_limit": 10 * 1024 * 1024,  # 10MB, considerar si es adecuado o debe ser mayor
                    }
                )
            except Exception as creation_error:
                # Verificación más robusta para errores en supabase-py v2
                if "already exists" in str(creation_error).lower() or \
                   (hasattr(creation_error, 'status_code') and creation_error.status_code == 409) or \
                   (hasattr(creation_error, 'args') and len(creation_error.args) > 0 and isinstance(creation_error.args[0], dict) and creation_error.args[0].get("error") == "Duplicate bucket"):
                    pass  # Está bien si ya existe
                else:
                    return Response(
                        {"error": f"Error de configuración del almacenamiento para el bucket '{bucket_name}': {str(creation_error)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

        original_filename = archivo.name
        file_extension = original_filename.split('.')[-1].lower() if '.' in original_filename else ''

        try:
            # Volver al inicio del archivo antes de leer, por si el cursor se ha movido
            archivo.seek(0)
            file_bytes = archivo.read()
        except Exception as e:
            return Response({"error": f"Error al leer el contenido del archivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        supabase_filename = f"{uuid.uuid4()}.{file_extension}"

        public_url = ""

        try:
            client_supabase.storage.from_(bucket_name).upload(
                path=supabase_filename,
                file=file_bytes,  # Usar los bytes cargados en memoria
                file_options={"content-type": archivo.content_type or 'application/octet-stream'}
            )

            public_url = client_supabase.storage.from_(bucket_name).get_public_url(supabase_filename)

        except Exception as e:
            return Response(
                {"error": f"Error al subir el archivo al bucket '{bucket_name}' o al obtener la URL: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        texto_extraido = ""
        extraction_message = ""

        try:
            if file_extension == 'pdf':
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                for page_num in range(len(pdf_reader.pages)):
                    page_obj = pdf_reader.pages[page_num]
                    texto_extraido += (page_obj.extract_text() or "")
                extraction_message = "Texto extraído del PDF con éxito."
            elif file_extension == 'docx':
                document = docx.Document(io.BytesIO(file_bytes))
                for para in document.paragraphs:
                    texto_extraido += para.text + "\n"
                extraction_message = "Texto extraído del documento Word con éxito."
            elif file_extension in ['txt', 'csv']:
                try:
                    texto_extraido = file_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    texto_extraido = file_bytes.decode('latin-1', errors='replace')
                extraction_message = "Contenido del archivo de texto extraído con éxito."
            else:
                return Response({
                    "message": f"Archivo subido con éxito al bucket '{bucket_name}'. Tipo de archivo '.{file_extension}' no es soportado para extracción de texto.",
                    "public_url": public_url,
                    "bucket_name": bucket_name,
                    "id_organization": id_organization,
                    "file_size_gb": f"{file_size_gb:.6f}",
                    "texto": ""
                }, status=status.HTTP_200_OK)

            return Response({
                "message": f"Archivo subido al bucket '{bucket_name}' y {extraction_message.lower()}",
                "texto": texto_extraido,
                "public_url": public_url,
                "bucket_name": bucket_name,
                "id_organization": id_organization,
                "file_size_gb": f"{file_size_gb:.6f}"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": f"Archivo subido con éxito al bucket '{bucket_name}', pero ocurrió un error durante la extracción del texto.",
                "error_details": f"Error al procesar el contenido del archivo: {str(e)}",
                "public_url": public_url,
                "bucket_name": bucket_name,
                "id_organization": id_organization,
                "file_size_gb": f"{file_size_gb:.6f}",
                "texto": ""
            }, status=status.HTTP_207_MULTI_STATUS)
