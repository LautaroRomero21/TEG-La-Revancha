"""Lectura táctica del orden de turnos para la IA Difícil.

La ronda tiene dos barreras: todos incorporan, luego atacan uno por uno.
El primer jugador rota después de cada ronda. Esta clase estima la exposición
ante jugadores que actúan ANTES de la próxima oportunidad de respuesta.

No consulta las misiones secretas de rivales ni modifica el motor de reglas.
"""

class LecturaDeTurnos:
    def __init__(self,juego):
        self.juego=juego

    def ventana(self,jugador):
        """Actores posteriores en esta ronda y anteriores en la siguiente.

        Los de la primera lista pueden responder más pronto; los de la segunda
        tendrán refuerzos adicionales antes de que este bot vuelva a atacar.
        Durante la incorporación/preparación, los posteriores todavía pueden
        observar nuestra colocación y concentrar refuerzos.
        """
        j=self.juego
        orden=[i for i in j.orden_ronda if not j.jugadores[i].eliminado]
        if jugador.idx not in orden:
            return {'posicion':0,'restantes':[],'siguiente':[],
                    'fraccion_pendiente':0.0,'preparacion':False}
        pos=orden.index(jugador.idx)
        restantes=orden[pos+1:]
        siguiente_orden=orden[1:]+orden[:1] if len(orden)>1 else orden
        siguiente=siguiente_orden[:siguiente_orden.index(jugador.idx)]
        preparacion=j.etapa=='preparacion'
        return {'posicion':pos,'restantes':restantes,'siguiente':siguiente,
                'fraccion_pendiente':len(restantes)/max(1,len(orden)-1),
                'preparacion':preparacion}

    def _puede_reaccionar(self,origen,destino,atacante,defensor):
        """Valida situación y pactos con el propietario simulado del destino.

        En evaluación de conquista, el tablero aún atribuye el destino al
        defensor anterior: por eso se usa el defensor hipotético explícito.
        """
        j=self.juego
        if atacante==defensor or atacante is None:return False
        if j.situacion==f'Descanso {j.jugadores[atacante].color_nombre}':
            return False
        ca=j.tablero[origen]['continente']
        cb=j.tablero[destino]['continente']
        if j.situacion=='Fronteras abiertas' and ca==cb:return False
        if j.situacion=='Fronteras cerradas' and ca!=cb:return False
        if j._prohibido_por_pacto(atacante,defensor,origen,destino):
            return False
        return True

    def amenaza(self,pais,jugador,guarnicion=None,excluir=(),colocacion=False):
        """Exposición estimada según las fuerzas vecinas y el orden de acción.

        No es una predicción cierta: considera la fuerza militar visible,
        una reserva plausible de refuerzos para adversarios que aún colocarán,
        la secuencia real de turnos y los tratados. La próxima ronda pesa
        menos porque el tablero puede cambiar antes de entonces.
        """
        j=self.juego
        v=self.ventana(jugador)
        g=j.ejercitos_de(pais,jugador.idx) if guarnicion is None else guarnicion
        total=0.0
        maxima=0.0
        for q in j.tablero[pais]['fronteras']:
            if q in excluir:continue
            enemigo=j.tablero[q]['propietario']
            if enemigo is None or j.es_propietario(q,jugador.idx):continue
            if not self._puede_reaccionar(q,pais,enemigo,jugador.idx):continue
            tropas=j.ejercitos_de(q,enemigo)
            if tropas<=1 and enemigo not in v['restantes'] and enemigo not in v['siguiente']:
                continue
            if enemigo in v['restantes']:
                # Durante preparación/incorporación todavía puede colocar
                # tropas; durante ataques ya no puede recibir refuerzos.
                fondo=3.0 if colocacion else 0.0
                ponderacion=1.25
            elif enemigo in v['siguiente']:
                fondo=2.0 if colocacion else 1.5
                ponderacion=.55
            else:
                fondo=0.0
                ponderacion=.20
            fuerzas=tropas+fondo
            # No atacarían exitosamente con un único ejército.
            if fuerzas<2:continue
            superioridad=max(0.0,fuerzas-max(1,g)+1.0)
            amenaza=ponderacion*(superioridad+min(5.0,fuerzas*.18))
            maxima=max(maxima,amenaza)
            total+=amenaza
        return maxima+max(0.0,total-maxima)*.25

    def reserva(self,pais,jugador,excluir=(),colocacion=False):
        """Defensa aconsejable para no abandonar un origen vulnerable."""
        j=self.juego
        ventana=self.ventana(jugador)
        necesidad=1
        for q in j.tablero[pais]['fronteras']:
            if q in excluir:continue
            enemigo=j.tablero[q]['propietario']
            if enemigo is None or j.es_propietario(q,jugador.idx):continue
            if not self._puede_reaccionar(q,pais,enemigo,jugador.idx):continue
            tropas=j.ejercitos_de(q,enemigo)
            if enemigo in ventana['restantes']:
                estimado=tropas+(3 if colocacion else 0)
                reserva=int(estimado*.9)+2
            elif enemigo in ventana['siguiente']:
                reserva=int((tropas+(2 if colocacion else 1))*.65)+1
            else:
                reserva=int(tropas*.4)+1
            necesidad=max(necesidad,reserva)
        return necesidad

    def limite_preparacion(self,jugador):
        """Primeros asientos: dispersar sin regalar frentes; últimos: concentrar."""
        j=self.juego
        fraccion=self.ventana(jugador)['fraccion_pendiente']
        disponibles=j.ejercitos_a_colocar
        if fraccion>=.67:
            return min(disponibles,4 if j.n_jugadores==2 else 2)
        if fraccion>=.34:
            return min(disponibles,3)
        return min(disponibles,6)

    def limite_incorporacion(self,jugador,amenaza_actual=0):
        """Hasta cuánto conviene revelar de golpe en una misma frontera."""
        ventana=self.ventana(jugador)
        fraccion=ventana['fraccion_pendiente']
        if fraccion>=.67:return 5 if amenaza_actual>=7 else 3
        if fraccion>=.34:return 7 if amenaza_actual>=7 else 5
        return 10
