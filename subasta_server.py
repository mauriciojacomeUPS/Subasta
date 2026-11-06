import Pyro4
import random
import time
import threading
import math


@Pyro4.expose
class SubastaServer:
    def __init__(self):
        products = ["Panda", "Jaron Japones", "PS5", "GTA6"]
        self.producto = random.choice(products)

        # Asignamos un valor inicial aleatorio para la puja (Entre 50 y 200)
        self.puja_mas_alta = float(random.randint(50, 200))
        self.mejor_postor = "Nadie"

        self.inicio_subasta = time.time()
        self.duracion_total = 60  # Duracion de la subasta en segundos

        # Cambios necesarios para el caso: concurrencia y clientes registrados.
        self.bloqueo = threading.Lock()
        self.clientes = []

        # Anuncia al ganador automaticamente a los 60 segundos.
        threading.Timer(self.duracion_total, self.mostrar_ganador).start()

    def _obtener_tiempo_restante(self):
        tiempo_transcurrido = time.time() - self.inicio_subasta
        tiempo_restante = int(self.duracion_total - tiempo_transcurrido)
        return max(0, tiempo_restante)

    def get_product(self):
        return self.producto

    def registrar_cliente(self, nombre):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("Ingresa un nombre valido.")
        with self.bloqueo:
            if nombre not in self.clientes:
                self.clientes.append(nombre)
        return "Cliente registrado."

    def get_datos_puja(self):
        # Datos cortos para que el cliente detecte cambios por polling.
        with self.bloqueo:
            finalizo = self._obtener_tiempo_restante() == 0
            return self.puja_mas_alta, self.mejor_postor, finalizo

    def get_consultar(self):
        with self.bloqueo:
            if self._obtener_tiempo_restante() == 0:
                resultado = "No hubo ganador."
                if self.mejor_postor != "Nadie":
                    resultado = f"Ganador: {self.mejor_postor}"
                return (
                    f"\nFINALIZADO\nProducto: {self.producto}\n"
                    f"{resultado}\nPuja final: ${self.puja_mas_alta:.2f}"
                )

            return (
                f"\nProducto: {self.producto}\n"
                f"Puja mas alta: ${self.puja_mas_alta:.2f}\n"
                f"Mejor postor: {self.mejor_postor}\n"
                f"Tiempo restante: {self._obtener_tiempo_restante()} segundos"
            )

    def ofertar_puja(self, nombre, nueva_puja):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("Nombre invalido.")
        if not isinstance(nueva_puja, (int, float)):
            raise ValueError("Monto invalido.")
        if not math.isfinite(nueva_puja):
            raise ValueError("La puja debe ser un numero finito.")

        # El bloqueo evita condiciones de carrera entre clientes.
        with self.bloqueo:
            if self._obtener_tiempo_restante() == 0:
                return "SUBASTA TERMINADA"

            if nueva_puja <= self.puja_mas_alta:
                raise ValueError("La puja debe superar el monto actual.")

            self.puja_mas_alta = float(nueva_puja)
            self.mejor_postor = nombre
            print(f"Nueva puja: {nombre} - ${nueva_puja:.2f}")
            return "Puja aceptada."

    def mostrar_ganador(self):
        with self.bloqueo:
            print("\n===== SUBASTA FINALIZADA =====")
            print(f"Producto: {self.producto}")
            if self.mejor_postor == "Nadie":
                print("No hubo ofertas. No hay ganador.")
            else:
                print(f"Ganador: {self.mejor_postor}")
                print(f"Puja ganadora: ${self.puja_mas_alta:.2f}")
            print("==============================\n")


if __name__ == "__main__":
    servidor = SubastaServer()
    daemon = Pyro4.Daemon(host="localhost")
    ns = Pyro4.locateNS(host="localhost", port=9090)
    uri = daemon.register(servidor)
    ns.register("subastas.central", uri)

    print("Servidor de subastas iniciado.")
    print(f"Producto: {servidor.producto}")
    print(f"Puja inicial: ${servidor.puja_mas_alta:.2f}")
    print("Duracion: 60 segundos")
    daemon.requestLoop()
