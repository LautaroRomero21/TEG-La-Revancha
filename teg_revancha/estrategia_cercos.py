"""Planificación de cerco para bots Difícil. No modifica reglas del TEG.

La comprobación de bloqueo sigue exclusivamente en JuegoTEG._pais_bloqueado:
- país no compartido, al menos tres vecinos, y no es el último del rival;
- TODOS los vecinos son de un único color, con DOS o más ejércitos cada uno.

Este módulo detecta oportunidades baratas, completa cercos con refuerzos o
reagrupamientos y procura no romperlos en ataques posteriores.
"""


class EstrategiaCerco:
    def __init__(self, juego, estrategia):
        self.juego = juego
        self.ia = estrategia

    def objetivos(self, jugador, incluir_completos=True):
        """Territorios enemigos rodeados en propiedad, con fichas pendientes.

        Se verifica TODO el vecindario; controlar solo algunas fronteras
        no significa poder bloquear un país. No se presuponen refuerzos
        que no estén disponibles ni se examinan objetivos secretos rivales.
        """
        j = self.juego
        actor = jugador.idx
        for pais, datos in j.tablero.items():
            victima = datos['propietario']
            vecinos = datos['fronteras']
            if (victima is None or victima == actor or pais in j.condominios
                    or len(vecinos) < 3 or len(j.paises_de(victima)) <= 1
                    or j.zona_para(pais)):
                continue
            if any(n in j.condominios or not j.es_propietario(n, actor)
                   for n in vecinos):
                continue
            faltantes = [(n, 2 - j.ejercitos_de(n, actor))
                         for n in vecinos if j.ejercitos_de(n, actor) < 2]
            if faltantes or incluir_completos:
                yield {'pais':pais, 'victima':victima, 'vecinos':tuple(vecinos),
                       'faltantes':tuple(faltantes),
                       'costo':sum(faltan for _, faltan in faltantes),
                       'completo':not faltantes}

    def reserva(self, origen, jugador, destino_atacado=None):
        """Reserva de 2 en una frontera que mantiene o prepara un cerco.

        Si se está conquistando el propio país rodeado, no hay motivo para
        conservar ese bloqueo: la conquista elimina el blanco del cerco.
        """
        if origen in self.juego.condominios:
            return 1
        for objetivo in self.objetivos(jugador):
            if (origen in objetivo['vecinos'] and
                    objetivo['pais'] != destino_atacado and
                    objetivo['costo'] <= 2):
                return 2
        return 1

    def compromete(self, origen, destino, jugador, bajas=0, traslado=1):
        """True si un ataque puede dejar bajo 2 a un guardia importante."""
        reserva = self.reserva(origen, jugador, destino_atacado=destino)
        if reserva < 2:
            return False
        restante = self.juego.ejercitos_de(origen,jugador.idx)-bajas-traslado
        return restante < reserva

    def _prioridad(self, objetivo, jugador):
        j = self.juego
        tropas = j.tablero[objetivo['pais']]['ejercitos']
        contexto = self.ia.contexto(jugador)
        rival = objetivo['victima']
        lider = max(contexto['paises'].values(),default=0)
        # Evitar bloquear un objetivo con pocas tropas si perderíamos la
        # carrera a 45 países por perseguir una barrera secundaria.
        if (lider >= 43 and rival not in
                [i for i, valor in contexto['paises'].items() if valor >= 43]):
            return -100.0
        valor = (12 + min(11,tropas*.9) + min(6,len(objetivo['vecinos']))*.7
                 - objetivo['costo']*3.2)
        if rival in [i for i, v in contexto['paises'].items() if v >= 38]:
            valor += 12
        # Un solo refuerzo para completar un bloqueo vale especialmente.
        if objetivo['costo']==1:
            valor += 5
        return valor

    def _fondos_permiten_cerco(self, objetivo):
        """Evitar planificar cercos imposibles por los bonos continentales."""
        j=self.juego
        por_continente={}
        for pais, faltan in objetivo['faltantes']:
            if j._pais_bloqueado(pais):
                return False
            cont=j.tablero[pais]['continente']
            por_continente[cont]=por_continente.get(cont,0)+faltan
        libre=j.ejercitos_a_colocar-sum(j.refuerzos_continente.values())
        necesario_libre=sum(max(0, n-j.refuerzos_continente.get(cont,0))
                            for cont,n in por_continente.items())
        return objetivo['costo']<=j.ejercitos_a_colocar and necesario_libre<=libre

    def refuerzo(self, jugador, paises_validos):
        """(país vecino, cantidad, blanco) para completar un cerco económico.

        Sólo actúa si quedan tropas y si el cerco se puede terminar con los
        fondos que restan. No malgasta cinco ejércitos intentando rodear
        un objetivo donde aún faltan cinco en otras fronteras.
        """
        j=self.juego
        permitidos=set(paises_validos)
        opciones=[]
        for objetivo in self.objetivos(jugador,incluir_completos=False):
            if objetivo['costo']>3 or not self._fondos_permiten_cerco(objetivo):
                continue
            puntos=self._prioridad(objetivo,jugador)
            if puntos<15:
                continue
            for pais,faltan in objetivo['faltantes']:
                if pais not in permitidos:
                    continue
                cont=j.tablero[pais]['continente']
                pool=j.refuerzos_continente.get(cont,0)
                libres=j.ejercitos_a_colocar-sum(j.refuerzos_continente.values())
                disponible=min(j.ejercitos_a_colocar,pool if pool else libres)
                if disponible<faltan:
                    continue
                opciones.append((puntos, -objetivo['costo'],pais,
                                faltan,objetivo['pais']))
        if not opciones:
            return None
        _,_,pais,cuantos,objetivo=max(opciones)
        return pais,cuantos,objetivo

    def reagrupe(self, jugador):
        """Trasladar solo lo necesario de una retaguardia a un guardia con 1.

        Respeta las unidades recibidas durante el turno y las reservas de
        todos los demás cercos. Retorna (origen, destino, cantidad, blanco).
        """
        j=self.juego
        opciones=[]
        for objetivo in self.objetivos(jugador,incluir_completos=False):
            if objetivo['costo']>2 or self._prioridad(objetivo,jugador)<15:
                continue
            for destino,faltan in objetivo['faltantes']:
                for origen in j.tablero[destino]['fronteras']:
                    if (not j.es_propietario(origen,jugador.idx)
                            or origen in j.condominios or origen==destino):
                        continue
                    soldados=j.ejercitos_de(origen,jugador.idx)
                    recibidos=j.reagrupados_recibidos.get(origen,0)
                    reserva=max(self.reserva(origen,jugador),
                                self.ia.turnos.reserva(origen,jugador))
                    if soldados-reserva-recibidos<faltan:
                        continue
                    # Dejar una ficha libre no sirve si a la vez otro guardia
                    # de ese mismo cerco baja a 1.
                    puntos=self._prioridad(objetivo,jugador)
                    opciones.append((puntos, soldados-reserva-recibidos,
                                     origen,destino,faltan,objetivo['pais']))
        return max(opciones) [2:] if opciones else None

    def escape(self, jugador, probabilidad):
        """Romper un encierro propio con un ataque razonable contra el vecino débil.

        Aunque la incorporación esté bloqueada, el reglamento todavía permite
        atacar desde el territorio si quedan tropas suficientes.
        """
        j=self.juego
        opciones=[]
        for origen in j.paises_de(jugador.idx):
            if not j._pais_bloqueado(origen):
                continue
            tropas=j.ejercitos_de(origen,jugador.idx)
            if tropas<3:
                continue
            for destino in self.ia._frentes(origen,jugador):
                if destino in j.condominios:
                    continue
                defensa=j.tablero[destino]['ejercitos']
                p, bajas=probabilidad(tropas,defensa,j.situacion)
                if p<.58:
                    continue
                valor=self.ia.valor_pais(destino,jugador,
                                         self.ia.contexto(jugador))
                score=18+p*12+bajas*(-1.5)+valor*.25
                opciones.append((score,p,origen,destino))
        return max(opciones) if opciones else None
