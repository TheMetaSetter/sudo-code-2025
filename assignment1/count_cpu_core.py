import os

def count_cpu_cores():
    """
    Counts the number of available CPU cores on the current machine.

    Returns:
        int: The number of CPU cores.
    """
    # os.cpu_count() returns the number of logical CPUs (cores) available.
    return os.cpu_count()

if __name__ == "__main__":
    num_cores = count_cpu_cores()
    print(f"Number of available CPU cores: {num_cores}")