# Ticket de Turno

Sistema de escritorio para que padres de familia agenden citas de trámites
escolares de sus hijos. Los administradores consultan, modifican y resuelven
las solicitudes y ven un dashboard.

## Ejecutar
```bash
python main.py            
pip install reportlab     
```
En Linux, si falta tkinter: `sudo apt install python3-tk`.

**Administrador inicial:** usuario `admin` · contraseña `Admin123`
(se crea solo la primera vez; la contraseña se guarda con PBKDF2 + sal).


# Modelo Base de datos

```mermaid
erDiagram
    MUNICIPIO ||--o{ SOLICITUD : "estudia en"
    NIVEL_EDUCATIVO ||--o{ SOLICITUD : "cursa"
    ASUNTO ||--o{ SOLICITUD : "trata"
    MUNICIPIO ||--|| TURNO_CONTADOR : "lleva"

    MUNICIPIO {
        int id PK
        string nombre UK
    }
    NIVEL_EDUCATIVO {
        int id PK
        string nombre UK
    }
    ASUNTO {
        int id PK
        string nombre UK
    }
    ADMINISTRADOR {
        int id PK
        string usuario UK
        string nombre
        string salt
        string password_hash
    }
    TURNO_CONTADOR {
        int municipio_id PK
        int ultimo
    }
    SOLICITUD {
        string curp PK
        string nombre_alumno
        string apellido_paterno
        string apellido_materno
        string nombre_tramitante
        string telefono
        string telefono_alterno
        string correo
        int nivel_id FK
        int municipio_id FK
        int asunto_id FK
        string observaciones
        int numero_turno
        string estatus
        string fecha_registro
        string fecha_modificacion
    }
```

# Modelo de clases

```mermaid
classDiagram
    class Catalogo {
        +int id
        +str nombre
    }
    Catalogo <|-- Municipio
    Catalogo <|-- NivelEducativo
    Catalogo <|-- Asunto

    class Solicitud {
        +str curp PK
        +str nombre_alumno
        +str apellido_paterno
        +str apellido_materno
        +str nombre_tramitante
        +str telefono
        +str telefono_alterno
        +str correo
        +int numero_turno
        +str estatus
        +str fecha_registro
        +nombre_completo()
    }
    class Administrador {
        +int id
        +str usuario
        +str nombre
        +str salt
        +str password_hash
    }

    Solicitud "*" --> "1" Municipio
    Solicitud "*" --> "1" NivelEducativo
    Solicitud "*" --> "1" Asunto

    class Database {
        <<Singleton>>
        +get_instance()
        +connect()
        +close()
    }
    class Session {
        <<Singleton>>
        +iniciar()
        +clear()
    }
    class Subject {
        <<Observer>>
        +attach()
        +detach()
        +notify()
    }

    class CatalogoDAO {
        +listar()
        +insertar()
        +actualizar()
        +eliminar()
    }
    CatalogoDAO <|-- MunicipioDAO
    CatalogoDAO <|-- NivelEducativoDAO
    CatalogoDAO <|-- AsuntoDAO
    class SolicitudDAO {
        +insertar()
        +actualizar()
        +buscar_por_curp()
        +buscar_por_nombre()
        +contar_por_estatus()
    }
    class AdministradorDAO {
        +buscar_por_usuario()
    }

    class SolicitudController {
        +registrar()
        +modificar_publico()
        +buscar()
        +cambiar_estatus()
        +eliminar()
    }
    class CatalogoController {
        +listar()
        +crear()
        +actualizar()
        +eliminar()
    }
    class AuthController {
        +login()
        +logout()
    }
    class DashboardController {
        +conteo_por_estatus()
    }
    class AppController {
        +cerrar_sistema()
    }

    SolicitudController --> SolicitudDAO
    SolicitudController *-- Subject
    CatalogoController --> CatalogoDAO
    AuthController --> AdministradorDAO
    AuthController --> Session
    AppController *-- SolicitudController
    AppController *-- CatalogoController
    AppController *-- AuthController
    AppController *-- DashboardController
    SolicitudDAO --> Database
    CatalogoDAO --> Database

    class MainWindow
    class RegistroView
    class ModificarView
    class LoginView
    class AdminSolicitudesView
    class CatalogoView
    class DashboardView
    class ObserverView {
        <<Observer>>
        +update()
    }
    ObserverView <|-- AdminSolicitudesView
    ObserverView <|-- DashboardView
    MainWindow --> AppController
```
Validación: `CurpValidator`, `SolicitudValidator`. Seguridad: `PasswordHasher`.
Comprobante: `ComprobanteService`.

