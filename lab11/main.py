"""Entry point demonstrativ pentru lab11."""

from lab11.factorial import factorial, parallel_factorial_multiprocessing, parallel_factorial_futures
from lab11.pipeline import count_words


def main() -> None:
    values = [5, 6, 7, 8]

    print("=== Factorial paralel ===\n")

    print("Factoriale individuale:")
    for n in values:
        print(f"  {n}! = {factorial(n)}")

    print("\nCu multiprocessing.Queue + Process:")
    res_mp = parallel_factorial_multiprocessing(values)
    for n in sorted(res_mp):
        print(f"  {n}! = {res_mp[n]}")

    print("\nCu ProcessPoolExecutor:")
    res_fut = parallel_factorial_futures(values)
    for n in sorted(res_fut):
        print(f"  {n}! = {res_fut[n]}")

    print("\n=== Pipeline fișiere ===\n")
    print(f"count_words('ana are mere'): {count_words('ana are mere')}")


if __name__ == "__main__":
    main()
