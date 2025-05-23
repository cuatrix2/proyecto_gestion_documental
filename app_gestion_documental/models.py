from django.db import models

class Usuario(models.Model):
    DEPARTAMENTOS = [
        ('Ventas', 'Ventas'),
        ('Legal', 'Legal'),
        ('Administrativo', 'Administrativo'),
    ]


    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    contrasena = models.CharField(max_length=128)  # Usar set_password()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    departamento = models.CharField(max_length=20, choices=DEPARTAMENTOS, default='Ventas')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Carpeta(models.Model):

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carpetas')

    def __str__(self):
        return self.nombre


class Documento(models.Model):
 
    nombre_archivo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='media/documentos/')
    tipo_archivo = models.CharField(max_length=50)
    tamano = models.FloatField()
    fecha_subida = models.DateTimeField(auto_now_add=True)
    ruta_archivo = models.TextField()
    texto_extraido = models.TextField(blank=True, null=True)
    estado_ocr = models.CharField(max_length=50, blank=True, null=True)
    carpeta = models.ForeignKey(Carpeta, on_delete=models.CASCADE, related_name='documentos')
    usuario_subidor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='documentos')

    def __str__(self):
        return self.nombre_archivo


class TransferenciaDocumento(models.Model):
  
    fecha_transferencia = models.DateTimeField(auto_now_add=True)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='transferencias')
    departamento_origen = models.CharField(max_length=20, choices=Usuario.DEPARTAMENTOS)
    departamento_destino = models.CharField(max_length=20, choices=Usuario.DEPARTAMENTOS)
    usuario_responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='transferencias_realizadas')

    def __str__(self):
        return f"Transferencia {self.id_transferencia} - Doc {self.documento.id_documento}"


class HistorialChat(models.Model):

    titulo = models.CharField(max_length=200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historiales_chat')
    carpeta = models.ForeignKey(Carpeta, on_delete=models.SET_NULL, null=True, blank=True, related_name='chats')
    documento = models.ForeignKey(Documento, on_delete=models.SET_NULL, null=True, blank=True, related_name='chats')

    def __str__(self):
        return self.titulo


class MensajeChat(models.Model):
   
    contenido = models.TextField()
    rol_mensaje = models.CharField(max_length=50)  
    fecha_envio = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(HistorialChat, on_delete=models.CASCADE, related_name='mensajes')

    def __str__(self):
        return f"Mensaje {self.id_mensaje} en Chat {self.chat.id_chat}"
