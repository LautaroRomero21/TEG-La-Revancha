"""Plan de remontada exclusivo de los bots en dificultad Difícil.

Cuando un bot se queda con pocos países, su prioridad pasa a conseguir la(s)
conquista(s) necesaria(s) para solicitar una tarjeta. No altera las reglas:
- Hasta el segundo canje: una conquista propia por turno.
- Desde el tercer canje: dos conquistas propias (o dos colectivas).
- Crisis, sanciones, límite de cinco cartas y descansos siguen vigentes.

La estrategia busca rivales accesibles usando probabilidades de dados reales.
Evita ataques desesperados con probabilidades demasiado bajas y no necesita
conocer las misiones secretas de los rivales.
"""


class PlanRemontada:
    def __init__(self, juego, estrategia, probabilidad):
        self.juego = juego
        self.estrategia = estrategia
        self.probabilidad = probabilidad

    def estado(self, jugador):
        juego = self.juego
        propios = len(juego.paises_exclusivos(jugador.idx))
        rivales = [len(juego.paises_exclusivos(j.idx)) for j in juego.jugadores
                   if j.idx != jugador.idx and not j.eliminado]
        lider = max(rivales, default=0)
        # No basta con estar segundo: hay que tener verdaderamente pocos
        # territorios, o una desventaja sustancial frente a otro jugador.
        limite = max(4, min(10, int(lider * .38)))
        critico = propios <= limite and (propios <= 5 or lider >= propios * 2.2)
        umbral = 1 if jugador.canjes_realizados < 3 else 2
        faltan = max(0, umbral - juego.conquistas_turno)
        # El reglamento también admite dos conquistas colectivas.
        if juego.conquistas_colectivas >= 2:
            faltan = 0
        habilitado = (
            juego.etapa == 'hostilidades'
            and not jugador.eliminado
            and juego.situacion != f'Descanso {jugador.color_nombre}'
            and jugador.idx not in juego.crisis_sin_tarjeta
            and juego.sancion_tarjeta[jugador.idx] == 0
            and not juego.tarjeta_solicitada
            and len(jugador.tarjetas) < 5
            and faltan > 0
        )
        return {
            'critico': critico,
            'buscar_tarjeta': bool(critico and habilitado),
            'faltan': faltan,
            'paises': propios,
            'lider': lider,
        }

    def _objetivos_asequibles(self, origen, jugador):
        juego = self.juego
        for destino in self.estrategia._frentes(origen, jugador):
            if destino in juego.condominios:
                continue  # La conquista de condominios tiene reglas especiales.
            defensor = juego.tablero[destino]['propietario']
            if defensor is None or defensor == jugador.idx:
                continue
            yield destino, juego.ejercitos_de(destino, defensor)

    def _dos_opciones(self, origen, jugador):
        """Bonificación discreta si hay más de una conquista débil disponible."""
        return sum(1 for _, b in self._objetivos_asequibles(origen, jugador)
                   if b <= 3) >= 2

    def plan_refuerzo(self, jugador, paises):
        """Devuelve (origen, cantidad, objetivo) o None.

        Selecciona un país con un blanco accesible; busca la MENOR incorporación
        que dé una probabilidad aceptable, en vez de apilar todos los refuerzos
        ante un enemigo inconquistable. Se recalcula tras cada incorporación.
        """
        juego = self.juego
        estado = self.estado(jugador)
        if not estado['buscar_tarjeta'] or not paises:
            return None
        libres = juego.ejercitos_a_colocar - sum(juego.refuerzos_continente.values())
        mejores = []
        for origen in paises:
            pool = juego.refuerzos_continente.get(
                juego.tablero[origen]['continente'], 0)
            maximo = min(juego.ejercitos_a_colocar, pool if pool else libres, 10)
            if maximo < 1:
                continue
            tropas = juego.ejercitos_de(origen, jugador.idx)
            objetivo_doble = estado['faltan'] >= 2 and self._dos_opciones(origen, jugador)
            for destino, defensores in self._objetivos_asequibles(origen, jugador):
                if defensores > tropas + maximo + 7:
                    continue  # No consumir toda la ronda en un frente imposible.
                p_actual = self.probabilidad(tropas, defensores, juego.situacion)[0]
                if p_actual >= .78:
                    continue  # Ya puede conquistar: reforzar otro frente.
                p_final = self.probabilidad(tropas + maximo, defensores, juego.situacion)[0]
                if p_final < .48 or p_final - p_actual < .04:
                    continue
                # Procurar una conquista razonablemente segura, sin comprar
                # tropas de más si ya alcanzamos esa probabilidad.
                meta = .73 if estado['paises'] > 3 else .65
                cantidad = maximo
                prob_alcanzada = p_final
                for n in range(1, maximo + 1):
                    pn = self.probabilidad(tropas + n, defensores, juego.situacion)[0]
                    if pn >= meta:
                        cantidad, prob_alcanzada = n, pn
                        break
                # Priorizar blancos baratos, de bajo coste en tropas; sumar
                # incentivo para dos capturas si el canje exige dos países.
                valor = self.estrategia.valor_pais(
                    destino, jugador, self.estrategia.contexto(jugador))
                puntaje = (
                    27 * prob_alcanzada + 18 * (prob_alcanzada - p_actual)
                    - 1.3 * cantidad - .35 * defensores
                    + .11 * valor + (5 if objetivo_doble else 0)
                )
                mejores.append((puntaje, origen, cantidad, destino))
        if not mejores:
            return None
        _, origen, cantidad, destino = max(mejores)
        return origen, cantidad, destino

    def candidato_ataque(self, jugador):
        """Elige un ataque para conseguir una tarjeta sin suicidar el ejército.

        En una remontada se admite algo más de riesgo que en el modo Difícil
        general, pero nunca se ataca si las probabilidades son insignificantes.
        El atacante sigue reevaluando la situación después de cada tirada.
        """
        juego = self.juego
        estado = self.estado(jugador)
        if not estado['buscar_tarjeta']:
            return None
        ctx = self.estrategia.contexto(jugador)
        fraccion = self.estrategia.turnos.ventana(jugador)['fraccion_pendiente']
        umbral = (.53 if estado['paises'] <= 3 else .61) + .035 * fraccion
        opciones = []
        for origen in juego.paises_de(jugador.idx):
            tropas = juego.ejercitos_de(origen, jugador.idx)
            if tropas < 2:
                continue
            doble = estado['faltan'] >= 2 and self._dos_opciones(origen, jugador)
            for destino, defensa in self._objetivos_asequibles(origen, jugador):
                p, perdidas = self.probabilidad(tropas, defensa, juego.situacion)
                if p < umbral:
                    continue
                # Se conservan ejércitos propios en el origen al conquistar.
                quedan = max(1, tropas - perdidas - 1)
                presion = self.estrategia.turnos.amenaza(
                    origen, jugador, guarnicion=quedan, excluir=(destino,))
                valor = self.estrategia.valor_pais(destino, jugador, ctx)
                puntaje = (
                    p * 27 - 1.5 * perdidas
                    - min(16, presion) * (.8 + .25 * fraccion)
                    - .30 * defensa + .16 * valor
                    + (4 if doble else 0)
                )
                # No terminar todo o nada por el simple hecho de conseguir
                # una carta: exigir utilidad mínima después de los riesgos.
                if puntaje > 0:
                    opciones.append((puntaje, p, origen, destino))
        return max(opciones) if opciones else None
