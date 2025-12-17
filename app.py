from flask import Flask, render_template, request, url_for
import os
import psycopg2
from datetime import datetime
from datetime import date
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import mimetypes
from flask import Flask, render_template, request, url_for, redirect

mimetypes.add_type('video/mp4', '.mp4')

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_connection():
    return psycopg2.connect(
        host="hopper.proxy.rlwy.net",
        database="railway",
        user="postgres",
        password="ySqSlZsapBqdJouMeLyrgjOZikxtfADc",
        port="20905"
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/formulario")
def formulario():
    return render_template("formulario.html")


@app.route("/subir_video", methods=["POST"])
def subir_video():
    cloudinary.config(
        cloud_name="dve6ex3cp",
        api_key="841612397828224",
        api_secret="vDQYZZ5pC3TQBFyt2-V1UrHHKKI",  # Click 'View API Keys' above to copy your API secret
        secure=True
    )

    # 📌 Datos
    semana = request.form["semana"]
    finca = request.form["finca"]
    invernadero = request.form["invernadero"]
    cama = request.form["cama"]
    fecha_video = request.form["fecha"]
    hora_video = request.form["hora"]
    fecha= date.today()
    hora = datetime.now()


    # 📌 Archivo
    archivo = request.files["video"]
    if archivo.filename == "":
        return "Archivo inválido", 400

    resultado = cloudinary.uploader.upload(
        archivo,
        resource_type="video"
    )

    ruta_final = resultado["secure_url"]

    # 📌 Insertar en BD
    conn = get_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO registros (
            semana, finca, invernadero, cama,
            fecha_video, hora_video,
            fecha, hora, archivo
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cur.execute(sql, (
        semana,
        finca,
        invernadero,
        cama,
        fecha_video,
        hora_video,
        fecha,
        hora,
        ruta_final
    ))

    conn.commit()
    cur.close()
    conn.close()

    video_url = url_for("static", filename=f"uploads/{archivo.filename}")

    return render_template(
        "video.html",
        video_url=video_url
    )

@app.route("/historico", methods=["GET"])
def historico():
    semana = request.args.get("semana")
    finca = request.args.get("finca")
    invernadero = request.args.get("invernadero")
    cama = request.args.get("cama")
    fecha_video = request.args.get("fecha_video")
    fecha = request.args.get("fecha")

    query = """
        SELECT semana, finca, invernadero, cama,
               fecha_video, hora_video,
               fecha, hora, archivo
        FROM registros
        WHERE 1=1
    """
    params = []

    # 🔢 NUMÉRICOS → EXACTO
    if semana:
        query += " AND semana = %s"
        params.append(int(semana))

    if invernadero:
        query += " AND invernadero = %s"
        params.append(int(invernadero))

    if cama:
        query += " AND cama = %s"
        params.append(int(cama))

    # 🔤 TEXTO → PARCIAL
    if finca:
        query += " AND finca ILIKE %s"
        params.append(f"%{finca}%")

    # 📅 FECHAS → EXACTO
    if fecha_video:
        query += " AND fecha_video = %s"
        params.append(fecha_video)

    if fecha:
        query += " AND fecha = %s"
        params.append(fecha)

    query += " ORDER BY fecha DESC, hora DESC"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    registros = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("historico.html", registros=registros)

@app.route("/eliminar", methods=["POST"])
def eliminar():
    invernadero = request.form["invernadero"]
    cama = request.form["cama"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM registros
        WHERE invernadero = %s
          AND cama = %s
          AND fecha = %s
          AND hora = %s
    """, (invernadero, cama, fecha, hora))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("historico"))

if __name__ == "__main__":
    app.run(debug=True)


