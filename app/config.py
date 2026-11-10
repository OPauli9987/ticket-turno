"""Configuracion central de la aplicacion"""
from pathlib import Path


class Config:
    APP_NAME = "Ticket de Turno"
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = str(DATA_DIR / "ticket_turno.db")

    ESTATUS_PENDIENTE = "Pendiente"
    ESTATUS_RESUELTO = "Resuelto"
    ESTATUS_VALIDOS = (ESTATUS_PENDIENTE, ESTATUS_RESUELTO)

    # Administrador inicial
    ADMIN_USUARIO = "admin"
    ADMIN_PASSWORD = "Admin123"
    ADMIN_NOMBRE = "Administrador General"

    # Datos semilla de catalogos
    MUNICIPIOS = [
        "Abasolo", "Acuña", "Allende", "Arteaga", "Candela", "Castaños",
        "Cuatro Ciénegas", "Escobedo", "Francisco I. Madero", "Frontera",
        "General Cepeda", "Guerrero", "Hidalgo", "Jiménez", "Juárez",
        "Lamadrid", "Matamoros", "Monclova", "Morelos", "Múzquiz",
        "Nadadores", "Nava", "Ocampo", "Parras", "Piedras Negras",
        "Progreso", "Ramos Arizpe", "Sabinas", "Sacramento", "Saltillo",
        "San Buenaventura", "San Juan de Sabinas", "San Pedro",
        "Sierra Mojada", "Torreón", "Viesca", "Villa Unión", "Zaragoza",
    ]
    NIVELES = ["Preescolar", "Primaria", "Secundaria", "Bachillerato",
               "Educación especial", "Educación para adultos"]
    ASUNTOS = ["Inscripción", "Reinscripción", "Cambio de escuela",
               "Baja de alumno", "Constancia de estudios",
               "Certificado / boleta", "Corrección de datos",
               "Beca", "Otro trámite"]
