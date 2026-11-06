# Sistema de subastas Pyro4 (modificaciones minimas)

Mantiene `SubastaServer`, `get_product`, `get_consultar`, `ofertar_puja` y el registro `subastas.central`.

## Cambios respecto al original

1. `__init__` correcto (dos guiones bajos a cada lado).
2. El servidor imprime el ganador automaticamente al cumplirse 60 segundos.
3. `get_consultar()` incluye `FINALIZADO`, el ganador y el precio final.
4. `threading.Lock()` evita que dos clientes cambien el precio simultaneamente.
5. En el cliente, al terminar al intentar ofertar, se vuelve a consultar el resultado.

## Ubuntu (en la carpeta de los archivos)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Abrir terminales nuevas y activar el entorno (`source .venv/bin/activate`) en cada una:

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

Ingresar un nombre diferente en cada cliente. Usar opcion 1 para ofertar y 2 para actualizar; la subasta termina a los 60 segundos de arrancar el servidor. El temporizador imprime el resultado en el servidor automaticamente, y los clientes lo ven al consultar de nuevo.

Para demostrar concurrencia, lanzar dos ofertas en clientes diferentes a la vez. Solo se acepta la que corresponda al precio mas alto en el momento de cada solicitud.
