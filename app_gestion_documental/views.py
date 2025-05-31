from django.shortcuts import render 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser 
import PyPDF2
import docx
import io
import uuid
import os


try:
    from .db_configuration import client_supabase
except ImportError:
 
    from db_configuration import client_supabase


class TextExtractionView(APIView):
    parser_classes = (MultiPartParser, FormParser) 

    def post(self, request):
        if not client_supabase:
            return Response(
                {"error": "Configuración del cliente Supabase incompleta o fallida en el servidor (desde db_configuration)."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        id_organization = request.data.get('id_organization')
        if not id_organization:
            return Response(
                {"error": "El parámetro 'id_organization' es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        bucket_name = request.data.get('bucket_name')
        if not bucket_name:
            return Response(
                {"error": "El parámetro 'bucket_name' es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        archivo = request.FILES.get('file')
        if not archivo:
            return Response({"error": "No se envió ningún archivo ('file')."}, status=status.HTTP_400_BAD_REQUEST)

        file_size_bytes = archivo.size
        file_size_gb = file_size_bytes / (1024 * 1024 * 1024)

        try:
            response_table = client_supabase.table("storage_organization").select("storage_used, available_storage").eq("organization", id_organization).maybe_single().execute()
        except Exception as e:
            return Response({
                "message": "Error al consultar el almacenamiento de la organización.",
                "error_details": str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if response_table.data is None:
            return Response({
                "message": "No se encontró información de almacenamiento para la organización.",
                "error_details": "Verifique el id_organization proporcionado.",
                "id_organization": id_organization,
            }, status=status.HTTP_404_NOT_FOUND)

        storage_data = response_table.data
        new_storage_used = storage_data["storage_used"] + file_size_gb

        if new_storage_used > storage_data["available_storage"]:
            return Response({
                "message": "Espacio de almacenamiento insuficiente. El archivo no ha sido subido.",
                "id_organization": id_organization,
                "file_size_gb": f"{file_size_gb:.6f}",
                "storage_used_gb": f"{storage_data['storage_used']:.6f}",
                "available_storage_gb": f"{storage_data['available_storage']:.6f}",
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

   
        try:
            client_supabase.storage.get_bucket(bucket_name)
        except Exception as e:

            try:
                client_supabase.storage.create_bucket(
                    bucket_name,
                    options={"public": True} 
                )
            except Exception as creation_error:
               
                if "already exists" in str(creation_error).lower() or \
                   (hasattr(creation_error, 'status_code') and creation_error.status_code == 409) or \
                   (hasattr(creation_error, 'args') and len(creation_error.args) > 0 and isinstance(creation_error.args[0], dict) and creation_error.args[0].get("error") == "Duplicate bucket"):
                    pass 
                else:
                    return Response(
                        {"error": f"Error creando/accediendo al bucket '{bucket_name}': {str(creation_error)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        
        original_filename = archivo.name
        file_extension = original_filename.split('.')[-1].lower() if '.' in original_filename else ''
        supabase_filename = f"{uuid.uuid4()}.{file_extension}"

        try:
            archivo.seek(0)
            file_bytes = archivo.read()
        except Exception as e:
            return Response({"error": f"Error al leer el contenido del archivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        public_url = ""
        try:
            upload_response = client_supabase.storage.from_(bucket_name).upload(
                path=supabase_filename,
                file=file_bytes,
                file_options={"content-type": archivo.content_type or 'application/octet-stream'}
            )
            public_url = client_supabase.storage.from_(bucket_name).get_public_url(supabase_filename)

       
            client_supabase.table("storage_organization").update({"storage_used": new_storage_used}).eq("organization", id_organization).execute()

        except Exception as e:
           
            return Response(
                {"error": f"Error al subir el archivo al bucket '{bucket_name}' o actualizar almacenamiento: {str(e)}",
                 "id_organization": id_organization,
                 "bucket_name": bucket_name
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        texto_extraido = ""
        extraction_message = "Extracción de texto no aplicable para este tipo de archivo o no solicitada."
        status_code = status.HTTP_200_OK 

        extractable_extensions = ['pdf', 'docx', 'txt', 'csv']
        if file_extension in extractable_extensions:
            try:
                if file_extension == 'pdf':
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                    for page_obj in pdf_reader.pages:
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
                
                return Response({
                    "message": f"Archivo subido y {extraction_message.lower()}",
                    "supabase_filename": supabase_filename, 
                    "public_url": public_url,
                    "bucket_name": bucket_name,
                    "id_organization": id_organization,
                    "file_size_gb": f"{file_size_gb:.6f}",
                    "texto": texto_extraido
                }, status=status.HTTP_200_OK)

            except Exception as e:
           
                status_code = status.HTTP_207_MULTI_STATUS
                extraction_message = f"Archivo subido con éxito, pero ocurrió un error durante la extracción del texto: {str(e)}"
              
                return Response({
                    "message": extraction_message,
                    "supabase_filename": supabase_filename,
                    "public_url": public_url,
                    "bucket_name": bucket_name,
                    "id_organization": id_organization,
                    "file_size_gb": f"{file_size_gb:.6f}",
                    "texto": ""
                }, status=status_code)
        else:
            # File uploaded, but not an extractable type
            return Response({
                "message": f"Archivo subido con éxito al bucket '{bucket_name}'. Tipo de archivo '.{file_extension}' no es soportado para extracción de texto.",
                "supabase_filename": supabase_filename,
                "public_url": public_url,
                "bucket_name": bucket_name,
                "id_organization": id_organization,
                "file_size_gb": f"{file_size_gb:.6f}",
                "texto": ""
            }, status=status.HTTP_200_OK)


    def delete(self, request):
        if not client_supabase:
            return Response(
                {"error": "Configuración del cliente Supabase incompleta o fallida en el servidor."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        id_organization = request.data.get('id_organization')
        bucket_name = request.data.get('bucket_name')
        file_name_to_delete = request.data.get('file_name') 

        if not all([id_organization, bucket_name, file_name_to_delete]):
            missing_params = []
            if not id_organization: missing_params.append("'id_organization'")
            if not bucket_name: missing_params.append("'bucket_name'")
            if not file_name_to_delete: missing_params.append("'file_name'")
            return Response(
                {"error": f"Los siguientes parámetros son requeridos: {', '.join(missing_params)}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_size_gb_to_delete = 0
        target_file_meta = None

        try:
         
            dir_path = os.path.dirname(file_name_to_delete)
            simple_file_name = os.path.basename(file_name_to_delete)

            files_in_dir = client_supabase.storage.from_(bucket_name).list(path=dir_path or None)

            if files_in_dir:
                for f_meta in files_in_dir:
                    if f_meta['name'] == simple_file_name:
                        target_file_meta = f_meta
                        break
            
            if not target_file_meta:

                pass


            if not target_file_meta or not target_file_meta.get('metadata'):
                return Response(
                    {"error": f"Archivo '{file_name_to_delete}' no encontrado en el bucket '{bucket_name}' (o en la ruta especificada) o no se pudo obtener metadatos."},
                    status=status.HTTP_404_NOT_FOUND
                )

            file_size_bytes_to_delete = target_file_meta['metadata'].get('size', 0)
            if file_size_bytes_to_delete == 0:
                print(f"Advertencia: El archivo '{file_name_to_delete}' tiene un tamaño de 0 bytes según los metadatos o el tamaño no está disponible.")
            file_size_gb_to_delete = file_size_bytes_to_delete / (1024 * 1024 * 1024)

        except Exception as e:
          
            return Response(
                {"error": f"Error al obtener metadatos del archivo '{file_name_to_delete}': {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

       
        try:
         
            remove_path = [file_name_to_delete]
            client_supabase.storage.from_(bucket_name).remove(remove_path)
        except Exception as e:
            return Response(
                {"error": f"Error al eliminar el archivo '{file_name_to_delete}' de Supabase Storage: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

      
        try:
            org_storage_response = client_supabase.table("storage_organization").select("storage_used").eq("organization", id_organization).maybe_single().execute()

            if org_storage_response.data is None:
                return Response(
                    {"error": f"No se encontró información de almacenamiento para la organización '{id_organization}'. El archivo fue eliminado del bucket pero el uso no pudo ser actualizado.",
                     "file_deleted": True,
                     "file_name": file_name_to_delete,
                     "bucket_name": bucket_name
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            current_storage_used_gb = org_storage_response.data["storage_used"]
            new_storage_used_gb = current_storage_used_gb - file_size_gb_to_delete
            new_storage_used_gb = max(0, new_storage_used_gb) 

            client_supabase.table("storage_organization").update({"storage_used": new_storage_used_gb}).eq("organization", id_organization).execute()

        except Exception as e:
            return Response(
                {"error": f"Archivo '{file_name_to_delete}' eliminado del bucket, pero ocurrió un error al actualizar el uso de almacenamiento para la organización '{id_organization}': {str(e)}",
                 "file_deleted": True,
                 "file_name": file_name_to_delete,
                 "bucket_name": bucket_name
                },
                status=status.HTTP_207_MULTI_STATUS
            )

        return Response({
            "message": f"Archivo '{file_name_to_delete}' eliminado con éxito del bucket '{bucket_name}' y almacenamiento actualizado.",
            "id_organization": id_organization,
            "file_size_freed_gb": f"{file_size_gb_to_delete:.6f}",
            "storage_used_updated_to_gb": f"{new_storage_used_gb:.6f}"
            
        }, status=status.HTTP_200_OK)
