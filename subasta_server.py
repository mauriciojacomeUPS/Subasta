import math
import random
import threading
import time

import Pyro4


@Pyro4.expose
class SubastaServer:
    def __init__(self):
        products = ["Panda", "Jaron Japones", "PS5", "GTA6"]
        self.producto = random.choice(products)

        # Precio inicial aleatorio entre 50 y 200.
        self.puja_mas_alta = float(random.randint(50, 200))
        self.mejor_postor = "Nadie"

        self.inicio_subasta = time.time()
        self.duracion_total = 60
        self.finalizada = False
        self.bloqueo = threading.Lock()

        # Al pasar 60 segundos, el servidor anuncia al ganador.
        temporizador = threading.Timer(
            self.duracion_total, self.finalizar_subasta
        )
        temporizador.daemon = True
        temporizador.start()

    def _obtener_tiempo_restante(self):
        transcurrido = time.time() - self.inicio_subasta
        return max(0, int(self.duracion_total - transcurrido))

    def _termino_el_tiempo(self):
        return time.time() - self.inicio_subasta >= self.duracion_total

    def finalizar_subasta(self):
        # El bloqueo evita leer un ganador mientras se registra una oferta.
        with self.bloqueo:
            if self.finalizada:
                return
            self.finalizada = True

            print("\n===== SUBASTA FINALIZADA =====")
            print(f"Producto: {self.producto}")
            if self.mejor_postor == "Nadie":
                print("No hubo ganador: nadie realizo una oferta.")
            else:
                print(f"GANADOR: {self.mejor_postor}")
                print(f"PUJA GANADORA: ${self.puja_mas_alta:.2f}")
            print("=============================\n")

    def get_product(self):
        return self.producto

    def get_consultar(self):
        with self.bloqueo:
            termino = self.finalizada or self._termino_el_tiempo()
            estado = "FINALIZADO" if termino else "EN CURSO"

            informacion = (
                f"\nProducto: {self.producto}\n"
                f"Puja mas alta: ${self.puja_mas_alta:.2f}\n"
                f"Mejor postor: {self.mejor_postor}\n"
                f"Tiempo restante: {self._obtener_tiempo_restante()} s\n"
                f"Estado: {estado}"
            )
            if termino:
                if self.mejor_postor == "Nadie":
                    informacion += "\nRESULTADO: No hubo ganador."
                else:
                    informacion += (
                        f"\nGANADOR: {self.mejor_postor}"
                        f"\nPRECIO FINAL: ${self.puja_mas_alta:.2f}"
                    )
            return informacion

    def ofertar_puja(self, nombre, nueva_puja):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("Debes indicar tu nombre.")

        try:
            nueva_puja = float(nueva_puja)
        except (TypeError, ValueError):
            raise ValueError("La puja debe ser un numero.") from None

        if not math.isfinite(nueva_puja):
            raise ValueError("La puja debe ser un numero valido.")

        # Solo un cliente puede verificar y actualizar la puja a la vez.
        with self.bloqueo:
            if self.finalizada or self._termino_el_tiempo():
                return "SUBASTA TERMINADA. No se aceptan mas ofertas."

            if nueva_puja <= self.puja_mas_alta:
                raise ValueError(
                    f"La puja debe superar ${self.puja_mas_alta:.2f}."
                )

            self.puja_mas_alta = nueva_puja
            self.mejor_postor = nombre.strip()
            print(f"Nueva puja: {self.mejor_postor} - ${nueva_puja:.2f}")
            return f"Puja aceptada: ${nueva_puja:.2f}."


if __name__ == "__main__":
    servidor = SubastaServer()
    ns = Pyro4.locateNS(host="localhost", port=9090)

    with Pyro4.Daemon(host="localhost") as daemon:
        uri = daemon.register(servidor)
        ns.register("subastas.central", uri)

        print("Servidor registrado como: subastas.central")
        print(f"Producto: {servidor.producto}")
        print(f"Precio inicial: ${servidor.puja_mas_alta:.2f}")
        print("Duracion: 60 segundos")
        daemon.requestLoop()
