#Ejercicio 1
import multiprocessing as mp
import random
import time
try:
    import matplotlib.pyplot as plt  # pyright: ignore[reportMissingModuleSource]
except ImportError:
    plt = None


def estimate_pi(seed: int, samples: int = 1_000_000) -> float:
    """
    Estima pi mediante el método de Monte Carlo.
    Genera puntos aleatorios y cuenta los que caen
    dentro de un cuarto de círculo unitario.
    """
    rng = random.Random(seed)

    inside = sum(
        rng.random()**2 + rng.random()**2 <= 1.0
        for _ in range(samples)
    )

    return 4 * inside / samples


if __name__ == "__main__":

    # Ocho tareas independientes.
    seeds = list(range(8))

    # Cantidad de procesos que se probarán.
    process_counts = [1, 2, 4, 8]

    # Guardar los tiempos y resultados.
    execution_times = []
    pi_estimates = []

    for num_processes in process_counts:

        print(f"\nEjecutando con {num_processes} proceso(s)...")

        start = time.perf_counter()

        with mp.Pool(processes=num_processes) as pool:
            results = pool.map(estimate_pi, seeds)

        elapsed = time.perf_counter() - start

        execution_times.append(elapsed)
        pi_estimates.append(sum(results) / len(results))

        print(f"Tiempo: {elapsed:.4f} segundos")
        print(f"Estimación de pi: {pi_estimates[-1]:.6f}")

    # Calcular la aceleración respecto a la ejecución
    # con un proceso.
    baseline_time = execution_times[0]

    speedups = [
        baseline_time / elapsed
        for elapsed in execution_times
    ]

    # Aceleración ideal: S(p) = p.
    ideal_speedup = process_counts

    # Mostrar resultados en una tabla.
    print("\nRESULTADOS EXPERIMENTALES")
    print("-" * 65)
    print(
        f"{'Procesos':<12}"
        f"{'Tiempo (s)':<15}"
        f"{'Speedup':<15}"
        f"{'Speedup ideal':<15}"
    )

    for p, t, s, ideal in zip(
        process_counts,
        execution_times,
        speedups,
        ideal_speedup
    ):
        print(f"{p:<12}{t:<15.4f}{s:<15.4f}{ideal:<15}")

    # Generar la gráfica.
    plt.figure(figsize=(9, 6))

    plt.plot(
        process_counts,
        speedups,
        marker="o",
        linewidth=2,
        label="Speedup experimental"
    )

    plt.plot(
        process_counts,
        ideal_speedup,
        marker="s",
        linestyle="--",
        linewidth=2,
        label="Speedup ideal"
    )

    plt.xlabel("Número de procesos")
    plt.ylabel("Aceleración (Speedup)")
    plt.title("Aceleración paralela de estimate_pi")
    plt.xticks(process_counts)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig("speedup.png", dpi=300)
    plt.show()

