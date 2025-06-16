from _generate_data import run_simulation
from _compute_tests import execute_tests
from _analyze_results import plot_results

import os
import shutil
from datetime import datetime


def clear_and_save_old_files(data_directory):
    files = [f for f in os.listdir(data_directory) if os.path.isfile(os.path.join(data_directory, f))]
    if files:
        # Use the creation time of the first file
        file_date = os.path.getctime(os.path.join(data_directory, files[0]))
        folder_name = datetime.fromtimestamp(file_date).strftime("old from %Y-%m-%d_%H-%M-%S")

        # Create the new folder
        new_folder_path = os.path.join(data_directory, folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Move all files into the new folder
        for file in files:
            src_path = os.path.join(data_directory, file)
            dst_path = os.path.join(new_folder_path, file)
            shutil.move(src_path, dst_path)


if __name__ == "__main__":
    data_directory='src/results/data'
    iterations = 7168 # to have square matrix as results

    clear_and_save_old_files(data_directory)

    run_simulation(iterations, data_directory)
    execute_tests(data_directory)
    plot_results(data_directory)








