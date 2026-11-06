import Pyro4


nombre = input("Cual es tu nombre? ")

ns = Pyro4.locateNS(host="localhost", port=9090)
uri = ns.lookup("subastas.central")
servidor = Pyro4.Proxy(uri)

print("\nConectado a la sala de subastas.")

while True:
    try:
        # El servidor entrega la informacion mas reciente.
        estado = servidor.get_consultar()
        print(estado)

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

            if "SUBASTA TERMINADA" in respuesta:
                # Consultar una vez mas para mostrar el ganador.
                print(servidor.get_consultar())
                break

        elif dato == "2":
            continue

        else:
            print("\nOpcion no valida. Intenta de nuevo.")

    except ValueError as error:
        print(f"\nError: {error}")
    except Pyro4.errors.CommunicationError as error:
        print(f"\nSe perdio la conexion con el servidor: {error}")
        break
