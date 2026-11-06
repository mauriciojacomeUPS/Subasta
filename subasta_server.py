import Pyro4
import random
import time
import threading


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

        # NUEVO: protege la puja si dos clientes ofertan al mismo tiempo.
        self.bloqueo = threading.Lock()

        # NUEVO: al terminar el tiempo mostramos el ganador en el servidor.
        threading.Timer(self.duracion_total, self.mostrar_ganador).start()

    def _obtener_tiempo_restante(self):
        tiempo_transcurrido = time.time() - self.inicio_subasta
        tiempo_restante = int(self.duracion_total - tiempo_transcurrido)
        return max(0, tiempo_restante)

    def get_product(self):
        return self.producto

    def get_consultar(self):
        with self.bloqueo:
            if time.time() - self.inicio_subasta >= self.duracion_total:
                return (
                    f"\nFINALIZADO\nProducto: {self.producto}\n"
                    f"Ganador: {self.mejor_postor}\n"
                    f"Puja final: ${self.puja_mas_alta:.2f}"
                )

            return (
                f"\nProducto: {self.producto}\n"
                f"Puja mas alta: ${self.puja_mas_alta:.2f}\n"
                f"Mejor postor: {self.mejor_postor}\n"
                f"Tiempo restante: {self._obtener_tiempo_restante()} segundos"
            )

    def ofertar_puja(self, nombre, nueva_puja):
        # NUEVO: validar el tipo sin detener el servicio.
        if not isinstance(nueva_puja, (int, float)):
            raise ValueError("Monto invalido.")

        with self.bloqueo:
            if time.time() - self.inicio_subasta >= self.duracion_total:
                return "SUBASTA TERMINADA"

            if nueva_puja <= self.puja_mas_alta:
                return "Tu puja debe superar la puja mas alta actual."

            self.puja_mas_alta = nueva_puja
            self.mejor_postor = nombre
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
