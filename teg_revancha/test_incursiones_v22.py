"""v22: una conquista barata puede ser útil solo para conseguir tarjeta."""
import unittest
from unittest.mock import patch

from logic import JuegoTEG, FASE_ATACAR, FASE_TARJETA


def escenario_mapa(dificultad='Dificil',tropas=25,defensa=1):
    juego=JuegoTEG(4,orden_inicial=[1,2,0,3],dificultad=dificultad)
    juego.etapa='hostilidades'
    juego.etapa_ronda='ATAQUE'
    juego.fase=FASE_ATACAR
    juego.turno_idx=1
    juego.ronda=4
    juego.situacion='Clásico'
    juego.crisis_sin_tarjeta=set()
    juego.conquistas_turno=0
    juego.conquistas_colectivas=0
    juego.sancion_tarjeta[1]=0
    juego.tarjeta_solicitada=False
    juego.bot_ataques_turno=0
    bot=juego.jugadores[1]
    bot.canjes_realizados=0
    bot.tarjetas.clear()
    # Un atacante fuerte frente a un único defensor. Los otros ejércitos
    # pueden recuperar rápidamente la ficha ocupada, como en la captura.
    for k,p in enumerate(juego.tablero):
        juego.tablero[p]['propietario']=[0,2,3][k%3]
        juego.tablero[p]['ejercitos']=18
    juego.tablero['Nigeria']['propietario']=1
    juego.tablero['Nigeria']['ejercitos']=tropas
    juego.tablero['Angola']['propietario']=0
    juego.tablero['Angola']['ejercitos']=defensa
    juego.tablero['Etiopia']['propietario']=2
    juego.tablero['Etiopia']['ejercitos']=14
    return juego


class IncursionesPorTarjeta(unittest.TestCase):
    def test_una_ficha_enemiga_vale_una_tarjeta_aunque_se_recapture(self):
        j=escenario_mapa()
        bot=j.jugadores[1]
        inc=j.ia_dificil.incursiones.candidato(bot)
        self.assertIsNotNone(inc)
        self.assertEqual(inc[-3:],('Nigeria','Angola',1))
        self.assertGreater(inc[1],.85)

    def test_captura_real_mueve_solo_una_ficha_en_dificil(self):
        j=escenario_mapa()
        bot=j.jugadores[1]
        with patch.object(j.ia_dificil,'diplomacia',return_value=None):
            with patch('logic.random.randint',side_effect=[6,6,6,1]):
                r=j.paso_bot()
        self.assertEqual(r['accion'],'atacar')
        self.assertIn('incursiona por tarjeta',r['texto'])
        self.assertTrue(r['dados']['conquisto'])
        self.assertEqual(j.tablero['Nigeria']['ejercitos'],24)
        self.assertEqual(j.tablero['Angola']['ejercitos'],1)
        self.assertEqual(j.conquistas_turno,1)
        j.fase=FASE_TARJETA
        self.assertTrue(j.puede_solicitar_tarjeta())
        r=j.paso_bot()
        self.assertEqual(r['accion'],'tarjeta')
        self.assertEqual(len(bot.tarjetas),1)

    def test_el_traslado_normal_sigue_siendo_tres(self):
        j=escenario_mapa(dificultad='Normal')
        with patch('logic.random.randint',side_effect=[6,6,6,1]):
            r=j.atacar('Nigeria','Angola',traslado_bot=1)
        self.assertTrue(r['conquisto'])
        self.assertEqual(j.tablero['Nigeria']['ejercitos'],22)
        self.assertEqual(j.tablero['Angola']['ejercitos'],3)

    def test_traslado_minimo_solo_cuando_se_solicita(self):
        j=escenario_mapa()
        with patch('logic.random.randint',side_effect=[6,6,6,1]):
            j.atacar('Nigeria','Angola')
        self.assertEqual(j.tablero['Nigeria']['ejercitos'],22)
        self.assertEqual(j.tablero['Angola']['ejercitos'],3)

    def test_traslado_bot_invalido_no_viola_reglas(self):
        for valor in (0,4,'1',-1,None):
            with self.subTest(valor=valor):
                j=escenario_mapa()
                with patch('logic.random.randint',side_effect=[6,6,6,1]):
                    j.atacar('Nigeria','Angola',traslado_bot=valor)
                self.assertEqual(j.tablero['Angola']['ejercitos'],3)

    def test_sin_tarjeta_pendiente_no_hay_incursion(self):
        j=escenario_mapa()
        j.conquistas_turno=1
        self.assertEqual(j.ia_dificil.incursiones.faltantes(j.jugadores[1]),0)
        self.assertIsNone(j.ia_dificil.incursiones.candidato(j.jugadores[1]))

    def test_con_cinco_tarjetas_o_crisis_no_se_regala_terreno(self):
        j=escenario_mapa()
        j.jugadores[1].tarjetas=list(j.tablero)[:5]
        self.assertIsNone(j.ia_dificil.incursiones.candidato(j.jugadores[1]))
        j.jugadores[1].tarjetas.clear()
        j.crisis_sin_tarjeta.add(1)
        self.assertIsNone(j.ia_dificil.incursiones.candidato(j.jugadores[1]))
        j.crisis_sin_tarjeta.clear()
        j.sancion_tarjeta[1]=1
        self.assertIsNone(j.ia_dificil.incursiones.candidato(j.jugadores[1]))

    def test_despues_de_tres_canjes_solo_si_hay_segunda_conquista(self):
        j=escenario_mapa()
        bot=j.jugadores[1]
        bot.canjes_realizados=3
        self.assertEqual(j.ia_dificil.incursiones.faltantes(bot),2)
        self.assertIsNone(j.ia_dificil.incursiones.candidato(bot))
        j.tablero['Sudafrica']['propietario']=0
        j.tablero['Sudafrica']['ejercitos']=1
        self.assertIsNotNone(j.ia_dificil.incursiones.candidato(bot))

    def test_ataque_imposible_no_persigue_tarjeta(self):
        j=escenario_mapa(tropas=3,defensa=20)
        self.assertIsNone(j.ia_dificil.incursiones.candidato(j.jugadores[1]))

    def test_dificil_respeta_fronteras_cerradas_y_abiertas(self):
        j=escenario_mapa()
        bot=j.jugadores[1]
        j.situacion='Fronteras abiertas'
        self.assertIsNone(j.ia_dificil.incursiones.candidato(bot))
        j.situacion='Fronteras cerradas'
        self.assertIsNotNone(j.ia_dificil.incursiones.candidato(bot))

    def test_zona_internacional_no_se_confunde_con_incursion(self):
        j=escenario_mapa()
        with patch.object(j,'zona_para',side_effect=lambda pais: {'pais':pais} if pais=='Angola' else None):
            self.assertIsNone(j.ia_dificil.incursiones.candidato(j.jugadores[1]))

    def test_prioridad_victoria_45_paises_antes_de_incursion(self):
        j=escenario_mapa()
        bot=j.jugadores[1]
        for pais in list(j.tablero)[:44]:
            j.tablero[pais]['propietario']=1
        with patch.object(j.ia_dificil.incursiones,'candidato',return_value=(100,1,'Nigeria','Angola',1)):
            with patch.object(j.ia_dificil,'candidato_ataque',return_value=None):
                with patch.object(j.ia_dificil,'diplomacia',return_value=None):
                    r=j.ia_dificil.atacar(bot)
        self.assertNotEqual(r.get('accion'),'atacar')

    def test_no_llamar_plan_de_incursion_en_normal(self):
        j=escenario_mapa(dificultad='Normal')
        with patch.object(j.ia_dificil.incursiones,'candidato',
                          side_effect=AssertionError('Normal no usa incursiones')):
            self.assertIsInstance(j.paso_bot(),dict)


if __name__=='__main__':
    unittest.main()
