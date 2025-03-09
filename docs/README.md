# RePA

El Registro Provincial Audiovisual, tiene como objetivo implementar una base de datos del Instituto de Artes Audiovisuales de Misiones, en la que se pueda registrar a todas aquellas personas que de una u otra manera están involucradas en la producción Audiovisual.



## Lógica de la aplicación:

La aplicación recopila información principalmente de dos tipos de entidades:
**Personas** y **Empresas**

### Relación de las entidades

```
RePA_app/
│
├── usuarios/
│   ├── persona*
│   ├── presentacion_personal
│   ├── obra_audiovisual
│   ├── capacitacion
│   ├── formacion*
│   ├── participacion_IAAVIM
│   ├── empresa*
│         ├── obra_audiovisual
│         ├── participacion_foros

```

La información es cargada en la plataforma a partir de un usuario.

El usuario será responsable de la información proporcionada: deberá registrar su información personal, las obras audiovisuales, capacitaciones, formación y su participación en IAAVIM.

De la misma manera, un usuario podrá registrar todas las empresas que haya creado y la información asociada a cada empresa, como las obras producidas, participaciones, etc.


## Estructura de la aplicación:

La API de Backend mantiene la sigueinte estructura de directorios:

```
my_app/
├── main.py
├── auth/
│   ├── auth.py
│   ├── permissions.py
├── db/
│   ├── database.py
├── models/
│   ├── user_model.py
├── schemas/
│   ├── user_schema.py
├── routes/
│   ├── user_routes.py
└── requirements.txt
```

- En el directorio **db** se encuentra el archivo de configuración de conexión a la base de datos, y es utilizado por los distintos módulos que necesitan conectarse a los datos.
- El directorio **auth** contiene las funcionalidades que permiten la gestión de tokens y la gestión de las Listas de Control de Acceso (ACL) de los usuarios.
- En el directorio **models** se encuentran definidos los modelos de datos para cada uno de los objetos, como *usuarios*, *personas*, *empresas*, etc.
- En el directorio **schemas** se encuentran definidas las **clases** que define la estructura de datos para cada uno de los objetos, y cómo se interactúa con ellos en cada caso.
- En el directorio **routes** se encuentra la lógica del sistema: se declaran las rutas para la ejecución de las funcionalidades del sistema, y la lógica de funcionamiento. Implementa también las ACL a cada una de las rutas, de acuerdo a la lógica de negocio definida.

Mediante esta estructura, es posible extender el funcionamiento de la API, incorporando en cada caso los distintos elementos para un "módulo" o función.

Para incorporar el "modulo" de empresa, se debe crear un *modelo* de datos, que será creado e insertado en la base de datos. Un *schema* que define las clases para el objeto de datos que se va a manipular (una empresa, un curso, etc.) y finalmente *routes* donde se define la lógica de negocio y restricciones propias del módulo a implementar.
