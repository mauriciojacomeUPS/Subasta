import Pyro4
import threading
import time


nombre = input("Cual es tu nombre? ")

ns = Pyro4.locateNS(host="localhost", port=9090)
uri = ns.lookup("subastas.central")
servidor = Pyro4.Proxy(uri)
servidor.registrar_cliente(nombre)

print("\nConectado a la sala de subastas.")


# NUEVO: consulta cada 2 segundos sin interrumpir el menu original.
def actualizar_pujas():
    # Cada hilo usa su propio Proxy para no compartir la conexion.
    conexion = Pyro4.Proxy(uri)
    ultimo_precio, _, _ = conexion.get_datos_puja()

    while True:
        time.sleep(2)
        try:
            precio, postor, finalizo = conexion.get_datos_puja()
            if precio != ultimo_precio:
                print(f"\n[ACTUALIZACION] {postor} ofrece ${precio:.2f}")
                ultimo_precio = precio

            if finalizo:
                print("\n[AVISO] Subasta finalizada.")
                print(conexion.get_consultar())
                break
        except Pyro4.errors.CommunicationError:
            print("\n[AVISO] No se pudo consultar al servidor.")
            break

    conexion._pyroRelease()


hilo = threading.Thread(target=actualizar_pujas, daemon=True)
hilo.start()

while True:
    try:
        # Consultamos el estado actual directamente al inicio del bucle
        estado = servidor.get_consultar()

        # Eliminamos las lineas decorativas de arriba y abajo
        print(estado)

        # Si el estado indica que ya finalizo, rompemos el bucle del cliente
        if "FINALIZADO" in estado:
            print("La subasta ha concluido. Gracias por participar.")
            break

        print("\n1._ Enviar una Puja")
        print("2._ Actualizar / Consultar estado")
        print("Escribe /salir para abandonar la sala")

        dato = input("Selecciona una opcion: ").strip()

        if dato == "/salir":
            print("Saliendo...")
            break

        if dato == "1":
            nueva_puja = float(input("Introduce el monto de tu puja: "))
            respuesta = servidor.ofertar_puja(nombre, nueva_puja)
            print(f"\n[SERVIDOR]: {respuesta}")

            # Si la respuesta avisa que ya termino, mostramos el ganador y cerramos
            if "SUBASTA TERMINADA" in respuesta:
                print(servidor.get_consultar())
                break

        elif dato == "2":
            # Al elegir esta opcion, el bucle vuelve a iniciar y actualiza el estado automaticamente
            continue

        else:
            print("\nOpcion no valida. Intenta de nuevo.")

    except ValueError as error:
        print(f"\nError: {error}")
    except Pyro4.errors.CommunicationError:
        print("\nError: No se pudo conectar con el servidor.")
        break
