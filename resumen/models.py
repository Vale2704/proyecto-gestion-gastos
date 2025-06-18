from django.db import models

class UnidadNegocio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class TipoGasto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Transaccion(models.Model):
    tipo_gasto = models.ForeignKey(TipoGasto, on_delete=models.CASCADE)
    tipo_costo = models.CharField(max_length=100, default='NA')
    unidad1_1 = models.CharField(max_length=100, default='NA')
    unidad1_2 = models.CharField(max_length=100, default='NA')
    unidad1_3 = models.CharField(max_length=100, default='NA')
    unidad1_4 = models.CharField(max_length=100, default='NA')
    unidad1_5 = models.CharField(max_length=100, default='NA')
    suma_unidad1 = models.CharField(max_length=100, default='NA')
    unidad2 = models.CharField(max_length=100, default='NA')
    unidad3 = models.CharField(max_length=100, default='NA')
    unidad4 = models.CharField(max_length=100, default='NA')
    unidad5 = models.CharField(max_length=100, default='NA')
    unidad6 = models.CharField(max_length=100, default='NA')
    unidad7 = models.CharField(max_length=100, default='NA')
    unidad8 = models.CharField(max_length=100, default='NA')
    suma_todas_lasunidades = models.CharField(max_length=100, default='NA')
    tipo = models.CharField(max_length=10, choices=[('compra', 'Compra'), ('venta', 'Venta')])
    mes = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    cuenta = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} - {self.mes} - {self.descripcion}"
