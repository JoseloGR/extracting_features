# Extracción de Features de Tweets

## Instalación

Se desarrolló como una aplicación de Backend utilizando el framework [FastAPI](https://fastapi.tiangolo.com/). Utiliza Python como lenguaje de programación y el proyecto ya tiene incluido un pequeño server que levanta una aplicación web con la documentación y opciones para ejecutar los endpoints sin usar otra herramienta.

Para correr el proyecto se recomienda utilizar `pipenv`. Previamente debes tener instalado Python, `pipenv` y `pip`. A continuación puedes revisar la documentación de `pipenv` por cualquier duda:

- [PipEnv](https://pipenv-es.readthedocs.io/es/latest)
- Python versión mínima 3.9.6
- pip versión mínima 21.2.1

Para instalar `pipenv` basta con correr el siguiente comando:

```
pip install pipenv
```


### Restauración de BD

Para que el proyecto pueda ejecutarse se debe tener instalado MongoDB de forma local.

Puedes revisar cómo instalar MongoDB dependiendo de tu SO en el siguiente [link](https://docs.mongodb.com/manual/installation/)

Con el siguiente comando restaurarás la BD generada durante la ejecución de los endpoints de extracción

```
mongorestore tweetsdb/
```

### Activar virtual environment

Ejecutar el siguiente comando para activar el virtual env de `pipenv`:

```
pipenv shell
```

Una vez activo, se deben instalar las dependencias:

```
pipenv install
```

Antes de levantar el server, se deben agregar las variables de ambiente de las API Keys a utilizar.

Debes copiar el archivo `.env.example`, renombrar el archivo como `.env` y pasarle los valores de API Keys

Para correr el server ejecutar el siguiente comando:

```
uvicorn main:app --reload
```

Con el server corriendo, abrir tu navegador favorito y entrar a `http://127.0.0.1:8000/docs`. En esta aplicación web encontrarás los endpoints que se utilizaron para extraer los sentimientos y emociones de los tweets.

Cabe resaltar que la información obtenida de Meaning Cloud y Parallel Dots se fue almacenando en una Base de Datos local de MongoDB.

Una vez que todos los tweets tuvieran la información se generó el csv correspondiente con la herramienta de mongo => mongoexport

## Endpoints: Sentimientos y Emociones

Para visualizar los primeros 10 tweets con los resultados de los rasgos ya obtenidos debes ejecutar el endpoint Get Sample Tweets `/tweets`

El endpoint utilizado para encontrar los sentimientos es Get Tweet Sentiments All `/tweet/sentiment/{skip}/{limit}`, donde skip y limit son valores numéricos enteros que se deben pasar para extraer los sentimientos de un rango de tweets.

Por ejemplo para obtener los sentimientos de los primeros 100 tweets se debe pasar `skip=0` y `limit=100`


De la misma forma, para obtener las emociones de los tweets se debe mandar a llamar Get Tweet Emotions All `/tweet/emotions/{skip}/{limit}`

Cada endpoint actualiza los valores obtenidos en el documento respectivo del tweet.


## Resultados

De acuerdo con los resultados obtenidos de los servicios web de Meaning Cloud y ParallelDots se llegó a la conclusión de que los siguientes rasgos son los que llegarían a darnos información necesaria para generar un modelo de ML para predecir si un tweet es xenófobo o no.

| Rasgo | Valores |
| ----- | ------- |
| agreement | [AGREEMENT - DISAGREEMENT] |
| irony | [IRONIC - NONIRONIC] |
| subjectivity | [OBJECTIVE - SUBJECTIVE] |
| score_tag | [P+ - P - NEU - N - N+ - NONE ] |
| angry | [0 - 1] |
| bored | [0 - 1] |
| excited | [0 - 1] |
| fear | [0 - 1] |
| happy | [0 - 1] |
| sad | [0 - 1] |


Esto ya que una manera de detectar comentarios xenófobos es con el uso de cómo una persona describe cierta situación acerca de personas ajenas a su comunidad. Las emociones y sentimientos tienen un papel fundamental ya que el miedo es un sentimiento que se percibe de manera natural en los seres humanos ante una situación cercana. Si algo representa un peligro para una persona o una comunidad una manera de proyectarlo es mediante un lenguaje con tintes de miedo que suelen incluir sentimientos de negatividad.

Por esto es que se eligieron los rasgos descritos, con ayuda de la clasificación y valores en porcentaje se podría medir la polaridad de los tweets.


## Archivo resultado

Dentro del proyecto se encuentra el archivo `features.csv` con los rasgos y los valores obtenidos con la ayuda de los servicios web de Meaning Cloud y Parallel Dots.
