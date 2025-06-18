# Sistema de Gestión de Gastos

Sistema web desarrollado en Django para la gestión y análisis de gastos empresariales, con capacidad de importación de datos desde archivos Excel y generación de reportes detallados.

## Características Principales

- 📊 Importación de datos desde archivos Excel
- 📈 Clasificación automática de gastos
- 📑 Generación de resúmenes y reportes
- 🔄 Procesamiento de múltiples unidades de negocio
- 📱 Interfaz web responsive y fácil de usar

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/Vale2704/proyecto-gestion-gastos.git
cd proyecto-gestion-gastos
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Realizar migraciones:
```bash
python manage.py migrate
```

5. Iniciar el servidor:
```bash
python manage.py runserver
```

## Uso

1. Acceder a la aplicación:
   - Abrir el navegador y visitar: `http://127.0.0.1:8000/`

2. Subir archivo Excel:
   - Ir a la sección "Subir archivo Excel"
   - Seleccionar el archivo con el formato correcto
   - El sistema procesará automáticamente los datos

3. Ver reportes:
   - Clasificación de gastos
   - Resumen general
   - Estado de resultados

## Estructura del Proyecto

```
proyecto-gestion-gastos/
├── estado_resultados_uni/    # Configuración principal de Django
├── resumen/                  # Aplicación principal
│   ├── migrations/          # Migraciones de la base de datos
│   ├── templates/           # Plantillas HTML
│   ├── models.py           # Modelos de datos
│   └── views.py            # Lógica de la aplicación
├── manage.py               # Script de administración
└── requirements.txt        # Dependencias del proyecto
```

## Formato del Archivo Excel

El archivo Excel debe contener las siguientes hojas:
- Compras
- Ventas

Columnas requeridas:
- cuenta_de_costos
- nombre_del_artículo
- tipo_costo
- Columnas de unidades (unidad1.1, unidad1.2, etc.)
- Columnas de meses (ene'2024, feb'2024, etc.)

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Autor

Valery Nitch Rodríguez
- GitHub: [@Vale2704](https://github.com/Vale2704)

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles. 