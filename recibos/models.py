from django.db import models


class Recibo(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.CharField(max_length=100)
    monto = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.codigo
