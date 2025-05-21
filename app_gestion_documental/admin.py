from django.contrib import admin

from.models import Usuario,Carpeta, Documento, TransferenciaDocumento,HistorialChat,MensajeChat

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Carpeta)
admin.site.register(Documento)
admin.site.register(TransferenciaDocumento)
admin.site.register(HistorialChat)
admin.site.register(MensajeChat)