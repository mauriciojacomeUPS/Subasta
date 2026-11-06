# Caso integrador: subasta distribuida con Pyro4

Esta version conserva el flujo original: producto aleatorio, puja inicial aleatoria, 60 segundos, menu 1/2, `/salir`, `get_consultar()` y `ofertar_puja()`. Los cambios estan comentados y son solo para cubrir los requisitos de la guia.

## Requisitos

1. **Name Server:** registro automatico con `ns.register("subastas.central", uri)`.
2. **Ofertas:** valida monto mayor, plazo y evita condiciones de carrera con `threading.Lock()`.
3. **Actualizacion:** un hilo en cada cliente hace polling cada 2 segundos y avisa cuando cambia la puja; el cliente se registra al conectarse.
4. **Fallos:** las entradas invalidas lanzan `ValueError`, que el cliente captura sin cerrar el servidor.

El servidor imprime el ganador automaticamente al finalizar los 60 segundos; los clientes tambien reciben un aviso. Si el cliente esta detenido en `input()`, el aviso aparece pero el menu continuara al introducir una opcion.

## Ejecutar con venv en Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
git clone https://github.com/mauriciojacomeUPS/Subasta.git
cd Subasta
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Abrir otras 3 terminales en la carpeta del proyecto y activar en cada una `source .venv/bin/activate`. Iniciar en este orden:

```bash
# Terminal 1
python -m Pyro4.naming -n localhost
# Terminal 2
python subasta_server.py
# Terminal 3
python subasta_client.py
# Terminal 4
python subasta_client.py
```

La subasta empieza cuando se ejecuta el servidor, no cuando entra el primer cliente. Si arrancas mas clientes, veran el mismo precio. Se recomienda Python 3.10 por compatibilidad de Pyro4.
