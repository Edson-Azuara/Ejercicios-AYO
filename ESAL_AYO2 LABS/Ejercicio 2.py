
import importlib

try:
    plt = importlib.import_module("matplotlib.pyplot")
except ImportError:
    plt = None

# Instancia del problema:
# (nombre, peso, valor)
objetos = [
    ("A", 2, 12),
    ("B", 3, 14),
    ("C", 5, 30),
    ("D", 7, 35),
    ("E", 9, 40)
]

CAPACIDAD = 15


def mochila_voraz(objetos, capacidad, criterio):
    """
    Resuelve una instancia de mochila 0/1 mediante
    un criterio voraz.

    criterio:
        'valor_peso': prioriza mayor valor/peso.
        'menor_peso': prioriza menor peso.
    """

    if criterio == "valor_peso":
        ordenados = sorted(
            objetos,
            key=lambda obj: obj[2] / obj[1],
            reverse=True
        )

    elif criterio == "menor_peso":
        ordenados = sorted(
            objetos,
            key=lambda obj: obj[1]
        )

    else:
        raise ValueError("Criterio desconocido")

    seleccionados = []
    peso_total = 0
    valor_total = 0

    for nombre, peso, valor in ordenados:

        # Comprobar si el objeto cabe en la mochila.
        if peso_total + peso <= capacidad:
            seleccionados.append(nombre)
            peso_total += peso
            valor_total += valor

    return seleccionados, peso_total, valor_total


def mostrar_resultados(nombre, resultado):
    seleccionados, peso, valor = resultado

    print(f"\n{nombre}")
    print("-" * 40)
    print("Objetos seleccionados:", seleccionados)
    print("Peso utilizado:", peso)
    print("Capacidad disponible:", CAPACIDAD)
    print("Espacio restante:", CAPACIDAD - peso)
    print("Valor total:", valor)


if __name__ == "__main__":

    # Ejecutar ambos algoritmos.
    resultado_valor_peso = mochila_voraz(
        objetos, CAPACIDAD, "valor_peso"
    )

    resultado_menor_peso = mochila_voraz(
        objetos, CAPACIDAD, "menor_peso"
    )

    # Mostrar los resultados.
    mostrar_resultados(
        "Método voraz por valor/peso",
        resultado_valor_peso
    )

    mostrar_resultados(
        "Método voraz por menor peso",
        resultado_menor_peso
    )

    # Tabla comparativa.
    print("\nCOMPARACIÓN FINAL")
    print("-" * 75)
    print(
        f"{'Método':<25}"
        f"{'Objetos':<18}"
        f"{'Peso':<10}"
        f"{'Valor':<10}"
    )

    for nombre, resultado in [
        ("Valor/peso", resultado_valor_peso),
        ("Menor peso", resultado_menor_peso)
    ]:
        seleccionados, peso, valor = resultado

        print(
            f"{nombre:<25}"
            f"{str(seleccionados):<18}"
            f"{peso:<10}"
            f"{valor:<10}"
        )

    # Gráfica comparativa (opcional; requiere matplotlib).
    if plt is None:
        print("No se generó la gráfica: instala matplotlib para habilitarla.")
    else:
        nombres = ["Valor/peso", "Menor peso"]

        pesos = [
            resultado_valor_peso[1],
            resultado_menor_peso[1]
        ]

        valores = [
            resultado_valor_peso[2],
            resultado_menor_peso[2]
        ]

        fig, axes = plt.subplots(1, 2, figsize=(11, 5))

        axes[0].bar(nombres, pesos)
        axes[0].axhline(
            CAPACIDAD,
            linestyle="--",
            label=f"Capacidad = {CAPACIDAD}"
        )
        axes[0].set_title("Peso utilizado")
        axes[0].set_ylabel("Peso")
        axes[0].legend()

        axes[1].bar(nombres, valores)
        axes[1].set_title("Valor total obtenido")
        axes[1].set_ylabel("Valor")

        fig.suptitle("Comparación de algoritmos voraces de mochila")
        plt.tight_layout()
        plt.savefig("comparacion_mochila.png", dpi=300)
        plt.show()

