# Ejercicio 5
import math
import random
import itertools
import statistics
import time
import matplotlib.pyplot as plt


# ==================================================
# CONFIGURACION DEL EXPERIMENTO
# ==================================================

NUM_INSTANCIAS = 100
NUM_CIUDADES = 9

ITERACIONES_SA = 1500

# Coordenadas en el plano: de 0 a 100.
SEMILLA_INSTANCIAS = 5000


# ==================================================
# DISTANCIAS Y COSTO DE UNA RUTA
# ==================================================

def crear_matriz_distancias(ciudades):
    n = len(ciudades)

    D = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            x1, y1 = ciudades[i]
            x2, y2 = ciudades[j]

            D[i][j] = math.hypot(
                x2 - x1,
                y2 - y1
            )

    return D


def costo_ruta(ruta, D):
    """
    Calcula la distancia total de una ruta,
    incluyendo el regreso a la ciudad inicial.
    """

    total = 0.0
    n = len(ruta)

    for i in range(n):
        siguiente = (i + 1) % n
        total += D[ruta[i]][ruta[siguiente]]

    return total


# ==================================================
# OPTIMO EXACTO POR FUERZA BRUTA
# ==================================================

def tsp_optimo_exacto(D):
    """
    Fija la ciudad 0 como origen y evalúa
    todas las permutaciones de las restantes.
    """

    n = len(D)
    mejor_costo = float("inf")
    mejor_ruta = None

    for permutacion in itertools.permutations(
        range(1, n)
    ):
        ruta = (0,) + permutacion
        costo = costo_ruta(ruta, D)

        if costo < mejor_costo:
            mejor_costo = costo
            mejor_ruta = ruta

    return list(mejor_ruta), mejor_costo


# ==================================================
# MST: ARBOL DE EXPANSION MINIMA
# ==================================================

def construir_mst(D, inicio=0):
    """
    Construye un MST mediante el algoritmo de Prim.
    Devuelve una lista de adyacencia del árbol.
    """

    n = len(D)

    incluido = [False] * n
    mejor = [float("inf")] * n
    padre = [-1] * n

    mejor[inicio] = 0.0

    for _ in range(n):

        u = min(
            (i for i in range(n) if not incluido[i]),
            key=lambda i: mejor[i]
        )

        incluido[u] = True

        for v in range(n):

            if not incluido[v] and D[u][v] < mejor[v]:

                mejor[v] = D[u][v]
                padre[v] = u

    # Convertir el árbol a lista de adyacencia.
    adyacencia = [[] for _ in range(n)]

    for v in range(n):

        if padre[v] != -1:

            u = padre[v]

            adyacencia[u].append(v)
            adyacencia[v].append(u)

    return adyacencia


# ==================================================
# RECORRIDO PREORDEN DEL MST
# ==================================================

def ruta_mst(D, inicio=0):
    """
    Recorre el MST mediante DFS y visita cada ciudad
    una sola vez, omitiendo visitas repetidas.
    """

    arbol = construir_mst(D, inicio)

    visitadas = set()
    ruta = []

    def dfs(u):

        visitadas.add(u)
        ruta.append(u)

        for v in sorted(arbol[u]):

            if v not in visitadas:
                dfs(v)

    dfs(inicio)

    return ruta


# ==================================================
# BUSQUEDA LOCAL 2-OPT
# ==================================================

def dos_opt(ruta, D):
    """
    Busca la mejor mejora 2-opt disponible
    y repite hasta alcanzar un óptimo local.
    """

    ruta = ruta[:]
    n = len(ruta)

    while True:

        mejor_delta = -1e-12
        mejor_par = None

        for i in range(n - 1):

            for k in range(i + 1, n):

                # Evitar invertir la ruta completa
                # y conservar el mismo ciclo.
                if i == 0 and k == n - 1:
                    continue

                a = ruta[i]
                b = ruta[(i + 1) % n]

                c = ruta[k]
                d = ruta[(k + 1) % n]

                delta = (
                    D[a][c]
                    + D[b][d]
                    - D[a][b]
                    - D[c][d]
                )

                if delta < mejor_delta:

                    mejor_delta = delta
                    mejor_par = (i, k)

        # No existen movimientos que mejoren la ruta.
        if mejor_par is None:
            break

        i, k = mejor_par

        ruta[i + 1:k + 1] = reversed(
            ruta[i + 1:k + 1]
        )

    return ruta


# ==================================================
# RECOCIDO SIMULADO
# ==================================================

def recocido_simulado(
    D,
    semilla,
    iteraciones=ITERACIONES_SA
):

    rng = random.Random(semilla)
    n = len(D)

    # Ruta inicial aleatoria.
    actual = list(range(n))
    rng.shuffle(actual)

    costo_actual = costo_ruta(actual, D)

    mejor_ruta = actual[:]
    mejor_costo = costo_actual

    T0 = 10.0
    Tf = 0.01

    for it in range(iteraciones):

        # Enfriamiento exponencial.
        progreso = it / iteraciones

        temperatura = T0 * (
            Tf / T0
        ) ** progreso

        # Proponer un movimiento 2-opt.
        i = rng.randrange(n - 1)
        k = rng.randrange(i + 1, n)

        if i == 0 and k == n - 1:
            continue

        a = actual[i]
        b = actual[(i + 1) % n]

        c = actual[k]
        d = actual[(k + 1) % n]

        delta = (
            D[a][c]
            + D[b][d]
            - D[a][b]
            - D[c][d]
        )

        # Aceptar siempre las mejoras.
        if delta < 0:

            aceptar = True

        else:

            probabilidad = math.exp(
                -delta / max(temperatura, 1e-12)
            )

            aceptar = rng.random() < probabilidad

        if aceptar:

            actual[i + 1:k + 1] = reversed(
                actual[i + 1:k + 1]
            )

            costo_actual += delta

            if costo_actual < mejor_costo:

                mejor_costo = costo_actual
                mejor_ruta = actual[:]

    return mejor_ruta


# ==================================================
# EXPERIMENTOS
# ==================================================

resultados = []

inicio_total = time.perf_counter()

for instancia in range(NUM_INSTANCIAS):

    rng = random.Random(
        SEMILLA_INSTANCIAS + instancia
    )

    # Generar nueve ciudades.
    ciudades = [
        (
            rng.uniform(0, 100),
            rng.uniform(0, 100)
        )
        for _ in range(NUM_CIUDADES)
    ]

    D = crear_matriz_distancias(ciudades)

    # ----------------------------------------------
    # 1. Solucion optima exacta
    # ----------------------------------------------

    _, costo_optimo = tsp_optimo_exacto(D)

    # ----------------------------------------------
    # 2. MST puro
    # ----------------------------------------------

    t0 = time.perf_counter()

    r_mst = ruta_mst(D)
    c_mst = costo_ruta(r_mst, D)

    tiempo_mst = time.perf_counter() - t0

    # ----------------------------------------------
    # 3. MST + 2-opt
    # ----------------------------------------------

    t0 = time.perf_counter()

    r_mst_2opt = dos_opt(r_mst, D)
    c_mst_2opt = costo_ruta(r_mst_2opt, D)

    tiempo_mst_2opt = time.perf_counter() - t0

    # ----------------------------------------------
    # 4. Busqueda local desde ruta aleatoria
    # ----------------------------------------------

    t0 = time.perf_counter()

    rng_local = random.Random(7000 + instancia)

    r_local = list(range(NUM_CIUDADES))
    rng_local.shuffle(r_local)

    r_local = dos_opt(r_local, D)
    c_local = costo_ruta(r_local, D)

    tiempo_local = time.perf_counter() - t0

    # ----------------------------------------------
    # 5. Recocido simulado
    # ----------------------------------------------

    t0 = time.perf_counter()

    r_sa = recocido_simulado(
        D,
        semilla=9000 + instancia
    )

    c_sa = costo_ruta(r_sa, D)

    tiempo_sa = time.perf_counter() - t0

    # ----------------------------------------------
    # Guardar resultados
    # ----------------------------------------------

    resultados.append({
        "instancia": instancia + 1,
        "optimo": costo_optimo,

        "mst": c_mst,
        "mst_2opt": c_mst_2opt,
        "local": c_local,
        "sa": c_sa,

        "ratio_mst": c_mst / costo_optimo,
        "ratio_mst_2opt": c_mst_2opt / costo_optimo,

        "tiempo_mst": tiempo_mst,
        "tiempo_mst_2opt": tiempo_mst_2opt,
        "tiempo_local": tiempo_local,
        "tiempo_sa": tiempo_sa
    })

    print(
        f"Instancia {instancia + 1:03d}/{NUM_INSTANCIAS} "
        f"| Optimo: {costo_optimo:.2f} "
        f"| MST: {c_mst:.2f} "
        f"| MST+2opt: {c_mst_2opt:.2f} "
        f"| Local: {c_local:.2f} "
        f"| SA: {c_sa:.2f}"
    )

tiempo_total = time.perf_counter() - inicio_total


# ==================================================
# RESUMEN ESTADISTICO
# ==================================================

metodos = {
    "MST puro": "mst",
    "MST + 2-opt": "mst_2opt",
    "Busqueda local": "local",
    "Recocido simulado": "sa"
}

print("\n========== RESUMEN DE COSTOS ==========")

for nombre, clave in metodos.items():

    costos = [r[clave] for r in resultados]

    print(f"\n{nombre}")
    print(f"Costo promedio: {statistics.mean(costos):.4f}")
    print(f"Costo minimo:   {min(costos):.4f}")
    print(f"Costo maximo:   {max(costos):.4f}")

    razones = [
        costo / r["optimo"]
        for costo, r in zip(costos, resultados)
    ]

    print(
        f"Razon promedio respecto al optimo: "
        f"{statistics.mean(razones):.4f}"
    )

ratios = [r["ratio_mst"] for r in resultados]

print("\n========== RAZON DE APROXIMACION MST ==========")
print(f"Razon minima: {min(ratios):.4f}")
print(f"Razon promedio: {statistics.mean(ratios):.4f}")
print(f"Razon maxima: {max(ratios):.4f}")
print(f"Limite teorico: 2.0000")

print(
    "Instancias que superan 2:",
    sum(r > 2 + 1e-9 for r in ratios)
)

print(f"\nTiempo total del experimento: {tiempo_total:.2f} s")


# ==================================================
# GRAFICA 1: HISTOGRAMA DE RAZONES
# ==================================================

plt.figure(figsize=(9, 6))

plt.hist(
    ratios,
    bins=15,
    edgecolor="black"
)

plt.axvline(
    2.0,
    linestyle="--",
    linewidth=2,
    label="Limite teorico = 2"
)

plt.xlabel("Razon de aproximacion: C_MST / C_optimo")
plt.ylabel("Frecuencia")
plt.title("Distribucion de la razon de aproximacion del MST")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("razon_aproximacion_mst.png", dpi=300)
plt.show()


# ==================================================
# GRAFICA 2: RAZON POR INSTANCIA
# ==================================================

plt.figure(figsize=(10, 6))

plt.scatter(
    range(1, NUM_INSTANCIAS + 1),
    ratios,
    alpha=0.75
)

plt.axhline(
    2.0,
    linestyle="--",
    linewidth=2,
    label="Limite teorico = 2"
)

plt.xlabel("Instancia")
plt.ylabel("Razon de aproximacion")
plt.title("Razon de aproximacion del MST en 100 instancias")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("dispersion_razon_mst.png", dpi=300)
plt.show()


# ==================================================
# GRAFICA 3: BOXPLOT DE COSTOS
# ==================================================

datos_costos = [
    [r["mst"] for r in resultados],
    [r["mst_2opt"] for r in resultados],
    [r["local"] for r in resultados],
    [r["sa"] for r in resultados]
]

plt.figure(figsize=(10, 6))

plt.boxplot(
    datos_costos,
    tick_labels=[
        "MST puro",
        "MST + 2-opt",
        "Busqueda local",
        "Recocido simulado"
    ]
)

plt.ylabel("Costo total de la ruta")
plt.title("Comparacion de costos en 100 instancias")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("comparacion_costos_tsp.png", dpi=300)
plt.show()


# ==================================================
# GRAFICA 4: COSTO PROMEDIO
# ==================================================

promedios = [
    statistics.mean(r["mst"] for r in resultados),
    statistics.mean(r["mst_2opt"] for r in resultados),
    statistics.mean(r["local"] for r in resultados),
    statistics.mean(r["sa"] for r in resultados)
]

plt.figure(figsize=(9, 6))

plt.bar(
    [
        "MST puro",
        "MST + 2-opt",
        "Busqueda local",
        "Recocido simulado"
    ],
    promedios
)

plt.ylabel("Costo promedio")
plt.title("Costo promedio por algoritmo")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("promedio_costos_tsp.png", dpi=300)
plt.show()