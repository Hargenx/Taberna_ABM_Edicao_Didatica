"""Experimento A/B: o que muda quando contratamos mais atendentes?

Execute a partir da raiz do projeto:
    python -m examples.comparar_cenarios
"""

from taberna_didatica import Configuracao, Taberna


def executar_cenario(atendentes: int, semente: int) -> tuple[int, int, int, float]:
    config = Configuracao(
        minutos=180,
        semente=semente,
        quantidade_atendentes=atendentes,
        chance_chegada=0.80,
        tempo_atendimento=5,
    )
    r = Taberna(config).executar()
    return r.atendidos, r.desistencias, r.receita, r.espera_media


def main() -> None:
    print("Comparação de capacidade — sementes pareadas")
    print("Atendentes | Atendidos (média) | Desistências (média) | Receita (média) | Espera (média)")
    for atendentes in (1, 2, 3, 4):
        medicoes = [executar_cenario(atendentes, seed) for seed in (21, 42, 84, 123, 456)]
        medias = [sum(valores) / len(valores) for valores in zip(*medicoes)]
        print(
            f"{atendentes:^10} | {medias[0]:^16.1f} | {medias[1]:^19.1f} | "
            f"{medias[2]:^13.1f} | {medias[3]:^13.2f}"
        )
    print("\nNota: receita não é lucro; o modelo não inclui salários nem custos de ingredientes.")


if __name__ == "__main__":
    main()
