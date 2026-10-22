"""Testes com unittest: não exigem pytest nem internet."""

import random
import unittest

from taberna_didatica import Configuracao, Taberna


class TesteTaberna(unittest.TestCase):
    def configurar(self, **mudancas: object) -> Configuracao:
        base = {
            "minutos": 15,
            "semente": 42,
            "quantidade_atendentes": 1,
            "chance_chegada": 1.0,
            "tempo_atendimento": 3,
            "preco_refeicao": 20,
            "paciencia_minima": 10,
            "paciencia_maxima": 10,
            "dinheiro_minimo": 100,
            "dinheiro_maximo": 100,
        }
        base.update(mudancas)
        return Configuracao(**base)

    def test_chegada_sem_clientes(self) -> None:
        taberna = Taberna(self.configurar(chance_chegada=0))
        resultado = taberna.executar()
        self.assertEqual(resultado.gerados, 0)
        self.assertEqual(resultado.receita, 0)
        self.assertEqual(resultado.utilizacao_atendentes, 0)

    def test_cliente_sem_recursos_nao_entra(self) -> None:
        taberna = Taberna(self.configurar(dinheiro_minimo=10, dinheiro_maximo=10))
        resultado = taberna.executar()
        self.assertEqual(resultado.recusados, 15)
        self.assertEqual(resultado.atendidos, 0)
        self.assertEqual(len(taberna.fila), 0)

    def test_fila_respeita_fifo(self) -> None:
        taberna = Taberna(self.configurar(minutos=8))
        taberna.executar()
        self.assertEqual(taberna.clientes[1].inicio_atendimento, 0)
        self.assertEqual(taberna.clientes[2].inicio_atendimento, 3)
        self.assertEqual(taberna.clientes[3].inicio_atendimento, 6)
        self.assertEqual(taberna.clientes[1].saida, 3)
        self.assertEqual(taberna.clientes[2].saida, 6)

    def test_atendimento_termina_no_tempo_correto(self) -> None:
        taberna = Taberna(self.configurar(minutos=1, tempo_atendimento=1))
        resultado = taberna.executar()
        self.assertEqual(resultado.atendidos, 1)
        self.assertEqual(taberna.clientes[1].saida, 1)
        self.assertEqual(resultado.receita, 20)

    def test_cliente_desiste_ao_atingir_limite(self) -> None:
        taberna = Taberna(
            self.configurar(minutos=8, tempo_atendimento=5, paciencia_minima=2, paciencia_maxima=2)
        )
        resultado = taberna.executar()
        self.assertGreater(resultado.desistencias, 0)
        self.assertEqual(taberna.clientes[2].saida, 3)
        self.assertEqual(taberna.clientes[2].estado, "desistiu")
        self.assertEqual(taberna.clientes[2].dinheiro, 100)

    def test_nao_cobra_antes_de_entregar(self) -> None:
        taberna = Taberna(self.configurar(minutos=1, tempo_atendimento=5))
        resultado = taberna.executar()
        self.assertEqual(resultado.em_atendimento, 1)
        self.assertEqual(resultado.atendidos, 0)
        self.assertEqual(resultado.receita, 0)
        self.assertEqual(taberna.clientes[1].dinheiro, 100)

    def test_pagamento_conserva_dinheiro(self) -> None:
        taberna = Taberna(self.configurar(minutos=30))
        resultado = taberna.executar()
        self.assertEqual(resultado.receita, 20 * resultado.atendidos)
        self.assertEqual(
            sum(cliente.dinheiro for cliente in taberna.clientes.values()) + taberna.caixa,
            taberna.dinheiro_criado,
        )
        taberna.verificar_invariantes()

    def test_passo_avanca_um_minuto(self) -> None:
        taberna = Taberna(self.configurar(minutos=2))
        self.assertEqual(taberna.resultado().minutos, 0)
        taberna.passo()
        self.assertEqual(taberna.resultado().minutos, 1)
        taberna.passo()
        self.assertEqual(taberna.resultado().minutos, 2)
        with self.assertRaises(RuntimeError):
            taberna.passo()

    def test_executar_apos_passos_continua_sem_recomecar(self) -> None:
        cfg = self.configurar()
        uma_vez = Taberna(cfg)
        uma_vez.passo()
        self.assertEqual(uma_vez.executar(), Taberna(cfg).executar())

    def test_resultado_nao_muda_estado(self) -> None:
        taberna = Taberna(self.configurar())
        taberna.passo()
        eventos = list(taberna.eventos)
        retrato1 = taberna.resultado()
        retrato2 = taberna.resultado()
        self.assertEqual(retrato1, retrato2)
        self.assertEqual(taberna.eventos, eventos)

    def test_mesma_semente_produz_mesmo_resultado_e_eventos(self) -> None:
        cfg = self.configurar(chance_chegada=0.67, dinheiro_minimo=10, dinheiro_maximo=60)
        primeira = Taberna(cfg)
        segunda = Taberna(cfg)
        self.assertEqual(primeira.executar(), segunda.executar())
        self.assertEqual(primeira.eventos, segunda.eventos)

    def test_simulacao_nao_altera_gerador_aleatorio_global(self) -> None:
        random.seed(12345)
        esperado = random.random()
        random.seed(12345)
        Taberna(self.configurar()).executar()
        self.assertEqual(random.random(), esperado)

    def test_saturacao_e_fila_ao_encerrar(self) -> None:
        taberna = Taberna(self.configurar(minutos=4, tempo_atendimento=10))
        resultado = taberna.executar()
        self.assertEqual(resultado.atendidos, 0)
        self.assertEqual(resultado.em_atendimento, 1)
        self.assertEqual(resultado.na_fila, 3)
        self.assertEqual(resultado.utilizacao_atendentes, 100)
        taberna.verificar_invariantes()

    def test_capacidade_de_atendentes_muda_atendimentos(self) -> None:
        um = Taberna(self.configurar(minutos=18, quantidade_atendentes=1))
        tres = Taberna(self.configurar(minutos=18, quantidade_atendentes=3))
        r1, r3 = um.executar(), tres.executar()
        self.assertEqual(r1.gerados, r3.gerados)
        self.assertGreater(r3.atendidos, r1.atendidos)

    def test_aumento_de_preco_impede_entrada(self) -> None:
        cfg = self.configurar(dinheiro_minimo=20, dinheiro_maximo=20)
        barato = Taberna(cfg).executar()
        caro = Taberna(self.configurar(dinheiro_minimo=20, dinheiro_maximo=20, preco_refeicao=30)).executar()
        self.assertEqual(barato.recusados, 0)
        self.assertEqual(caro.recusados, caro.gerados)

    def test_valida_configuracao(self) -> None:
        for mudancas in (
            {"minutos": 0},
            {"quantidade_atendentes": 0},
            {"chance_chegada": -0.1},
            {"chance_chegada": 1.1},
            {"tempo_atendimento": 0},
            {"preco_refeicao": 0},
            {"paciencia_minima": 0},
            {"paciencia_maxima": 0},
            {"dinheiro_minimo": -1},
            {"dinheiro_maximo": 5, "dinheiro_minimo": 6},
        ):
            with self.subTest(mudancas=mudancas), self.assertRaises(ValueError):
                self.configurar(**mudancas)

    def test_estados_sempre_coerentes_ao_longo_da_simulacao(self) -> None:
        taberna = Taberna(self.configurar(minutos=80, chance_chegada=0.83))
        for _ in range(taberna.config.minutos):
            taberna.passo()
            taberna.verificar_invariantes()


if __name__ == "__main__":
    unittest.main()
