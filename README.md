# AI-103 Lab: agente de reclamos por envíos dañados

Laboratorio práctico para AI-103: un agente en Azure AI Foundry que revisa reclamos de paquetes dañados y recomienda reembolso, reemplazo o rechazo. El detalle del caso y las fases está en [ai103-damaged-shipment-claims-agent.md](ai103-damaged-shipment-claims-agent.md).

## Requisitos

- [uv](https://docs.astral.sh/uv/) (gestiona Python y las dependencias)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli), con acceso al proyecto de Azure AI Foundry

## Instalación

```sh
uv sync
```

Esto crea `.venv/` con Python 3.14 (fijado en `.python-version`) e instala las versiones exactas de `uv.lock`. No hace falta activar el entorno.

## Configuración

1. Crea un archivo `.env` en la raíz con:

   ```sh
   PROJECT_ENDPOINT=<endpoint del proyecto de AI Foundry>
   SMALL_MODEL_DEPLOYMENT_NAME=<nombre del deployment del modelo pequeño>
   LARGE_MODEL_DEPLOYMENT_NAME=<nombre del deployment del modelo grande>
   ```

   `.env` está en `.gitignore`; no lo subas.

2. Inicia sesión en Azure (la app usa `DefaultAzureCredential`):

   ```sh
   az login
   ```

## Ejecutar

```sh
uv run app.py
```

## Dependencias

- Agregar un paquete: `uv add <paquete>`
- Quitar un paquete: `uv remove <paquete>`
- Actualizar todo dentro de los rangos de `pyproject.toml`: `uv lock --upgrade && uv sync`

Sube a git tanto `pyproject.toml` como `uv.lock`.
