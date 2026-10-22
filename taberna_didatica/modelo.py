"""Uma taberna mínima para estudar simulação baseada em agentes (ABM).

Um tick equivale a um minuto. Não há dependências externas.
"""

import random
from collections import deque
from dataclasses import dataclass

RACAS = ("humano", "anão", "elfo", "orc", "hobbit", "goblin")


@dataclass(frozen=True)
class Configuracao:
    minutos: int = 120
    semente: int = 42
    quantidade_atendentes: int = 2
    chance_chegada: float = 0.65
    tempo_atendimento: int = 4
    preco_refeicao: int = 20
    paciencia_minima: int = 3
    paciencia_maxima: int = 12
    dinheiro_minimo: int = 10
    dinheiro_maximo: int = 60

    def __post_init__(self) -> None:
        if self.minutos < 1 or self.quantidade_atendentes < 1:
            raise ValueError("Minutos e quantidade de atendentes devem ser positivos.")
        if not 0 <= self.chance_chegada <= 1:
            raise ValueError("A chance de chegada deve estar entre 0 e 1.")
        if self.tempo_atendimento < 1 or self.preco_refeicao < 1:
            raise ValueError("Tempo de atendimento e preço devem ser positivos.")
        if not 1 <= self.paciencia_minima <= self.paciencia_maxima:
            raise ValueError("Intervalo de paciência inválido.")
        if not 0 <= self.dinheiro_minimo <= self.dinheiro_maximo:
            raise ValueError("Intervalo de dinheiro inválido.")


@dataclass
class Cliente:
    identificador: int
    raca: str
    dinheiro: int
    paciencia: int
    chegada: int
    estado: str = "fila"
    inicio_atendimento: int | None = None
    saida: int | None = None


@dataclass
class Atendente:
    identificador: int
    cliente_id: int | None = None
    termina_em: int | None = None


@dataclass(frozen=True)
class Resultado:
    minutos: int
    gerados: int
    recusados: int
    atendidos: int
    desistencias: int
    na_fila: int
    em_atendimento: int
    receita: int
    espera_media: float
    utilizacao_atendentes: float


class Taberna:
    """Ambiente onde agentes interagem por uma fila FIFO e uma refeição."""

    def __init__(self, configuracao: Configuracao) -> None:
        self.config = configuracao
        self.aleatorio = random.Random(configuracao.semente)
        self.minuto = 0
        self.clientes: dict[int, Cliente] = {}
        self.fila: deque[int] = deque()
        self.atendentes = [
            Atendente(numero + 1)
            for numero in range(configuracao.quantidade_atendentes)
        ]
        self.caixa = 0
        self.dinheiro_criado = 0
        self.minutos_ocupados = 0
        self.esperas_concluidas: list[int] = []
        self.eventos: list[str] = []

    def _registrar(self, mensagem: str) -> None:
        self.eventos.append(f"[{self.minuto:03d} min] {mensagem}")

    def _chegar_cliente(self) -> None:
        if self.aleatorio.random() >= self.config.chance_chegada:
            return

        numero = len(self.clientes) + 1
        dinheiro = self.aleatorio.randint(
            self.config.dinheiro_minimo, self.config.dinheiro_maximo
        )
        paciencia = self.aleatorio.randint(
            self.config.paciencia_minima, self.config.paciencia_maxima
        )
        raca = self.aleatorio.choice(RACAS)
        cliente = Cliente(numero, raca, dinheiro, paciencia, self.minuto)
        self.clientes[numero] = cliente
        self.dinheiro_criado += dinheiro

        if dinheiro < self.config.preco_refeicao:
            cliente.estado = "recusado"
            cliente.saida = self.minuto
            self._registrar(f"{raca} #{numero} não entrou: sem dinheiro.")
            return

        self.fila.append(numero)
        self._registrar(f"{raca} #{numero} entrou na fila.")

    def _desistir_por_espera(self) -> None:
        # Só quem ainda está na fila pode desistir.
        # Preservamos a ordem dos demais clientes.
        nova_fila: deque[int] = deque()
        while self.fila:
            numero = self.fila.popleft()
            cliente = self.clientes[numero]
            if self.minuto - cliente.chegada >= cliente.paciencia:
                cliente.estado = "desistiu"
                cliente.saida = self.minuto
                self._registrar(f"Cliente #{numero} desistiu de esperar.")
            else:
                nova_fila.append(numero)
        self.fila = nova_fila

    def _iniciar_atendimentos(self) -> None:
        for atendente in self.atendentes:
            if atendente.cliente_id is not None or not self.fila:
                continue
            numero = self.fila.popleft()  # FIFO: primeiro a entrar, primeiro a sair.
            cliente = self.clientes[numero]
            cliente.estado = "em_atendimento"
            cliente.inicio_atendimento = self.minuto
            atendente.cliente_id = numero
            atendente.termina_em = self.minuto + self.config.tempo_atendimento
            self._registrar(f"Atendente #{atendente.identificador} iniciou cliente #{numero}.")

    def _concluir_atendimentos(self) -> None:
        for atendente in self.atendentes:
            if atendente.cliente_id is None or atendente.termina_em != self.minuto:
                continue
            cliente = self.clientes[atendente.cliente_id]
            # Pagamento só após a refeição ser efetivamente entregue.
            cliente.dinheiro -= self.config.preco_refeicao
            self.caixa += self.config.preco_refeicao
            cliente.estado = "atendido"
            cliente.saida = self.minuto
            if cliente.inicio_atendimento is None:
                raise RuntimeError("Cliente sem início de atendimento.")
            self.esperas_concluidas.append(cliente.inicio_atendimento - cliente.chegada)
            self._registrar(
                f"Atendente #{atendente.identificador} serviu cliente "
                f"#{cliente.identificador} (+{self.config.preco_refeicao} moedas)."
            )
            atendente.cliente_id = None
            atendente.termina_em = None

    def passo(self) -> None:
        """Avança exatamente um minuto, em uma ordem de eventos explícita."""
        if self.minuto >= self.config.minutos:
            raise RuntimeError("A simulação chegou ao tempo configurado.")

        # 1. Aguardar/desistir; 2. chegar; 3. alocar atendente disponível.
        self._desistir_por_espera()
        self._chegar_cliente()
        self._iniciar_atendimentos()

        # 4. Contabilizar ocupação durante este minuto.
        self.minutos_ocupados += sum(
            atendente.cliente_id is not None for atendente in self.atendentes
        )

        # 5. Avançar o relógio e concluir quem terminou neste instante.
        self.minuto += 1
        self._concluir_atendimentos()

    def executar(self) -> Resultado:
        while self.minuto < self.config.minutos:
            self.passo()
        self.verificar_invariantes()
        return self.resultado()

    def resultado(self) -> Resultado:
        """Gera um retrato do estado sem avançar o relógio."""
        estados = [cliente.estado for cliente in self.clientes.values()]
        espera = (
            sum(self.esperas_concluidas) / len(self.esperas_concluidas)
            if self.esperas_concluidas
            else 0.0
        )
        utilizacao = (
            100 * self.minutos_ocupados / (self.minuto * len(self.atendentes))
            if self.minuto
            else 0.0
        )
        return Resultado(
            minutos=self.minuto,
            gerados=len(self.clientes),
            recusados=estados.count("recusado"),
            atendidos=estados.count("atendido"),
            desistencias=estados.count("desistiu"),
            na_fila=len(self.fila),
            em_atendimento=estados.count("em_atendimento"),
            receita=self.caixa,
            espera_media=espera,
            utilizacao_atendentes=utilizacao,
        )

    def verificar_invariantes(self) -> None:
        """Propriedades que não podem ser violadas pelo modelo."""
        if sum(c.dinheiro for c in self.clientes.values()) + self.caixa != self.dinheiro_criado:
            raise AssertionError("O dinheiro não foi conservado.")
        if any(c.dinheiro < 0 for c in self.clientes.values()):
            raise AssertionError("Existe cliente com dinheiro negativo.")
        if any(self.clientes[num].estado != "fila" for num in self.fila):
            raise AssertionError("A fila contém cliente fora da espera.")
        ativos = [a.cliente_id for a in self.atendentes if a.cliente_id is not None]
        if len(ativos) != len(set(ativos)):
            raise AssertionError("Cliente atribuído a mais de um atendente.")
        if any(self.clientes[num].estado != "em_atendimento" for num in ativos):
            raise AssertionError("Ocupação inconsistente do atendente.")
        if len(self.clientes) != (
            len(self.fila)
            + len(ativos)
            + sum(
                c.estado in ("recusado", "atendido", "desistiu")
                for c in self.clientes.values()
            )
        ):
            raise AssertionError("Cliente foi contado mais de uma vez ou desapareceu.")
