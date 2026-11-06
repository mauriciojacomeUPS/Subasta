import Pyro4

nombre = input("Cual es tu nombre? ")

ns = Pyro4.locateNS(host="localhost", port=9090)
uri = ns.lookup("subastas.central")
servidor = Pyro4.Proxy(uri)

print("\nConectado a la sala de subastas.")

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

    except ValueError:
        print("\nError: Introduce un numero valido para la puja.")
