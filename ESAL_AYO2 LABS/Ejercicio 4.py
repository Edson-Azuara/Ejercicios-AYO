# Ejercicio 4
import math
import random
import time
import statistics
import matplotlib.pyplot as plt


# ==========================================
# CONFIGURACION DEL EXPERIMENTO
# ==========================================

NUM_CIUDADES = 20
NUM_ITERACIONES = 5000
NUM_PRUEBAS = 20

TEMPERATURA_INICIAL = 10.0
TEMPERATURA_FINAL = 0.01

# Generar las mismas ciudades para ambos esquemas
generador = random.Random(42)

ciudades = [
    (generador.uniform(0, 100),
     generador.uniform(0, 100))
    for _ in range(NUM_CIUDADES)
]


# ==========================================
# CALCULO DE DISTANCIAS
# ==========================================

def distancia(a, b):
    """Distancia euclidiana entre dos ciudades."""
    x1, y1 = ciudades[a]
    x2, y2 = ciudades[b]

    return math.hypot(x2 - x1, y2 - y1)


def costo_ruta(ruta):
    """Distancia total, incluyendo el regreso al origen."""
    total = 0

    for i in range(len(ruta)):
        siguiente = (i + 1) % len(ruta)

        total += distancia(ruta[i], ruta[siguiente])

    return total


# ==========================================
# MOVIMIENTO 2-OPT
# ==========================================

def movimiento_2opt(ruta, rng):
    """
    Selecciona dos aristas y propone invertir
    el segmento comprendido entre ellas.
    """

    n = len(ruta)

    i = rng.randrange(n - 1)
    k = rng.randrange(i + 1, n)

    # Evitar elegir las dos aristas que se cierran
    # sobre la misma ruta completa.
    if i == 0 and k == n - 1:
        return None, None

    a = ruta[i]
    b = ruta[(i + 1) % n]
    c = ruta[k]
    d = ruta[(k + 1) % n]

    # Cambio de costo al sustituir las dos aristas.
    delta = (
        distancia(a, c)
        + distancia(b, d)
        - distancia(a, b)
        - distancia(c, d)
    )

    nueva_ruta = ruta[:]
    nueva_ruta[i + 1:k + 1] = reversed(
        nueva_ruta[i + 1:k + 1]
    )

    return nueva_ruta, delta


# ==========================================
# ESQUEMAS DE ENFRIAMIENTO
# ==========================================

def calcular_temperatura(
    iteracion,
    esquema,
    temperatura_inicial,
    temperatura_final,
    total_iteraciones
):
    progreso = iteracion / total_iteraciones

    if esquema == "lineal":
        return (
            temperatura_inicial
            + (temperatura_final - temperatura_inicial)
            * progreso
        )

    elif esquema == "exponencial":
        return temperatura_inicial * (
            temperatura_final / temperatura_inicial
        ) ** progreso

    else:
        raise ValueError("Esquema de enfriamiento desconocido.")


# ==========================================
# ALGORITMO SIMULATED ANNEALING
# ==========================================

def recocido_simulado(esquema, semilla):

    rng = random.Random(semilla)

    # Crear una ruta inicial aleatoria.
    ruta_actual = list(range(NUM_CIUDADES))
    rng.shuffle(ruta_actual)

    costo_actual = costo_ruta(ruta_actual)

    # Guardar la mejor solución encontrada.
    mejor_ruta = ruta_actual[:]
    mejor_costo = costo_actual

    historial = []
    movimientos_aceptados = 0

    inicio = time.perf_counter()

    for iteracion in range(NUM_ITERACIONES):

        temperatura = calcular_temperatura(
            iteracion,
            esquema,
            TEMPERATURA_INICIAL,
            TEMPERATURA_FINAL,
            NUM_ITERACIONES
        )

        # Proponer un movimiento 2-opt.
        nueva_ruta, delta = movimiento_2opt(
            ruta_actual, rng
        )

        if nueva_ruta is not None:

            nuevo_costo = costo_actual + delta

            # Aceptar siempre una mejora.
            if delta < 0:
                aceptar = True

            # Una solución peor puede aceptarse.
            else:
                probabilidad = math.exp(
                    -delta / max(temperatura, 1e-12)
                )

                aceptar = rng.random() < probabilidad

            if aceptar:
                ruta_actual = nueva_ruta
                costo_actual = nuevo_costo
                movimientos_aceptados += 1

                # Actualizar la mejor solución.
                if costo_actual < mejor_costo:
                    mejor_costo = costo_actual
                    mejor_ruta = ruta_actual[:]

        # Registrar la mejor distancia encontrada.
        if iteracion % 50 == 0:
            historial.append(
                (iteracion, temperatura, mejor_costo)
            )

    tiempo = time.perf_counter() - inicio

    return {
        "esquema": esquema,
        "ruta": mejor_ruta,
        "costo": mejor_costo,
        "tiempo": tiempo,
        "aceptados": movimientos_aceptados,
        "historial": historial
    }


# ==========================================
# EXPERIMENTOS
# ==========================================

resultados = {
    "lineal": [],
    "exponencial": []
}

for esquema in resultados:

    print("\nEjecutando esquema:", esquema)

    for prueba in range(NUM_PRUEBAS):

        resultado = recocido_simulado(
            esquema,
            semilla=1000 + prueba
        )

        resultados[esquema].append(resultado)

        print(
            f"Prueba {prueba + 1:02d}: "
            f"Costo = {resultado['costo']:.2f}, "
            f"Tiempo = {resultado['tiempo']:.5f} s"
        )


# ==========================================
# RESUMEN ESTADISTICO
# ==========================================

print("\n========== RESUMEN FINAL ==========")

for esquema, pruebas in resultados.items():

    costos = [r["costo"] for r in pruebas]
    tiempos = [r["tiempo"] for r in pruebas]

    print(f"\nEsquema: {esquema}")
    print(f"Costo promedio: {statistics.mean(costos):.2f}")
    print(f"Mejor costo: {min(costos):.2f}")
    print(f"Peor costo: {max(costos):.2f}")
    print(f"Tiempo promedio: {statistics.mean(tiempos):.5f} s")


# ==========================================
# GRAFICA 1: CURVAS DE CONVERGENCIA
# ==========================================

plt.figure(figsize=(10, 6))

for esquema, pruebas in resultados.items():

    # Promediar los costos de las 20 pruebas.
    longitudes = [
        len(r["historial"]) for r in pruebas
    ]

    n_puntos = min(longitudes)

    costos_promedio = []

    for i in range(n_puntos):
        valores = [
            r["historial"][i][2]
            for r in pruebas
        ]

        costos_promedio.append(
            statistics.mean(valores)
        )

    iteraciones = [
        pruebas[0]["historial"][i][0]
        for i in range(n_puntos)
    ]

    plt.plot(
        iteraciones,
        costos_promedio,
        label=esquema.capitalize()
    )

plt.xlabel("Iteraciones")
plt.ylabel("Mejor distancia encontrada")
plt.title("Convergencia del Recocido Simulado")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("convergencia_sa.png", dpi=300)
plt.show()


# ==========================================
# GRAFICA 2: TIEMPO VS CALIDAD
# ==========================================

plt.figure(figsize=(9, 6))

for esquema, pruebas in resultados.items():

    tiempos = [r["tiempo"] for r in pruebas]
    costos = [r["costo"] for r in pruebas]

    plt.scatter(
        tiempos,
        costos,
        label=esquema.capitalize(),
        alpha=0.7
    )

plt.xlabel("Tiempo de ejecución (segundos)")
plt.ylabel("Distancia final")
plt.title("Tiempo de ejecución vs calidad de la solución")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("tiempo_vs_calidad_sa.png", dpi=300)
plt.show()


# ==========================================
# GRAFICA 3: TIEMPO PROMEDIO
# ==========================================

esquemas = list(resultados.keys())

tiempos_promedio = [
    statistics.mean(
        [r["tiempo"] for r in resultados[e]]
    )
    for e in esquemas
]

plt.figure(figsize=(8, 5))
plt.bar(esquemas, tiempos_promedio)

plt.xlabel("Esquema de enfriamiento")
plt.ylabel("Tiempo promedio (segundos)")
plt.title("Comparación del tiempo de ejecución")
plt.tight_layout()
plt.savefig("tiempo_promedio_sa.png", dpi=300)
plt.show()


# ==========================================
# MEJOR RUTA ENCONTRADA
# ==========================================

for esquema, pruebas in resultados.items():

    mejor = min(pruebas, key=lambda r: r["costo"])

    print(f"\nMejor ruta con enfriamiento {esquema}:")
    print("Ruta:", mejor["ruta"])
    print(f"Distancia: {mejor['costo']:.2f}")