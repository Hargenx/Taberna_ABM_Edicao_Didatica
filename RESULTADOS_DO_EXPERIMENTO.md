# Experimento demonstrativo: quantidade de atendentes

O script `examples/comparar_cenarios.py` executa cinco sementes pareadas (`21, 42, 84, 123, 456`) por configuração, com:

- 180 ticks, 1 tick = 1 minuto;
- chance de chegada de 0,80 por minuto;
- tempo fixo de serviço de 5 minutos;
- preço de 20 moedas por refeição;
- mesmas distribuições iniciais de dinheiro, paciência e raças.

| Atendentes | Atendidos (média) | Desistências (média) | Receita (média) | Espera dos atendidos (média, min) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 35,6 | 72,2 | 712,0 | 6,45 |
| 2 | 70,2 | 37,4 | 1.404,0 | 4,30 |
| 3 | 99,6 | 9,4 | 1.992,0 | 2,11 |
| 4 | 110,2 | 0,6 | 2.204,0 | 0,29 |

**Interpretação:** neste cenário, mais atendentes reduziram congestionamento e desistências, permitindo mais refeições entregues e aumentando a receita. Isso é resultado de um modelo sintético; não equivale a dados de um hospital nem de um negócio real. Receita não considera salários ou custos de ingredientes. A comparação entre cinco sementes não constitui teste inferencial de superioridade.

## Verificações executadas

- 17 testes automatizados com `unittest`: aprovados.
- Compilação com `compileall`: aprovada.
- Simulações de 100 e 1.440 ticks com sementes 21, 42 e 84: concluídas com invariantes íntegros.
- Ruff e mypy: não executados por não estarem instalados no ambiente.
