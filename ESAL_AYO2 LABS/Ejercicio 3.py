#Problema 3

import math
import random
import statistics
import matplotlib.pyplot as plt


# ==========================================
# 1. CONFIGURACION DEL EXPERIMENTO
# ==========================================

NUM_CIUDADES = 20
NUM_PRUEBAS = 200

# Generar las ciudades con coordenadas reproducibles.
rng = random.Random(42)

ciudades = [
    (rng.uniform(0, 100), rng.uniform(0, 100))
    for _ in range(NUM_CIUDADES)
]


# ==========================================
# 2. CALCULAR DISTANCIA ENTRE DOS CIUDADES
# ==========================================

def distancia(a, b):
    return math.dist(ciudades[a], ciudades[b])


# ==========================================
# 3. CALCULAR LONGITUD TOTAL DE UNA RUTA
# ==========================================

def longitud_ruta(ruta):
    total = 0

    for i in range(len(ruta)):
        ciudad_actual = ruta[i]
        siguiente = ruta[(i + 1) % len(ruta)]

        total += distancia(ciudad_actual, siguiente)

    return total


# ==========================================
# 4. GENERAR SOLUCION ALEATORIA
# ==========================================

def ruta_aleatoria(seed):
    rng = random.Random(seed)

    ruta = list(range(NUM_CIUDADES))
    rng.shuffle(ruta)

    return ruta


# ==========================================
# 5. VECINO MAS CERCANO
# ==========================================

def vecino_mas_cercano(seed):
    rng = random.Random(seed)

    inicio = rng.randrange(NUM_CIUDADES)

    ruta = [inicio]
    no_visitadas = set(range(NUM_CIUDADES))
    no_visitadas.remove(inicio)

    while no_visitadas:

        actual = ruta[-1]

        siguiente = min(
            no_visitadas,
            key=lambda ciudad: distancia(actual, ciudad)
        )

        ruta.append(siguiente)
        no_visitadas.remove(siguiente)

    return ruta


# ==========================================
# 6. ALGORITMO 2-OPT
# ==========================================

def dos_opt(ruta_inicial):
    ruta = ruta_inicial.copy()

    n = len(ruta)
    mejoras = 0

    while True:

        movimiento_encontrado = False

        # Examinar posibles intercambios de aristas.
        for i in range(n - 1):

            for k in range(i + 2, n):

                # Evitar seleccionar las dos aristas
                # que cierran el ciclo y son adyacentes.
                if i == 0 and k == n - 1:
                    continue

                a = ruta[i]
                b = ruta[(i + 1) % n]

                c = ruta[k]
                d = ruta[(k + 1) % n]

                # Cambio de distancia producido por 2-opt.
                cambio = (
                    distancia(a, c)
                    + distancia(b, d)
                    - distancia(a, b)
                    - distancia(c, d)
                )

                # Aceptar el primer movimiento que mejora.
                if cambio < -1e-12:

                    ruta[i + 1:k + 1] = reversed(
                        ruta[i + 1:k + 1]
                    )

                    mejoras += 1
                    movimiento_encontrado = True

                    break

            if movimiento_encontrado:
                break

        # Si no hay mejoras, se alcanzó un óptimo local.
        if not movimiento_encontrado:
            break

    return ruta, mejoras, longitud_ruta(ruta)


# ==========================================
# 7. REALIZAR LOS EXPERIMENTOS
# ==========================================

resultados = {
    "Aleatoria": {
        "mejoras": [],
        "distancias": []
    },
    "Vecino cercano": {
        "mejoras": [],
        "distancias": []
    }
}

for prueba in range(NUM_PRUEBAS):

    # Escenario A: ruta inicial aleatoria.
    inicial_a = ruta_aleatoria(1000 + prueba)

    final_a, mejoras_a, distancia_a = dos_opt(inicial_a)

    resultados["Aleatoria"]["mejoras"].append(mejoras_a)
    resultados["Aleatoria"]["distancias"].append(distancia_a)

    # Escenario B: vecino más cercano desde inicio aleatorio.
    inicial_b = vecino_mas_cercano(2000 + prueba)

    final_b, mejoras_b, distancia_b = dos_opt(inicial_b)

    resultados["Vecino cercano"]["mejoras"].append(mejoras_b)
    resultados["Vecino cercano"]["distancias"].append(distancia_b)


# ==========================================
# 8. MOSTRAR RESULTADOS
# ==========================================

print("\nRESULTADOS DEL EXPERIMENTO")
print("=" * 78)

print(
    f"{'Metodo':<20}"
    f"{'Mejoras promedio':<22}"
    f"{'Distancia promedio':<22}"
    f"{'Mejor distancia':<18}"
)

for metodo, datos in resultados.items():

    promedio_mejoras = statistics.mean(datos["mejoras"])
    promedio_distancia = statistics.mean(datos["distancias"])
    mejor_distancia = min(datos["distancias"])

    print(
        f"{metodo:<20}"
        f"{promedio_mejoras:<22.2f}"
        f"{promedio_distancia:<22.2f}"
        f"{mejor_distancia:<18.2f}"
    )


# ==========================================
# 9. GRAFICA DE CAJA: NUMERO DE MEJORAS
# ==========================================

nombres = ["Aleatoria", "Vecino cercano"]

datos_mejoras = [
    resultados[nombre]["mejoras"]
    for nombre in nombres
]

plt.figure(figsize=(9, 6))

plt.boxplot(
    datos_mejoras,
    tick_labels=nombres,
    showmeans=True
)

plt.ylabel("Número de mejoras aceptadas")
plt.title("2-opt: mejoras necesarias para alcanzar un óptimo local")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("mejoras_2opt.png", dpi=300)
plt.show()


# ==========================================
# 10. GRAFICA DE CAJA: CALIDAD DE LAS RUTAS
# ==========================================

datos_distancias = [
    resultados[nombre]["distancias"]
    for nombre in nombres
]

plt.figure(figsize=(9, 6))

plt.boxplot(
    datos_distancias,
    tick_labels=nombres,
    showmeans=True
)

plt.ylabel("Distancia total de la ruta")
plt.title("2-opt: calidad de los óptimos locales obtenidos")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig("calidad_2opt.png", dpi=300)
plt.show()