from flask import Flask, request, jsonify, send_from_directory
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import mask
from rasterio.warp import transform_bounds
from rasterio.transform import xy
import numpy as np
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
from shapely.geometry import shape, mapping
from shapely.ops import transform as shapely_transform
import pyproj
import os

app = Flask(__name__)

RASTER_PATH = r"C:\\Users\\eduar\\downloads\\Or.tif"
OUTPUT_FOLDER = "static"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def normalizar(banda):
    banda = banda.astype(np.float32)
    mask_val = banda > 0
    if np.any(mask_val):
        min_val = np.nanmin(banda[mask_val])
        max_val = np.nanmax(banda[mask_val])
    else:
        min_val, max_val = 0, 1
    norm = ((banda - min_val) / (max_val - min_val) * 255).clip(0, 255).astype(np.uint8)
    return norm

def obtener_escala(src, max_pixels=2_000_000):
    total_pixels = src.width * src.height
    escala = max(1, int((total_pixels / max_pixels)**0.5))
    return escala

def generar_overlay_base():
    with rasterio.open(RASTER_PATH) as src:
        escala = obtener_escala(src)
        alto = src.height // escala
        ancho = src.width // escala

        r = src.read(1, out_shape=(alto, ancho), resampling=Resampling.average)
        g = src.read(2, out_shape=(alto, ancho), resampling=Resampling.average)
        b = src.read(3, out_shape=(alto, ancho), resampling=Resampling.average)

        r_norm = normalizar(r)
        g_norm = normalizar(g)
        b_norm = normalizar(b)

        alpha = np.where((r_norm == 0) & (g_norm == 0) & (b_norm == 0), 0, 255).astype(np.uint8)
        rgba = np.dstack((r_norm, g_norm, b_norm, alpha))

        img = Image.fromarray(rgba, mode="RGBA")
        img.save(os.path.join(OUTPUT_FOLDER, "overlay.png"))
        print("[INFO] Overlay RGB base generado.")

        height, width = alto, ancho
        transform = src.transform * src.transform.scale(
            (src.width / width),
            (src.height / height)
        )
        top_left = xy(transform, 0, 0, offset='ul')
        bottom_right = xy(transform, height, width, offset='lr')
        minx, maxy = top_left
        maxx, miny = bottom_right

        if src.crs.to_string() != 'EPSG:4326':
            minx, miny, maxx, maxy = transform_bounds(
                src.crs.to_string(), 'EPSG:4326', minx, miny, maxx, maxy
            )

        bounds = [[miny, minx], [maxy, maxx]]
        with open(os.path.join(OUTPUT_FOLDER, "bounds_overlay.txt"), "w") as f:
            f.write(str(bounds))

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.abspath(OUTPUT_FOLDER), filename)

@app.route('/bounds')
def get_bounds():
    try:
        with open(os.path.join(OUTPUT_FOLDER, "bounds_overlay.txt")) as f:
            bounds = eval(f.read())
        return jsonify({'status': 'ok', 'bounds': bounds})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/rgb_data')
def rgb_data():
    try:
        with rasterio.open(RASTER_PATH) as src:
            escala = obtener_escala(src)
            alto = src.height // escala
            ancho = src.width // escala

            r = src.read(1, out_shape=(alto, ancho), resampling=Resampling.average)
            g = src.read(2, out_shape=(alto, ancho), resampling=Resampling.average)
            b = src.read(3, out_shape=(alto, ancho), resampling=Resampling.average)

            r_norm = normalizar(r)
            g_norm = normalizar(g)
            b_norm = normalizar(b)

            alpha = np.where((r_norm == 0) & (g_norm == 0) & (b_norm == 0), 0, 255).astype(np.uint8)
            rgba = np.dstack((r_norm, g_norm, b_norm, alpha))
            rgb_matrix = rgba.tolist()

        return jsonify({'status': 'ok', 'rgb_matrix': rgb_matrix})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/ndvi_data')
def ndvi_data():
    try:
        with rasterio.open(RASTER_PATH) as src:
            escala = obtener_escala(src)
            alto = src.height // escala
            ancho = src.width // escala

            red = src.read(4, out_shape=(alto, ancho), resampling=Resampling.average).astype(np.float32)
            nir = src.read(6, out_shape=(alto, ancho), resampling=Resampling.average).astype(np.float32)

            ndvi = (nir - red) / (nir + red + 1e-6)
            ndvi_normalizado = np.clip((ndvi + 1) / 2, 0, 1)

            mask_val = (red > 0) & (nir > 0)
            colors = ["#8B0000", "#FF6347", "#FF1100", "#FFFF00", "#28D606"]
            cmap = LinearSegmentedColormap.from_list("ndvi_custom", colors, N=256)
            rgba_float = cmap(ndvi_normalizado)
            rgba_uint8 = (rgba_float * 255).astype(np.uint8)
            alpha = np.zeros_like(ndvi_normalizado, dtype=np.uint8)
            alpha[mask_val] = 255
            rgba_uint8[..., 3] = alpha

            ndvi_matrix = rgba_uint8.tolist()

        return jsonify({'status': 'ok', 'ndvi_matrix': ndvi_matrix})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/recortar', methods=['POST'])
def recortar():
    try:
        data = request.get_json()
        if not data or 'geojson' not in data:
            return jsonify({'status': 'error', 'message': 'No GeoJSON recibido'}), 400

        geom = shape(data['geojson']['geometry'])
        tipo = data.get('tipo', 'rgb')

        with rasterio.open(RASTER_PATH) as src:
            if src.crs.to_string() != 'EPSG:4326':
                transformer = pyproj.Transformer.from_crs("EPSG:4326", src.crs, always_xy=True).transform
                geom = shapely_transform(transformer, geom)

            out_image, out_transform = mask(src, [mapping(geom)], crop=True)

            r = normalizar(out_image[0])
            g = normalizar(out_image[1])
            b = normalizar(out_image[2])
            alpha = np.where((r == 0) & (g == 0) & (b == 0), 0, 255).astype(np.uint8)
            rgba = np.dstack((r, g, b, alpha))

            salida = os.path.join(os.path.abspath(OUTPUT_FOLDER), "recorte_overlay.png")
            img = Image.fromarray(rgba, mode="RGBA")
            img.save(salida)

            height, width = out_image.shape[1], out_image.shape[2]
            top_left = xy(out_transform, 0, 0, offset='ul')
            bottom_right = xy(out_transform, height, width, offset='lr')
            minx, maxy = top_left
            maxx, miny = bottom_right

            if src.crs.to_string() != 'EPSG:4326':
                minx, miny, maxx, maxy = transform_bounds(
                    src.crs.to_string(), 'EPSG:4326', minx, miny, maxx, maxy
                )

            bounds_leaflet = [[miny, minx], [maxy, maxx]]

        return jsonify({
            'status': 'ok',
            'overlay_path': '/static/recorte_overlay.png',
            'bounds': bounds_leaflet
        })

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("[INFO] Generando overlays base antes de iniciar servidor...")
    generar_overlay_base()
    app.run(debug=True)
