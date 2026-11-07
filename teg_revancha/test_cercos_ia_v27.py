"""Regresiones v27: cercos estratégicos para IA Difícil.

Angola tiene exactamente tres fronteras: Nigeria, Etiopía y Mauritania.
Todos deben pertenecer al bot, con al menos 2 ejércitos cada uno.
"""
import unittest
from unittest.mock import patch
from logic import JuegoTEG, FASE_INCORPORAR, FASE_REAGRUPAR, FASE_ATACAR


GUARDIAS=('Nigeria','Etiopia','Mauritania')
BLANCO='Angola'


def escenario(soldados=(1,2,2), disponibles=5):
    j=JuegoTEG(4,orden_inicial=[1,0,2,3],dificultad='Dificil')
    j.etapa='hostilidades'
    j.etapa_ronda='INCORPORACION'
    j.fase=FASE_INCORPORAR
    j.turno_idx=1
    j.ronda=3
    j.situacion='Clásico'
    j.ejercitos_a_colocar=disponibles
    j.refuerzos_continente={}
    j.jugadores[1].tarjetas.clear()
    j.bot_refuerzos_por_pais={}
    j.reagrupados_recibidos={}
    # Distribución sin líderes a punto de 45 países, para que el cerco
    # pueda competir de verdad con la estrategia convencional.
    for i,pais in enumerate(j.tablero):
        j.tablero[pais]['propietario']=[0,2,3][i%3]
        j.tablero[pais]['ejercitos']=6
    propios=[p for p in list(j.tablero)[2::7] if p not in (BLANCO,*GUARDIAS)]
    for pais in propios:
        j.tablero[pais]['propietario']=1
        j.tablero[pais]['ejercitos']=6
    for pais,n in zip(GUARDIAS,soldados):
        j.tablero[pais]['propietario']=1
        j.tablero[pais]['ejercitos']=n
    j.tablero[BLANCO]['propietario']=2
    j.tablero[BLANCO]['ejercitos']=9
    # El rival posee otros países; el último país es inbloqueable por regla.
    j.tablero['Alaska']['propietario']=2
    return j


class ReglaMotor(unittest.TestCase):
    def test_un_guardia_con_una_ficha_no_bloquea(self):
        j=escenario()
        self.assertFalse(j._pais_bloqueado(BLANCO))
        self.assertTrue(j.incorporar('Nigeria',1))
        self.assertTrue(j._pais_bloqueado(BLANCO))

    def test_requisito_tres_vecinos_y_mismo_color(self):
        j=escenario((2,2,2))
        self.assertTrue(j._pais_bloqueado(BLANCO))
        j.tablero['Mauritania']['propietario']=0
        self.assertFalse(j._pais_bloqueado(BLANCO))

    def test_condominio_no_sera_considerado_para_el_bloqueo(self):
        j=escenario((2,2,2))
        j.condominios['Nigeria']={1:2,0:1}
        j._sincronizar_condominio('Nigeria')
        self.assertFalse(j._pais_bloqueado(BLANCO))


class PlanificarCerco(unittest.TestCase):
    def test_identifica_pais_con_un_unico_guardia_incompleto(self):
        j=escenario()
        bot=j.jugadores[1]
        objetivos=[x for x in j.ia_dificil.cercos.objetivos(bot)
                   if x['pais']==BLANCO]
        self.assertEqual(len(objetivos),1)
        self.assertEqual(objetivos[0]['faltantes'],(('Nigeria',1),))
        self.assertEqual(objetivos[0]['costo'],1)

    def test_refuerza_exactamente_un_ejercito_y_activa_bloqueo(self):
        j=escenario()
        bot=j.jugadores[1]
        plan=j.ia_dificil.cercos.refuerzo(bot,list(GUARDIAS))
        self.assertEqual(plan,('Nigeria',1,BLANCO))
        self.assertTrue(j.incorporar(plan[0],plan[1]))
        self.assertEqual(j.tablero['Nigeria']['ejercitos'],2)
        self.assertTrue(j._pais_bloqueado(BLANCO))

    def test_cerca_dos_fronteras_con_un_refuerzo_cada_una(self):
        j=escenario((1,1,2),disponibles=4)
        bot=j.jugadores[1]
        for _ in range(2):
            plan=j.ia_dificil.cercos.refuerzo(bot,list(GUARDIAS))
            self.assertIsNotNone(plan)
            self.assertEqual(plan[1],1)
            self.assertTrue(j.incorporar(plan[0],plan[1]))
        self.assertTrue(j._pais_bloqueado(BLANCO))

    def test_no_gasta_el_ultimo_refuerzo_si_no_puede_completar_cerco(self):
        j=escenario((1,1,2),disponibles=1)
        self.assertIsNone(j.ia_dificil.cercos.refuerzo(
            j.jugadores[1],list(GUARDIAS)))

    def test_respeta_bonos_de_continente_obligatorios(self):
        j=escenario()
        j.refuerzos_continente={'Europa':5}
        self.assertIsNone(j.ia_dificil.cercos.refuerzo(
            j.jugadores[1],list(GUARDIAS)))

    def test_no_confunde_cerco_parcial_con_encierro(self):
        j=escenario()
        j.tablero['Mauritania']['propietario']=0
        self.assertFalse(any(x['pais']==BLANCO for x in
                             j.ia_dificil.cercos.objetivos(j.jugadores[1])))

    def test_motor_dificil_incorpora_con_prioridad_de_cerco(self):
        j=escenario()
        j.ejercitos_a_colocar=1
        with patch.object(j.ia_dificil.remontada,'plan_refuerzo',return_value=None):
            estado=j.ia_dificil.refuerzo(j.jugadores[1])
        self.assertEqual(estado['accion'],'incorporar')
        self.assertEqual((estado['pais'],estado['cantidad']),('Nigeria',1))
        self.assertTrue(j._pais_bloqueado(BLANCO))

    def test_normal_no_activa_plan_de_cerco(self):
        j=escenario()
        j.dificultad='Normal'
        with patch.object(j.ia_dificil.cercos,'refuerzo',
                          side_effect=AssertionError('Normal invoco cerco')):
            j.paso_bot()


class PreservarCerco(unittest.TestCase):
    def test_guardia_de_2_no_debe_salir_a_otro_ataque(self):
        j=escenario((2,2,2))
        bot=j.jugadores[1]
        self.assertEqual(j.ia_dificil.cercos.reserva('Nigeria',bot),2)
        self.assertTrue(j.ia_dificil.cercos.compromete(
            'Nigeria','Sudafrica',bot,bajas=0,traslado=1))
        self.assertFalse(j.ia_dificil.cercos.compromete(
            'Nigeria',BLANCO,bot,bajas=0,traslado=1))

    def test_no_drenar_guardia_durante_reagrupamiento(self):
        j=escenario((2,2,2))
        j.fase=FASE_REAGRUPAR
        bot=j.jugadores[1]
        with patch.object(j.ia_dificil.turnos,'reserva',return_value=1):
            j.ia_dificil.reagrupar(bot)
        # Incluso si otro frente demanda refuerzos, no debe quedar por
        # debajo de dos ninguno de los guardias del cerco establecido.
        for p in GUARDIAS:
            self.assertGreaterEqual(j.tablero[p]['ejercitos'],2)

    def test_reagrupar_un_guardia_incompleto_conserva_el_donante(self):
        j=escenario((1,3,2))
        j.fase=FASE_REAGRUPAR
        bot=j.jugadores[1]
        with patch.object(j.ia_dificil.turnos,'reserva',return_value=1):
            maniobra=j.ia_dificil.cercos.reagrupe(bot)
        self.assertIsNotNone(maniobra)
        origen,destino,cantidad,blanco=maniobra
        self.assertEqual((origen,destino,cantidad,blanco),
                         ('Etiopia','Nigeria',1,BLANCO))
        self.assertTrue(j.reagrupar(origen,destino,cantidad))
        self.assertTrue(j._pais_bloqueado(BLANCO))


class SalidaDeEncierro(unittest.TestCase):
    def test_bot_bloqueado_busca_romper_por_vecino_debil(self):
        j=escenario()
        for n in GUARDIAS:
            j.tablero[n]['propietario']=2
            j.tablero[n]['ejercitos']=2
        j.tablero[BLANCO]['propietario']=1
        j.tablero[BLANCO]['ejercitos']=16
        j.fase=FASE_ATACAR
        bot=j.jugadores[1]
        self.assertTrue(j._pais_bloqueado(BLANCO))
        plan=j.ia_dificil.cercos.escape(
            bot,__import__('ia_dificil').probabilidad_conquista)
        self.assertIsNotNone(plan)
        self.assertEqual(plan[-2],BLANCO)
        self.assertIn(plan[-1],GUARDIAS)

    def test_bot_bloqueado_no_ataca_si_defensa_es_imposible(self):
        j=escenario()
        for n in GUARDIAS:
            j.tablero[n]['propietario']=2
            j.tablero[n]['ejercitos']=25
        j.tablero[BLANCO]['propietario']=1
        j.tablero[BLANCO]['ejercitos']=2
        j.fase=FASE_ATACAR
        self.assertTrue(j._pais_bloqueado(BLANCO))
        self.assertIsNone(j.ia_dificil.cercos.escape(
            j.jugadores[1],__import__('ia_dificil').probabilidad_conquista))


if __name__=='__main__':
    unittest.main()
