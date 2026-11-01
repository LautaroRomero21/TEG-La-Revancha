"""Regresiones v20: orden de turnos, IA Difícil y estadísticas de canjes."""
import unittest
from unittest.mock import patch
from logic import JuegoTEG, FASE_INCORPORAR, FASE_ATACAR


def juego_orden(orden=(1,2,0,3),dificultad='Dificil'):
    j=JuegoTEG(4,orden_inicial=list(orden),dificultad=dificultad)
    j.turno_idx=1
    j.fase=FASE_ATACAR
    j.etapa='hostilidades'
    j.etapa_ronda='ATAQUE'
    j.ronda=3
    j.situacion='Clásico'
    for q in j.tablero['Nigeria']['fronteras']:
        j.tablero[q]['propietario']=1
        j.tablero[q]['ejercitos']=2
    j.tablero['Nigeria']['propietario']=1
    j.tablero['Nigeria']['ejercitos']=16
    j.tablero['Angola']['propietario']=2
    j.tablero['Angola']['ejercitos']=9
    return j


class OrdenReal(unittest.TestCase):
    def test_primero_tiene_mas_rivales_por_jugar(self):
        j=juego_orden((1,2,0,3))
        ventana=j.ia_dificil.turnos.ventana(j.jugadores[1])
        self.assertEqual(ventana['restantes'],[2,0,3])
        self.assertEqual(ventana['siguiente'],[2,0,3])
        self.assertEqual(ventana['fraccion_pendiente'],1.0)

    def test_ultimo_no_tiene_rivales_pendientes_en_esta_ronda(self):
        j=juego_orden((2,0,3,1))
        ventana=j.ia_dificil.turnos.ventana(j.jugadores[1])
        self.assertEqual(ventana['restantes'],[])
        self.assertEqual(ventana['fraccion_pendiente'],0)

    def test_orden_ignora_eliminados(self):
        j=juego_orden((1,2,0,3))
        j.jugadores[2].eliminado=True
        ventana=j.ia_dificil.turnos.ventana(j.jugadores[1])
        self.assertEqual(ventana['restantes'],[0,3])

    def test_rotacion_siguiente_ronda_es_considerada(self):
        j=juego_orden((2,0,3,1))
        ventana=j.ia_dificil.turnos.ventana(j.jugadores[1])
        self.assertEqual(ventana['siguiente'],[0,3])

    def test_el_que_juega_despues_es_mayor_amenaza(self):
        j=juego_orden((1,2,0,3))
        bot=j.jugadores[1]
        temprano=j.ia_dificil.turnos.amenaza('Nigeria',bot,guarnicion=5)
        j.orden_ronda=[2,0,3,1]
        ultimo=j.ia_dificil.turnos.amenaza('Nigeria',bot,guarnicion=5)
        self.assertGreater(temprano,ultimo)

    def test_nieve_y_fronteras_respetadas_al_proyectar_amenazas(self):
        j=juego_orden()
        bot=j.jugadores[1]
        j.situacion='Fronteras abiertas'
        # Nigeria y Angola pertenecen al mismo continente.
        self.assertEqual(j.ia_dificil.turnos.amenaza('Nigeria',bot,guarnicion=2),0)

    def test_reserva_aumenta_con_rival_que_juega_despues(self):
        j=juego_orden((1,2,0,3))
        bot=j.jugadores[1]
        temprano=j.ia_dificil.turnos.reserva('Nigeria',bot)
        j.orden_ronda=[2,0,3,1]
        ultimo=j.ia_dificil.turnos.reserva('Nigeria',bot)
        self.assertGreater(temprano,ultimo)


class PreparacionContextual(unittest.TestCase):
    def test_bot_primero_distribuye_sus_ocho_refuerzos(self):
        j=JuegoTEG(4,orden_inicial=[1,0,2,3],dificultad='Dificil')
        movidos=[]
        for _ in range(12):
            if j.turno_idx!=1:break
            evento=j.paso_bot()
            self.assertEqual(evento['accion'],'incorporar')
            movidos.extend([evento['pais']]*evento['cantidad'])
        self.assertEqual(len(movidos),8)
        self.assertGreaterEqual(len(set(movidos)),4)
        self.assertLessEqual(max(movidos.count(p) for p in set(movidos)),2)

    def test_preparacion_posterior_permita_concentracion_mayor(self):
        primero=JuegoTEG(4,orden_inicial=[1,0,2,3],dificultad='Dificil')
        ultimo=JuegoTEG(4,orden_inicial=[0,2,3,1],dificultad='Dificil')
        self.assertEqual(primero.ia_dificil.turnos.limite_preparacion(primero.jugadores[1]),2)
        self.assertEqual(ultimo.ia_dificil.turnos.limite_preparacion(ultimo.jugadores[1]),6)

    def test_segunda_preparacion_tiene_registro_independiente(self):
        j=JuegoTEG(4,orden_inicial=[1,0,2,3],dificultad='Dificil')
        for _ in range(4):j.paso_bot()
        self.assertTrue(j.ia_dificil._colocaciones_preparacion.get((0,1)))
        self.assertNotIn((1,1),j.ia_dificil._colocaciones_preparacion)
        j.vuelta_preparacion=1
        j.turno_idx=1
        j.ejercitos_a_colocar=4
        j.paso_bot()
        self.assertTrue(j.ia_dificil._colocaciones_preparacion.get((1,1)))

    def test_inicio_normal_no_consulta_analisis_avanzado(self):
        j=JuegoTEG(4,orden_inicial=[1,0,2,3],dificultad='Normal')
        with patch.object(j.ia_dificil.turnos,'ventana',side_effect=AssertionError('No llamar')):
            self.assertEqual(j.paso_bot()['accion'],'incorporar')


class CombateYReagrupamiento(unittest.TestCase):
    def test_ataque_temprano_se_penaliza_por_exposicion(self):
        j=juego_orden((1,2,0,3))
        j.tablero['Angola']['ejercitos']=2
        j.tablero['Nigeria']['ejercitos']=19
        bot=j.jugadores[1]
        ctx=j.ia_dificil.contexto(bot)
        temprano=j.ia_dificil.evaluacion_ataque('Nigeria','Angola',bot,ctx)
        j.orden_ronda=[2,0,3,1]
        tardio=j.ia_dificil.evaluacion_ataque('Nigeria','Angola',bot,ctx)
        self.assertIsNotNone(temprano)
        self.assertIsNotNone(tardio)
        self.assertGreater(tardio[0],temprano[0])

    def test_reserva_protege_guarnicion_amenazada(self):
        j=juego_orden()
        bot=j.jugadores[1]
        j.tablero['Nigeria']['ejercitos']=10
        j.tablero['Angola']['ejercitos']=14
        reserva=j.ia_dificil.turnos.reserva('Nigeria',bot)
        self.assertGreater(reserva,1)

    def test_valor_del_canje_es_independiente_por_color(self):
        j=juego_orden()
        esperados=[6,10,15,20,25,30]
        for i in range(4):
            jugador=j.jugadores[i]
            for anteriores,valor in enumerate(esperados):
                jugador.canjes_realizados=anteriores
                self.assertEqual(j.valor_canje(jugador),valor)

    def test_canjes_no_se_mutan_al_consultar(self):
        j=juego_orden()
        bot=j.jugadores[2]
        bot.canjes_realizados=3
        self.assertEqual(j.valor_canje(bot),20)
        self.assertEqual(bot.canjes_realizados,3)


if __name__=='__main__':
    unittest.main()
