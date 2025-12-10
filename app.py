from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Configurar carpeta donde se guardarán los videos
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Crear carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Variables donde se guardarán los datos del formulario
semana = None
finca = None
invernadero = None
cama = None
fecha = None
hora = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/formulario")
def formulario():
    return render_template("formulario.html")


@app.route("/guardar_datos", methods=["POST"])
def guardar_datos():
    global semana, finca, invernadero, cama, fecha, hora

    semana = request.form["semana"]
    finca = request.form["finca"]
    invernadero = request.form["invernadero"]
    cama = request.form["cama"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    print("Datos recibidos:")
    print("Semana:", semana)
    print("Finca:", finca)
    print("Invernadero:", invernadero)
    print("Cama:", cama)
    print("Fecha:", fecha)
    print("Hora:", hora)

    return redirect(url_for("formulario"))


@app.route("/subir_video", methods=["POST"])
def subir_video():
    if "video" not in request.files:
        return "No se envió el archivo", 400

    archivo = request.files["video"]

    if archivo.filename == "":
        return "Nombre de archivo no válido", 400

    ruta_final = os.path.join(app.config["UPLOAD_FOLDER"], archivo.filename)
    archivo.save(ruta_final)

    print("Video guardado en:", ruta_final)

    return f"""
    <h2>Video subido correctamente</h2>
    <video width="500" controls>
        <source src="/static/uploads/{archivo.filename}" type="video/mp4">
    </video>
    <br><a href="/formulario">Volver</a>
    """


if __name__ == "__main__":
    app.run(debug=True)
