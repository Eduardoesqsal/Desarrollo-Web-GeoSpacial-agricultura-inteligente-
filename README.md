# Desarrollo-Web-GeoSpacial-agricultura-inteligente-
flujo para generación de índices para agricultura de precisión 

Overla_Nvdi_Array
🌍 WebGIS NDVI Viewer
Aplicación Flask + Leaflet para visualizar ortomosaicos RGB y generar un análisis de NDVI (Índice de Vegetación de Diferencia Normalizada) en la web.
Permite cargar imágenes GeoTIFF, normalizar bandas, generar overlays, visualizar histogramas y aplicar máscaras de transparencia sobre vegetación y suelo.

🚀 Características
Visualización RGB y NDVI sobre mapas base satelitales.
Escalado automático de imágenes grandes (optimización).
Histograma interactivo del NDVI con rampa de colores rojo → verde.
Slider dinámico para filtrar rangos de NDVI.
Botón de transparencia de suelo automático.
Funcionalidad de recorte por polígono en el mapa (con Leaflet-Geoman).
Compatible con ortomosaicos provenientes de drones.

## 📂 Estructura del Proyecto

```plaintext
Proyecto_NDVI/
├── app.py                # Backend Flask (API para RGB, NDVI y recortes)
├── index.html            # Interfaz web (Leaflet, controles, visualización de NDVI)
├── requirements.txt      # Dependencias del proyecto
├── Or.tif                # Ortofoto de entrada (GeoTIFF)
├── static/               # Carpeta para overlays y recortes generados
│   ├── overlay.png        # Imagen overlay (NDVI o RGB procesado)
│   ├── bounds_overlay.txt # Límites geográficos del overlay
│   └── recorte_overlay.png # Recorte generado dinámicamente
o dinámicamente


yaml Copiar Editar

⚙️ Instalación
Clonar este repositorio o copiar los archivos a una carpeta local.

Crear un entorno virtual (opcional pero recomendado):

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
Instalar dependencias:

bash
Copiar
Editar
pip install -r requirements.txt
▶️ Uso
Coloca tu ortomosaico en la raíz del proyecto y actualiza la ruta en app.py:

python
Copiar
Editar
RASTER_PATH = r"C:\\Users\\tu_usuario\\downloads\\Or.tif" cambia a tu ruta local para lectura.
Ejecuta el servidor:

bash
Copiar
Editar
python app.py copiar este comando para correr la app
Abre en tu navegador: en http://127.0.0.1:5000

cpp
Copiar
Editar
http://127.0.0.1:5000/
🖼️ Funcionalidades principales
Capa RGB: Visualiza la ortofoto en colores naturales.

Capa NDVI: Aplica cálculo NDVI con escala de color personalizada.

Histograma: Muestra distribución de valores NDVI.

Slider NDVI: Filtra visualización en rango seleccionado.

Recorte: Dibuja un polígono y genera un overlay de la zona seleccionada.

📦 Requerimientos principales
Python 3.9+

Flask

Rasterio

Numpy

Pillow (PIL)

Shapely

PyProj

Matplotlib

Todos incluidos en requirements.txt.

📌 Notas
Si el raster es muy grande (> 5GB), el backend aplica resampling automático para no saturar memoria.

La carpeta static/ guarda los overlays generados en cada ejecución.

El sistema está optimizado para ortomosaicos de drones con bandas RGB + NIR.

Demostraciones 

<img width="1919" height="911" alt="image" src="https://github.com/user-attachments/assets/c44c50b1-11ea-461f-ace9-51636c65692a" />

<img width="1899" height="915" alt="image" src="https://github.com/user-attachments/assets/3024a216-4220-4d4b-a0d6-40d55f27a7d5" />

