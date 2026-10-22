"""Execute com: python -m taberna_didatica --ajuda (ou --help)."""

import argparse

from .modelo import Configuracao, Taberna


def main() -> None:
    parser = argparse.ArgumentParser(description="ABM didático de uma taberna de fantasia")
    parser.add_argument("--minutos", type=int, default=120)
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--atendentes", type=int, default=2)
    parser.add_argument("--chegada", type=float, default=0.65, help="Chance por minuto, de 0 a 1")
    parser.add_argument("--tempo-atendimento", type=int, default=4)
    parser.add_argument("--preco", type=int, default=20, help="Moedas por refeição")
    parser.add_argument("--eventos", action="store_true", help="Mostra o diário dos agentes")
    args = parser.parse_args()

    configuracao = Configuracao(
        minutos=args.minutos,
        semente=args.semente,
        quantidade_atendentes=args.atendentes,
        chance_chegada=args.chegada,
        tempo_atendimento=args.tempo_atendimento,
        preco_refeicao=args.preco,
    )
    taberna = Taberna(configuracao)
    resultado = taberna.executar()

    if args.eventos:
        print("\nDIÁRIO DE EVENTOS")
        print("\n".join(taberna.eventos))

    print("\n=== TABERNA ABM — EDIÇÃO DIDÁTICA ===")
    print(f"Tempo:                 {resultado.minutos} minutos")
    print(f"Clientes gerados:      {resultado.gerados}")
    print(f"Recusados (sem verba): {resultado.recusados}")
    print(f"Atendidos:             {resultado.atendidos}")
    print(f"Desistências:          {resultado.desistencias}")
    print(f"Ainda na fila:         {resultado.na_fila}")
    print(f"Em atendimento:        {resultado.em_atendimento}")
    print(f"Espera média atendidos:{resultado.espera_media:7.2f} min")
    print(f"Ocupação atendentes:   {resultado.utilizacao_atendentes:6.1f}%")
    print(f"Receita:               {resultado.receita} moedas")


if __name__ == "__main__":
    main()
