"""Regresiones v21: remontada por tarjetas y frontera Siberia–Chukchi."""
import unittest
from unittest.mock import patch

from data import PAISES_DATA
from logic import JuegoTEG, FASE_ATACAR, FASE_INCORPORAR, FASE_TARJETA


def partida_critica(n=4, tropas=1, defensores=2):
    j=JuegoTEG(n_jugadores=n, orden_inicial=[1]+[i for i in range(n) if i!=1],
               dificultad='Dificil')
    j.etapa='hostilidades'
    j.etapa_ronda='INCORPORACION'
    j.fase=FASE_INCORPORAR
    j.ronda=4
    j.turno_idx=1
    j.situacion='Clásico'
    j.refuerzos_continente={}
    j.ejercitos_a_colocar=7
    j.conquistas_turno=0
    j.conquistas_colectivas=0
    j.crisis_sin_tarjeta=set()
    j.sancion_tarjeta[1]=0
    j.jugadores[1].canjes_realizados=0
    j.jugadores[1].tarjetas.clear()
    # Distribución pública de fuerzas: nadie está a punto de ganar.
    rivales=[i for i in range(n) if i!=1]
    for i,p in enumerate(j.tablero):
        j.tablero[p]['propietario']=rivales[i%len(rivales)]
        j.tablero[p]['ejercitos']=20
        j.tablero[p]['misiles']=0
    j.tablero['Nigeria']['propietario']=1
    j.tablero['Nigeria']['ejercitos']=tropas
    j.tablero['Angola']['propietario']=2 if n>=3 else 0
    j.tablero['Angola']['ejercitos']=defensores
    return j


class FronteraSiberiaChukchi(unittest.TestCase):
    def test_relacion_eliminada_en_ambos_sentidos(self):
        self.assertNotIn('Chukchi',PAISES_DATA['Siberia']['fronteras'])
        self.assertNotIn('Siberia',PAISES_DATA['Chukchi']['fronteras'])
        self.assertIn('Chechenia',PAISES_DATA['Siberia']['fronteras'])
        self.assertIn('Kamchatka',PAISES_DATA['Chukchi']['fronteras'])

    def test_grafo_sigue_siendo_reciproco(self):
        j=partida_critica()
        self.assertFalse(j.son_adyacentes('Siberia','Chukchi'))
        for pais,d in j.tablero.items():
            for vecino in d['fronteras']:
                self.assertIn(pais,j.tablero[vecino]['fronteras'])


class NecesidadDeTarjeta(unittest.TestCase):
    def test_un_pais_es_critico_y_puede_buscar_tarjeta(self):
        j=partida_critica()
        e=j.ia_dificil.remontada.estado(j.jugadores[1])
        self.assertTrue(e['critico'])
        self.assertTrue(e['buscar_tarjeta'])
        self.assertEqual(e['faltan'],1)

    def test_despues_tercer_canje_debe_conquistar_dos(self):
        j=partida_critica()
        bot=j.jugadores[1]
        bot.canjes_realizados=3
        self.assertEqual(j.ia_dificil.remontada.estado(bot)['faltan'],2)
        j.conquistas_turno=1
        self.assertEqual(j.ia_dificil.remontada.estado(bot)['faltan'],1)
        j.conquistas_turno=2
        self.assertFalse(j.ia_dificil.remontada.estado(bot)['buscar_tarjeta'])

    def test_conquista_colectiva_y_tarjeta_ya_lograda(self):
        j=partida_critica()
        j.conquistas_colectivas=2
        self.assertFalse(j.ia_dificil.remontada.estado(j.jugadores[1])['buscar_tarjeta'])
        j.conquistas_colectivas=0
        j.tarjeta_solicitada=True
        self.assertFalse(j.ia_dificil.remontada.estado(j.jugadores[1])['buscar_tarjeta'])

    def test_no_insiste_si_mano_esta_llena(self):
        j=partida_critica()
        j.jugadores[1].tarjetas=['Nigeria']*5
        self.assertFalse(j.ia_dificil.remontada.estado(j.jugadores[1])['buscar_tarjeta'])

    def test_crisis_y_sancion_impiden_busqueda_tarjeta(self):
        j=partida_critica()
        j.crisis_sin_tarjeta.add(1)
        self.assertFalse(j.ia_dificil.remontada.estado(j.jugadores[1])['buscar_tarjeta'])
        j.crisis_sin_tarjeta.clear()
        j.sancion_tarjeta[1]=1
        self.assertFalse(j.ia_dificil.remontada.estado(j.jugadores[1])['buscar_tarjeta'])

    def test_ejercito_sano_no_se_vuelve_desesperado(self):
        j=partida_critica()
        bot=j.jugadores[1]
        for pais in list(j.tablero)[:23]:
            j.tablero[pais]['propietario']=1
        self.assertFalse(j.ia_dificil.remontada.estado(bot)['critico'])


class IncorporacionParaRemontar(unittest.TestCase):
    def test_elije_frente_asequible_no_apila_ante_20_ejercitos(self):
        j=partida_critica(tropas=1,defensores=2)
        plan=j.ia_dificil.remontada.plan_refuerzo(j.jugadores[1],['Nigeria'])
        self.assertIsNotNone(plan)
        origen,cantidad,destino=plan
        self.assertEqual((origen,destino),('Nigeria','Angola'))
        self.assertGreaterEqual(cantidad,1)
        self.assertLessEqual(cantidad,7)

    def test_refuerzo_real_se_aplica_para_abrir_ataque(self):
        j=partida_critica(tropas=1,defensores=2)
        respuesta=j.paso_bot()
        self.assertEqual(respuesta['accion'],'incorporar')
        self.assertEqual(respuesta['pais'],'Nigeria')
        self.assertIn('remontada',respuesta['texto'])
        self.assertGreater(j.tablero['Nigeria']['ejercitos'],1)

    def test_si_no_existe_ningun_ataque_viable_no_se_fuerza_plan(self):
        j=partida_critica(tropas=1,defensores=20)
        self.assertIsNone(j.ia_dificil.remontada.plan_refuerzo(j.jugadores[1],['Nigeria']))

    def test_refuerzos_libres_y_continentales_siguen_limitados(self):
        j=partida_critica(tropas=1,defensores=2)
        j.refuerzos_continente={'Africa':2}
        plan=j.ia_dificil.remontada.plan_refuerzo(j.jugadores[1],['Nigeria'])
        self.assertIsNotNone(plan)
        self.assertLessEqual(plan[1],2)


class AtaqueParaConseguirTarjeta(unittest.TestCase):
    def test_puede_atacar_con_riesgo_moderado_si_esta_casi_eliminado(self):
        j=partida_critica(tropas=3,defensores=1)
        j.fase=FASE_ATACAR
        bot=j.jugadores[1]
        plan=j.ia_dificil.remontada.candidato_ataque(bot)
        self.assertIsNotNone(plan)
        self.assertEqual(plan[-2:],('Nigeria','Angola'))
        self.assertGreater(plan[1],.5)

    def test_no_ataca_2_contra_20_por_conseguir_tarjeta(self):
        j=partida_critica(tropas=2,defensores=20)
        j.fase=FASE_ATACAR
        self.assertIsNone(j.ia_dificil.remontada.candidato_ataque(j.jugadores[1]))

    def test_el_bot_dificil_utiliza_candidato_de_remontada(self):
        j=partida_critica(tropas=3,defensores=1)
        j.fase=FASE_ATACAR
        j.bot_ataques_turno=0
        with patch.object(j.ia_dificil,'diplomacia',return_value=None):
            with patch.object(j,'atacar',return_value={'ok':True}):
                accion=j.paso_bot()
        self.assertEqual(accion['accion'],'atacar')
        self.assertEqual((accion['pais'],accion['destino']),('Nigeria','Angola'))

    def test_el_modo_normal_sigue_independiente(self):
        j=JuegoTEG(4,orden_inicial=[1,0,2,3],dificultad='Normal')
        with patch.object(j.ia_dificil.remontada,'plan_refuerzo',
                          side_effect=AssertionError('Normal no invoca remontada')):
            with patch.object(j.ia_dificil.remontada,'candidato_ataque',
                              side_effect=AssertionError('Normal no invoca remontada')):
                j.turno_idx=1
                self.assertEqual(j.paso_bot()['accion'],'incorporar')


if __name__=='__main__':
    unittest.main()
