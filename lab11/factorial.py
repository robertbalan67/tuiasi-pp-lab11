"""
Calcul factorial paralel cu multiprocessing.Queue + Process
și cu concurrent.futures.ProcessPoolExecutor.
"""

from __future__ import annotations
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed


# ─── Funcție de bază ──────────────────────────────────────────────────────────

def factorial(n: int) -> int:
    """Calculează n! iterativ. factorial(0) = factorial(1) = 1."""
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# ─── Worker (module-level — necesar pentru pickling pe Windows) ───────────────

def _worker_factorial(input_queue: multiprocessing.Queue,
                      output_queue: multiprocessing.Queue) -> None:
    """Consumă valori din input_queue, calculează n!, trimite în output_queue."""
    while True:
        n = input_queue.get()
        if n is None:          # sentinel de oprire
            break
        output_queue.put((n, factorial(n)))


# ─── Implementări paralele ────────────────────────────────────────────────────

def parallel_factorial_multiprocessing(values: list[int]) -> dict[int, int]:
    """
    Calculează factorialele în paralel cu 4 procese și multiprocessing.Queue.

    Arhitectură:
      1. input_queue + output_queue
      2. 4 procese Process(target=_worker_factorial)
      3. toate valorile → input_queue
      4. None × 4 → input_queue (semnale de oprire)
      5. colectare rezultate din output_queue
    """
    num_workers = 4
    input_queue:  multiprocessing.Queue = multiprocessing.Queue()
    output_queue: multiprocessing.Queue = multiprocessing.Queue()

    processes = [
        multiprocessing.Process(
            target=_worker_factorial,
            args=(input_queue, output_queue)
        )
        for _ in range(num_workers)
    ]

    for p in processes:
        p.start()

    # Trimitem valorile de procesate
    for v in values:
        input_queue.put(v)

    # Semnale de oprire — unul per worker
    for _ in range(num_workers):
        input_queue.put(None)

    # Colectăm exact len(values) rezultate
    results: dict[int, int] = {}
    for _ in values:
        n, fact = output_queue.get()
        results[n] = fact

    for p in processes:
        p.join()

    return results


def parallel_factorial_futures(values: list[int]) -> dict[int, int]:
    """
    Calculează factorialele în paralel cu ProcessPoolExecutor (max_workers=4).

    Fiecare valoare este trimisă ca job separat; rezultatele se colectează
    pe măsură ce se termină (as_completed).
    """
    results: dict[int, int] = {}
    with ProcessPoolExecutor(max_workers=4) as executor:
        # Mapăm fiecare future la valoarea sa de intrare
        future_to_n = {executor.submit(factorial, n): n for n in values}
        for future in as_completed(future_to_n):
            n = future_to_n[future]
            results[n] = future.result()
    return results
