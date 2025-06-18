import pandas as pd
from celery import shared_task
from .models import TipoGasto, Transaccion

@shared_task
def procesar_excel_async(ruta_archivo):
    df = pd.read_excel(ruta_archivo, sheet_name='Compras')
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    for _, fila in df.iterrows():
        tipo_gasto_nombre = fila.get('tipo_gasto') or fila.get('tipo_de_gasto') or 'NA'
        tipo_gasto, _ = TipoGasto.objects.get_or_create(nombre=tipo_gasto_nombre)
        transaccion = Transaccion(
            tipo_gasto=tipo_gasto,
            tipo_costo=fila.get('tipo_costo', 'NA'),
            unidad1_1=fila.get('unidad1_1', 'NA'),
            unidad1_2=fila.get('unidad1_2', 'NA'),
            unidad1_3=fila.get('unidad1_3', 'NA'),
            unidad1_4=fila.get('unidad1_4', 'NA'),
            unidad1_5=fila.get('unidad1_5', 'NA'),
            suma_unidad1=fila.get('suma_unidad1', 'NA'),
            unidad2=fila.get('unidad2', 'NA'),
            unidad3=fila.get('unidad3', 'NA'),
            unidad4=fila.get('unidad4', 'NA'),
            unidad5=fila.get('unidad5', 'NA'),
            unidad6=fila.get('unidad6', 'NA'),
            unidad7=fila.get('unidad7', 'NA'),
            unidad8=fila.get('unidad8', 'NA'),
            suma_todas_lasunidades=fila.get('suma_todas_lasunidades', 'NA'),
            tipo=fila.get('tipo', 'compra'),
            mes=fila.get('mes', 'NA'),
            descripcion=fila.get('descripcion', 'NA'),
            cuenta=fila.get('cuenta', 'NA')
        )
        transaccion.save()
    return 'Importación completada correctamente.'
