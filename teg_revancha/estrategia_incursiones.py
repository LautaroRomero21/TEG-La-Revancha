"""Incursiones de un ejército para obtener tarjetas (IA Difícil).

Una conquista no siempre tiene como objetivo conservar terreno. Si el bot
todavía necesita una conquista para solicitar tarjeta, puede atacar una ficha
débil y ocuparla con UNA sola unidad, aun si otro jugador podrá recuperarla.
La guarnición principal queda protegida. No se inventan nuevas reglas.
"""

class IncursionPorTarjeta:
    def __init__(self,juego,estrategia,calcular_probabilidad):
        self.juego=juego
        self.estrategia=estrategia
        self.probabilidad=calcular_probabilidad

    def faltantes(self,jugador):
        """Conquistas propias que faltan para una tarjeta este turno; 0 si no aplica."""
        j=self.juego
        if (j.etapa!='hostilidades' or j.fase!='ATACAR'
                or jugador.idx!=j.turno_idx or jugador.eliminado
                or j.situacion==f'Descanso {jugador.color_nombre}'
                or jugador.idx in j.crisis_sin_tarjeta
                or j.sancion_tarjeta[jugador.idx]>0 or j.tarjeta_solicitada
                or len(jugador.tarjetas)>=5 or j.conquistas_colectivas>=2):
            return 0
        requerido=1 if jugador.canjes_realizados<3 else 2
        return max(0,requerido-j.conquistas_turno)

    def _segunda_conquista_viable(self,jugador,primero_origen,primero_destino,bajas):
        """No empezar a buscar una tarjeta de dos conquistas con un solo blanco."""
        j=self.juego
        for origen in j.paises_de(jugador.idx):
            # Tras la incursión solo sale una ficha del origen.
            soldados=j.ejercitos_de(origen,jugador.idx)
            if origen==primero_origen:
                soldados=max(1,int(soldados-bajas-1))
            if soldados<2:continue
            for destino in self.estrategia._frentes(origen,jugador):
                if destino==primero_destino or destino in j.condominios:continue
                if j.zona_para(destino):continue
                defensor=j.tablero[destino]['propietario']
                if defensor is None:continue
                defensa=j.ejercitos_de(destino,defensor)
                p,_=self.probabilidad(soldados,defensa,j.situacion)
                if p>=.78:return True
        return False

    def candidato(self,jugador):
        """Devuelve (puntuación, probabilidad, origen, destino, traslado=1).

        La pérdida de la nueva ficha es aceptable, no la pérdida del ejército
        de origen. La ventaja de una tarjeta se compara contra el coste de la
        incursión, la fuerza futura del rival y la seguridad del origen.
        """
        j=self.juego
        faltan=self.faltantes(jugador)
        if not faltan:return None
        contexto=self.estrategia.contexto(jugador)
        opciones=[]
        for origen in j.paises_de(jugador.idx):
            tropas=j.ejercitos_de(origen,jugador.idx)
            if tropas<3:continue
            # Una incursión desde un condominio no debe tomar tropas del socio.
            for destino in self.estrategia._frentes(origen,jugador):
                if destino in j.condominios or j.zona_para(destino):continue
                defensor=j.tablero[destino]['propietario']
                if defensor is None or defensor==jugador.idx:continue
                defensa=j.ejercitos_de(destino,defensor)
                prob,bajas=self.probabilidad(tropas,defensa,j.situacion)
                if prob<.85:continue
                origen_restante=max(1,int(tropas-bajas-1))
                if origen_restante<2:continue
                reserva=self.estrategia.turnos.reserva(
                    origen,jugador,excluir=(destino,))
                exposicion_nueva=self.estrategia.turnos.amenaza(
                    origen,jugador,guarnicion=origen_restante,excluir=(destino,))
                exposicion_previa=self.estrategia.turnos.amenaza(
                    origen,jugador,guarnicion=tropas,excluir=(destino,))
                exceso=max(0,reserva-origen_restante)
                if exceso>2:continue  # Nunca sacrificar el frente propio por una carta.
                if faltan>1 and not self._segunda_conquista_viable(
                        jugador,origen,destino,bajas):continue

                # La recuperación inmediata por otro color es esperable:
                # en una incursión se asume la pérdida de la ficha adelantada.
                riesgo_destino=self.estrategia.turnos.amenaza(
                    destino,jugador,guarnicion=1,excluir=(origen,))
                prob_recaptura=min(1.0,riesgo_destino/15)
                valor_tarjeta=14+min(9,len(jugador.tarjetas)*2.2)
                # Si hay otro jugador con muchas tarjetas que podría aprovechar
                # la conquista, moderamos la puntuación sin vetar la táctica.
                lider=max((len(j.tarjetas) for j in j.jugadores
                           if j.idx!=jugador.idx and not j.eliminado),default=0)
                valor=min(12,self.estrategia.valor_pais(
                    destino,jugador,contexto))  # valor territorial secundario
                puntuacion=(
                    10*prob + valor_tarjeta + .12*valor
                    - 1.8*bajas - .35*defensa
                    - 1.7*max(0,exposicion_nueva-exposicion_previa)
                    - 1.2*exceso
                    - 2.3*prob_recaptura
                    - (2.0 if lider>=4 and prob_recaptura>.6 else 0)
                )
                if puntuacion>12:
                    opciones.append((puntuacion,prob,origen,destino,1))
        return max(opciones) if opciones else None
