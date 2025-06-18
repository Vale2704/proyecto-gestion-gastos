from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse, JsonResponse
from .models import TipoGasto, UnidadNegocio, Transaccion
import pandas as pd
from datetime import datetime
import os
from collections import defaultdict
import io
import matplotlib.pyplot as plt
import numpy as np
import json
import xlsxwriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_GET
import tempfile

# Vista de inicio
# def inicio(request):
#     return render(request, 'resumen/inicio.html')

# Procesar Excel y guardar datos en la sesión y la base de datos
def procesar_excel(archivo, session):
    from .models import Transaccion, TipoGasto
    # Limpiar la base de datos antes de importar
    Transaccion.objects.all().delete()
    resumen_rows = []
    xls = pd.ExcelFile(archivo)
    hojas = xls.sheet_names
    for hoja, tipo in [('Compras', 'compra'), ('Ventas', 'venta')]:
        if hoja in hojas:
            df = pd.read_excel(xls, sheet_name=hoja)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            columnas_unidades = [
                'unidad1.1', 'unidad1.2', 'unidad1.3', 'unidad1.4', 'unidad1.5', 'suma_unidad1',
                'unidad2', 'unidad3', 'unidad4', 'unidad5', 'unidad6', 'unidad7', 'unidad8', 'suma_todas_lasunidades'
            ]
            columnas_meses = [col for col in df.columns if any(m in col for m in ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']) or "'24" in col or "'25" in col]
            for idx, row in df.iterrows():
                cuenta = row.get('cuenta_de_costos', '')
                descripcion = row.get('nombre_del_artículo', '')
                tipo_gasto_nombre = row.get('tipo_costo', '') or 'Sin Clasificar'
                tipo_gasto_obj, _ = TipoGasto.objects.get_or_create(nombre=tipo_gasto_nombre)
                for mes in columnas_meses:
                    valor_mes = row.get(mes, np.nan)
                    if pd.notnull(valor_mes) and valor_mes != 0:
                        trans = Transaccion(
                            cuenta=cuenta,
                            descripcion=descripcion,
                            tipo=tipo,
                            tipo_gasto=tipo_gasto_obj,
                            mes=mes,
                            total=valor_mes,
                            unidad1_1=row.get('unidad1.1', ''),
                            unidad1_2=row.get('unidad1.2', ''),
                            unidad1_3=row.get('unidad1.3', ''),
                            unidad1_4=row.get('unidad1.4', ''),
                            unidad1_5=row.get('unidad1.5', ''),
                            suma_unidad1=row.get('suma_unidad1', ''),
                            unidad2=row.get('unidad2', ''),
                            unidad3=row.get('unidad3', ''),
                            unidad4=row.get('unidad4', ''),
                            unidad5=row.get('unidad5', ''),
                            unidad6=row.get('unidad6', ''),
                            unidad7=row.get('unidad7', ''),
                            unidad8=row.get('unidad8', ''),
                            suma_todas_lasunidades=row.get('suma_todas_lasunidades', '')
                        )
                        trans.save()
                        resumen_rows.append({
                            'cuenta': cuenta,
                            'descripcion': descripcion,
                            'tipo': tipo,
                            'tipo_gasto': tipo_gasto_nombre,
                            'mes': mes,
                            'total': valor_mes
                        })
    session['resumen_rows'] = resumen_rows
    session['excel_error'] = ''
    session.modified = True

# Vista para subir Excel y mostrar clasificación automáticamente
def subir_excel(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        try:
            procesar_excel(archivo, request.session)
            messages.success(request, 'Archivo procesado correctamente.')
            return redirect('clasificacion')
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {str(e)}')
    excel_error = request.session.get('excel_error', '')
    return render(request, 'resumen/subir_excel.html', {'excel_error': excel_error})

# Vista de clasificación de gastos
def clasificacion(request):
    from .models import Transaccion
    tipo = request.GET.get('tipo', 'compra')
    transacciones = Transaccion.objects.filter(tipo=tipo)
    filas = []
    for t in transacciones:
        unidades = [
            ('unidad1_1', t.unidad1_1),
            ('unidad1_2', t.unidad1_2),
            ('unidad1_3', t.unidad1_3),
            ('unidad1_4', t.unidad1_4),
            ('unidad1_5', t.unidad1_5),
            ('unidad2', t.unidad2),
            ('unidad3', t.unidad3),
            ('unidad4', t.unidad4),
            ('unidad5', t.unidad5),
            ('unidad6', t.unidad6),
            ('unidad7', t.unidad7),
            ('unidad8', t.unidad8)
        ]
        for nombre_unidad, valor_unidad in unidades:
            if valor_unidad and valor_unidad != 'NA':
                filas.append({
                    'tipo_gasto': t.tipo_gasto.nombre,
                    'mes': t.mes,
                    'unidad': nombre_unidad,
                    'valor': valor_unidad,
                    'tipo': t.tipo,
                    'descripcion': t.descripcion,
                    'cuenta': t.cuenta
                })
    return render(request, 'resumen/clasificacion.html', {'filas': filas, 'tipo': tipo})

# Vista para generar y descargar el reporte Excel
def generar_reporte(request):
    gastos = Gasto.objects.all().select_related('unidad', 'tipo_gasto')
    data = []
    for gasto in gastos:
        data.append({
            'Unidad': gasto.unidad.nombre,
            'Tipo de Gasto': gasto.tipo_gasto.nombre,
            'Mes': gasto.mes.strftime('%Y-%m'),
            'Monto': float(gasto.monto)
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not df.empty:
            totales_unidad = {}
            for unidad, df_unidad in df.groupby('Unidad'):
                workbook = writer.book
                worksheet = workbook.add_worksheet(unidad[:31])
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                total_format = workbook.add_format({
                    'bold': True,
                    'fg_color': '#FFC7CE',
                    'border': 1
                })
                percent_format = workbook.add_format({
                    'num_format': '0.00%',
                    'border': 1
                })
                money_format = workbook.add_format({
                    'num_format': '$#,##0.00',
                    'border': 1
                })
                resumen = df_unidad.pivot_table(
                    index=['Mes', 'Tipo de Gasto'],
                    values='Monto',
                    aggfunc='sum'
                ).reset_index()
                total_mes = df_unidad.groupby('Mes')['Monto'].sum().reset_index()
                total_mes['Tipo de Gasto'] = 'TOTAL MES'
                resumen_final = pd.concat([resumen, total_mes], ignore_index=True)
                resumen_final['% del Mes'] = resumen_final.apply(
                    lambda row: (row['Monto'] / total_mes[total_mes['Mes'] == row['Mes']]['Monto'].values[0])
                    if row['Tipo de Gasto'] != 'TOTAL MES' else 1, axis=1
                )
                headers = ['Mes', 'Tipo de Gasto', 'Monto', '% del Mes']
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)
                for row_idx, row in enumerate(resumen_final.itertuples(), start=1):
                    worksheet.write(row_idx, 0, row.Mes)
                    worksheet.write(row_idx, 1, row.Tipo_de_Gasto)
                    worksheet.write(row_idx, 2, row.Monto, money_format)
                    worksheet.write(row_idx, 3, row._4, percent_format)
                    if row.Tipo_de_Gasto == 'TOTAL MES':
                        worksheet.set_row(row_idx, None, total_format)
                worksheet.set_column('A:A', 15)
                worksheet.set_column('B:B', 25)
                worksheet.set_column('C:C', 15)
                worksheet.set_column('D:D', 15)
                plt.figure(figsize=(10, 6))
                pivot_data = df_unidad.pivot_table(
                    index='Mes',
                    columns='Tipo de Gasto',
                    values='Monto',
                    aggfunc='sum'
                ).fillna(0)
                pivot_data.plot(kind='bar', stacked=True)
                plt.title(f'Gastos Mensuales - {unidad}')
                plt.xlabel('Mes')
                plt.ylabel('Monto ($)')
                plt.xticks(rotation=45)
                plt.tight_layout()
                imgdata = io.BytesIO()
                plt.savefig(imgdata, format='png')
                imgdata.seek(0)
                worksheet.insert_image('F2', 'grafica', {'image_data': imgdata})
                plt.close()
                total_operativo = df_unidad['Monto'].sum()
                totales_unidad[unidad] = total_operativo
                last_row = len(resumen_final) + 3
                worksheet.write(last_row, 0, 'Total Operativo:', header_format)
                worksheet.write(last_row, 1, total_operativo, money_format)
            summary_sheet = workbook.add_worksheet('Resumen General')
            summary_sheet.write(0, 0, 'Unidad de Negocio', header_format)
            summary_sheet.write(0, 1, 'Total Operativo', header_format)
            for row_idx, (unidad, total) in enumerate(totales_unidad.items(), start=1):
                summary_sheet.write(row_idx, 0, unidad)
                summary_sheet.write(row_idx, 1, total, money_format)
            summary_sheet.set_column('A:A', 30)
            summary_sheet.set_column('B:B', 20)
        else:
            workbook = writer.book
            worksheet = workbook.add_worksheet('SinDatos')
            worksheet.write(0, 0, 'No hay datos para generar el reporte.')
    output.seek(0)
    return FileResponse(output, as_attachment=True, filename='reporte_gastos.xlsx')

def estado_resultados(request):
    resumen_rows = request.session.get('resumen_rows', None)
    data = []
    resumen_lista = []
    if resumen_rows:
        resumen_rows = json.loads(resumen_rows)
        for row in resumen_rows:
            data.append(row)
        df = pd.DataFrame(data)
        if not df.empty:
            # Aseguramos que la columna 'total' sea numérica, ignorando errores
            if 'total' in df.columns:
                df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)
            else:
                df['total'] = 0
            # Definir los 15 campos para agrupar
            campos_agrupacion = [
                'tipo_gasto', 'tipo_costo', 'unidad1_1', 'unidad1_2', 'unidad1_3', 'unidad1_4', 'unidad1_5',
                'suma_unidad1', 'unidad2', 'unidad3', 'unidad4', 'unidad5', 'unidad6', 'unidad7', 'unidad8',
                'suma_todas_lasunidades', 'mes', 'tipo', 'cuenta', 'descripcion'
            ]
            campos_existentes = [c for c in campos_agrupacion if c in df.columns]
            total_general = df['total'].sum() if 'total' in df.columns else 0
            if campos_existentes:
                agrupado = df.groupby(campos_existentes, dropna=False).agg({'total': 'sum'}).reset_index()
                for _, row in agrupado.iterrows():
                    porcentaje = round(100 * row['total'] / total_general, 2) if total_general > 0 else 0
                    resumen_item = {c: row[c] for c in campos_existentes}
                    resumen_item['total'] = row['total']
                    resumen_item['porcentaje'] = porcentaje
                    resumen_lista.append(resumen_item)
            else:
                resumen_lista = []
            # Estado de resultados básico
            total_ventas = float(df[df.get('tipo', '') == 'venta']['total'].sum()) if 'tipo' in df.columns else 0.0
            total_gastos = float(df[df.get('tipo', '') == 'compra']['total'].sum()) if 'tipo' in df.columns else 0.0
            totalidad_operativa = total_ventas - total_gastos
        else:
            total_ventas = 0.0
            total_gastos = 0.0
            totalidad_operativa = 0.0
    else:
        total_ventas = 0.0
        total_gastos = 0.0
        totalidad_operativa = 0.0
    estado_resultados = {
        'total_ventas': total_ventas,
        'total_gastos': total_gastos,
        'totalidad_operativa': totalidad_operativa
    }
    return render(request, 'resumen/estado_resultados.html', {'estado_resultados': estado_resultados, 'resumen': resumen_lista})

def resumen_general(request):
    resumen_rows = request.session.get('resumen_rows', None)
    resumen_lista = []
    if resumen_rows:
        resumen_rows = json.loads(resumen_rows)
        df = pd.DataFrame(resumen_rows)
        if not df.empty:
            total_general = df['total'].sum()
            agrupado = df.groupby(['cuenta', 'unidad', 'mes', 'año'], dropna=False).agg({'total': 'sum'}).reset_index()
            for _, row in agrupado.iterrows():
                porcentaje = round(100 * row['total'] / total_general, 2) if total_general > 0 else 0
                resumen_lista.append({
                    'cuenta': row['cuenta'],
                    'unidad': row['unidad'],
                    'mes': row['mes'],
                    'año': row['año'],
                    'total': row['total'],
                    'porcentaje': porcentaje
                })
    return render(request, 'resumen/resumen_general.html', {'resumen': resumen_lista})

def descargar_resumen_excel(request):
    resumen_rows = request.session.get('resumen_rows', None)
    data = []
    resumen_lista = []
    if resumen_rows:
        resumen_rows = json.loads(resumen_rows)
        for row in resumen_rows:
            data.append(row)
        df = pd.DataFrame(data)
        if not df.empty:
            df['agrupacion'] = df['cuenta'].apply(lambda x: 'Ingresos' if 'Ingreso' in str(x) else ('Costo de Producción' if 'Costo' in str(x) else 'Gasto OPERATIVO'))
            total_ventas = float(df[df['agrupacion'] == 'Ingresos']['total'].sum())
            total_gastos = float(df[df['agrupacion'] != 'Ingresos']['total'].sum())
            totalidad_operativa = total_ventas - total_gastos
            total_general = df['total'].sum()
            agrupado = df.groupby(['cuenta', 'unidad', 'mes', 'año'], dropna=False).agg({'total': 'sum'}).reset_index()
            for _, row in agrupado.iterrows():
                porcentaje = round(100 * row['total'] / total_general, 2) if total_general > 0 else 0
                resumen_lista.append({
                    'cuenta': row['cuenta'],
                    'unidad': row['unidad'],
                    'mes': row['mes'],
                    'año': row['año'],
                    'total': row['total'],
                    'porcentaje': porcentaje
                })
        else:
            total_ventas = 0.0
            total_gastos = 0.0
            totalidad_operativa = 0.0
    else:
        total_ventas = 0.0
        total_gastos = 0.0
        totalidad_operativa = 0.0
    # Crear el archivo Excel en memoria
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Estado de Resultados')
    # Escribir encabezados
    worksheet.write('A1', 'Total Ventas')
    worksheet.write('B1', 'Total Gastos')
    worksheet.write('C1', 'Totalidad Operativa')
    worksheet.write('A2', total_ventas)
    worksheet.write('B2', total_gastos)
    worksheet.write('C2', totalidad_operativa)
    # Escribir resumen general
    resumen_ws = workbook.add_worksheet('Resumen General')
    headers = ['Cuenta', 'Unidad', 'Mes', 'Año', 'Costo', '% del Total']
    for col, header in enumerate(headers):
        resumen_ws.write(0, col, header)
    for row_idx, item in enumerate(resumen_lista, start=1):
        resumen_ws.write(row_idx, 0, item['cuenta'])
        resumen_ws.write(row_idx, 1, item['unidad'])
        resumen_ws.write(row_idx, 2, item['mes'])
        resumen_ws.write(row_idx, 3, item['año'])
        resumen_ws.write(row_idx, 4, item['total'])
        resumen_ws.write(row_idx, 5, item['porcentaje'])
    workbook.close()
    output.seek(0)
    response = FileResponse(output, as_attachment=True, filename='estado_resultados_resumen.xlsx')
    return response

def descargar_resumen_pdf(request):
    resumen_rows = request.session.get('resumen_rows', None)
    data = []
    resumen_lista = []
    if resumen_rows:
        resumen_rows = json.loads(resumen_rows)
        for row in resumen_rows:
            data.append(row)
        df = pd.DataFrame(data)
        if not df.empty:
            df['agrupacion'] = df['cuenta'].apply(lambda x: 'Ingresos' if 'Ingreso' in str(x) else ('Costo de Producción' if 'Costo' in str(x) else 'Gasto OPERATIVO'))
            total_ventas = float(df[df['agrupacion'] == 'Ingresos']['total'].sum())
            total_gastos = float(df[df['agrupacion'] != 'Ingresos']['total'].sum())
            totalidad_operativa = total_ventas - total_gastos
            total_general = df['total'].sum()
            agrupado = df.groupby(['cuenta', 'unidad', 'mes', 'año'], dropna=False).agg({'total': 'sum'}).reset_index()
            for _, row in agrupado.iterrows():
                porcentaje = round(100 * row['total'] / total_general, 2) if total_general > 0 else 0
                resumen_lista.append({
                    'cuenta': row['cuenta'],
                    'unidad': row['unidad'],
                    'mes': row['mes'],
                    'año': row['año'],
                    'total': row['total'],
                    'porcentaje': porcentaje
                })
        else:
            total_ventas = 0.0
            total_gastos = 0.0
            totalidad_operativa = 0.0
    else:
        total_ventas = 0.0
        total_gastos = 0.0
        totalidad_operativa = 0.0
    # Crear PDF en memoria
    output = io.BytesIO()
    p = canvas.Canvas(output, pagesize=letter)
    width, height = letter
    y = height - 40
    p.setFont('Helvetica-Bold', 16)
    p.drawString(40, y, 'Estado de Resultados')
    y -= 30
    p.setFont('Helvetica', 12)
    p.drawString(40, y, f'Total Ventas: ${total_ventas:.2f}')
    y -= 20
    p.drawString(40, y, f'Total Gastos: ${total_gastos:.2f}')
    y -= 20
    p.drawString(40, y, f'Totalidad Operativa: ${totalidad_operativa:.2f}')
    y -= 40
    p.setFont('Helvetica-Bold', 14)
    p.drawString(40, y, 'Resumen General')
    y -= 25
    p.setFont('Helvetica-Bold', 10)
    p.drawString(40, y, 'Cuenta')
    p.drawString(120, y, 'Unidad')
    p.drawString(200, y, 'Mes')
    p.drawString(240, y, 'Año')
    p.drawString(280, y, 'Costo')
    p.drawString(340, y, '% del Total')
    y -= 15
    p.setFont('Helvetica', 10)
    for item in resumen_lista:
        if y < 50:
            p.showPage()
            y = height - 40
        p.drawString(40, y, str(item['cuenta']))
        p.drawString(120, y, str(item['unidad']))
        p.drawString(200, y, str(item['mes']))
        p.drawString(240, y, str(item['año']))
        p.drawString(280, y, f"${item['total']:.2f}")
        p.drawString(340, y, f"{item['porcentaje']}%")
        y -= 15
    p.save()
    output.seek(0)
    response = FileResponse(output, as_attachment=True, filename='estado_resultados_resumen.pdf')
    return response

# Descarga de plantilla de ejemplo
@require_GET
def descargar_plantilla(request):
    plantilla_path = os.path.join(settings.MEDIA_ROOT, 'plantilla_ejemplo.xlsx')
    return FileResponse(open(plantilla_path, 'rb'), as_attachment=True, filename='plantilla_ejemplo.xlsx')
