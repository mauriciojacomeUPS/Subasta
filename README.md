# Subasta con Pyro4

Proyecto de subastas distribuido. Se conserva el cliente original casi linea por linea y los nombres de los metodos del servidor: `SubastaServer`, `get_product`, `get_consultar`, `ofertar_puja`. El fragmento del servidor compartido en el chat estaba cortado despues de `get_product`, por lo que los metodos siguientes se completaron sin disponer de su codigo original.

## Cambios minimos

- Corregido `_init_` a `__init__` para que Python inicialice el servidor.
- Se agrego `threading.Timer` para imprimir quien gano al cumplirse los 60 segundos.
- Se agrego `threading.Lock` para proteger las ofertas simultaneas.
- Al finalizar, `get_consultar()` muestra el ganador y la puja final.
- En el cliente solo se agrego una consulta del resultado si una oferta llega al final de la subasta.

## Ejecutar en Ubuntu

```bash
sudo apt install python3 python3-venv python3-pip -y
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En tres o cuatro terminales dentro de la carpeta del proyecto, activar `.venv` y ejecutar, en este orden:

```bash
python -m Pyro4.naming -n localhost
python subasta_server.py
python subasta_client.py
python subasta_client.py
```

La subasta dura 60 segundos desde que se inicia el servidor. Para ver el resultado desde un cliente que esta esperando un comando, seleccionar la opcion 2.

Nota: esta implementacion conserva el estilo educativo original. No guarda datos despues de cerrar el servidor.
