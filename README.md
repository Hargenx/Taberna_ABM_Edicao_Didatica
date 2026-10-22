# A Taberna do Deus Esquecido — Edição Didática

> **Projeto independente e enxuto para a disciplina de ABM / Simulação Baseada em Agentes.**
> Não é uma atualização nem uma cópia do projeto avançado *A Taberna do Deus Esquecido — Beta*.

## O problema

No mundo de fantasia, humanos, elfos, anões, orcs, hobbits e goblins procuram a taberna para comprar uma refeição. Há poucos atendentes e **uma única fila FIFO**. A cada minuto:

1. Clientes esperando podem **desistir** caso esgotem sua paciência.
2. Um novo cliente pode **chegar**, se a sorte permitir.
3. Quem não tem dinheiro suficiente **não entra**.
4. Um atendente livre chama o **primeiro da fila**.
5. Após terminar o atendimento, o cliente **paga**, recebe sua refeição e sai.

O estabelecimento possui um caixa. O preço é fixo e o atendimento demora um número inteiro de minutos. **Um tick = um minuto.** O mundo do Vigilante é apenas o contexto narrativo; não há magia, combate, estoque, cozinha, turnos nem interface gráfica neste exemplo.

## Objetivos da aula

- Identificar **agentes** (clientes e atendentes) e **ambiente** (taberna, fila, caixa).
- Observar **estado** (dinheiro, paciência, ocupado/livre) e **regras individuais**.
- Explicar a diferença entre regras locais e **resultado emergente** (espera, abandono, congestionamento).
- Comparar cenários modificando somente um parâmetro por vez.
- Usar **semente aleatória** para reproduzir experimentos.
- Avaliar o resultado com métricas, sem confundir **receita** com **lucro**.

## Estrutura

```text
Taberna_ABM_Edicao_Didatica/
├── README.md
├── GUIA_DA_AULA.md
├── taberna_didatica/
│   ├── __init__.py
│   ├── modelo.py           # Configuração, agentes, fila e motor
│   └── __main__.py        # Interface de linha de comando
├── examples/
│   ├── __init__.py
│   └── comparar_cenarios.py
└── tests/
    └── test_modelo.py
```

**Requisitos:** Python 3.11 ou superior. Apenas biblioteca padrão; não precisa de `pip install`.

## Executar no Windows (PowerShell)

Abra o terminal **na pasta que contém este README**:

```powershell
py -m taberna_didatica
```

Para acompanhar cada decisão:

```powershell
py -m taberna_didatica --minutos 20 --semente 42 --eventos
```

Para provocar congestionamento:

```powershell
py -m taberna_didatica --minutos 120 --atendentes 1 --chegada 0.9 --tempo-atendimento 6
```

Para comparar diferentes quantidades de atendentes sob sementes iguais:

```powershell
py -m examples.comparar_cenarios
```

Executar os testes:

```powershell
py -m unittest discover -s tests -v
```

Em Linux/macOS, substitua `py` por `python3` quando necessário.

## Parâmetros principais

| Parâmetro | Padrão | Significado |
| --- | ---: | --- |
| `--minutos` | 120 | Duração da simulação |
| `--semente` | 42 | Aleatoriedade reproduzível |
| `--atendentes` | 2 | Capacidade paralela de atendimento |
| `--chegada` | 0.65 | Chance de **até um** visitante chegar por minuto |
| `--tempo-atendimento` | 4 | Minutos para atender cada pessoa |
| `--preco` | 20 | Preço de uma refeição, em moedas |
| `--eventos` | desligado | Exibe o histórico detalhado |

Paciência e dinheiro iniciais também podem ser configurados pela classe `Configuracao` no código Python.

## Indicadores

| Métrica | Como interpretar |
| --- | --- |
| Clientes gerados | Todos os visitantes sorteados, inclusive recusados |
| Recusados | Chegaram sem dinheiro para a refeição |
| Atendidos | Receberam a refeição e pagaram |
| Desistências | Entraram na fila, mas perderam a paciência |
| Na fila / em atendimento | Ainda não concluíram a visita no fim da execução |
| Espera média | Média **somente de clientes atendidos**, desde a chegada até começar o atendimento |
| Ocupação | Percentual de minutos disponíveis que os atendentes estiveram ocupados |
| Receita | Moedas recebidas das refeições **efetivamente entregues** |

**Invariante econômico:** a soma do dinheiro de todos os clientes gerados e do caixa da taberna permanece constante. Este modelo não cria dinheiro durante os pagamentos; novas chegadas adicionam participantes e seus saldos iniciais ao universo observado.

## Regras que merecem atenção

- A fila é `collections.deque` e segue FIFO (`append` / `popleft`).
- A decisão de desistir ocorre **antes** de distribuir os atendentes naquele minuto.
- O atendimento iniciado no instante `t` termina em `t + tempo_atendimento`.
- Pagamento somente ocorre na conclusão, **não** quando o cliente entra na fila.
- No fim do horizonte, clientes em fila ou atendimento **não contam** como atendidos ou desistentes.
- A aleatoriedade pertence à instância da simulação (`random.Random`), sem alterar o gerador global.
- Raças são apenas características narrativas. **Não existem vantagens nem preconceitos raciais neste modelo**.

## Para os dois grupos de ABM

### Grupo A: fila de atendimento inspirada no SUS

Reutilize o **raciocínio**, não a história. Troque cliente por paciente, atendente por profissional de saúde e refeição por atendimento. Adicione **classificação de risco** e compare FIFO com uma política clínica de prioridade. Na realidade, atendimentos urgentes não devem seguir apenas uma fila FIFO. Proponha como medir tempo de espera por gravidade, abandono e utilização da equipe.

### Grupo B: mercado financeiro com dois perfis de investidores

Reutilize o **esqueleto de ABM** (`agentes + estado + regras + ticks + métricas + semente`), mas **não reutilize a fila como se fosse um mercado**. Crie investidores **fundamentalistas** (decidem segundo preço versus valor estimado) e **seguidores de tendência** (consideram movimentos anteriores), com um ativo negociável, caixa, quantidade de ativos, ordens e regra explícita de formação de preços. Compare preços, volume e volatilidade. O presente exemplo ilustra somente uma economia de compra e consumo; não simula bolsa de valores.

## O que ficou deliberadamente de fora

Grupos de aventureiros, cozinha e ingredientes, atendimento em fases, turnos, taberna 24 horas, leis do Santuário, vínculos sociais, pagamentos compartilhados, logísticas e painel 2D. Esses temas pertencem ao projeto avançado — introduzi-los aqui esconderia o conceito que a aula pretende ensinar.

## Créditos

A ideia e a direção pedagógica de *A Taberna do Deus Esquecido* são do idealizador do projeto. **ChatGPT (OpenAI, GPT-6)** colaborou na adaptação didática, modelagem, implementação do exemplo, cenários, testes e documentação. Este material foi criado para ensino e deve ser lido, modificado e questionado pelos estudantes.
