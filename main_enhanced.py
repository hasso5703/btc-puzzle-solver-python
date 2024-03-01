import argparse
import multiprocessing
import os
import re
from bit import Key
import pandas as pd
import random
import time
from pathlib import Path
import sys

seed = time.time()
random.seed(seed)

DIR_DATA = Path('data')  # ENTER YOUR DATA DIRECTORY PATH HERE
DATA_FILE = Path(DIR_DATA, 'puzzles_data.csv')
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError as error:
    print("Le fichier spécifié n'a pas été trouvé :", error)
    print("Changez le chemin du dossier 'data' dans le code : ")
    print("-> -> -> DIR_DATA = Path(r'/Users/you/project/example/data') <- <- <-")
    sys.exit()
except pd.errors.ParserError as error:
    print("Erreur de lecture du fichier CSV :", error)
    sys.exit()


def valid_hex_range(option):
    match = re.fullmatch(r'([0-9a-fA-F]+):([0-9a-fA-F]+)', option)
    if match:
        return match.groups()
    raise argparse.ArgumentTypeError(f'Invalid hex range: {option}')


def worker(start_range, end_range, target_address, output_file, process_id, found_flag):
    hex_count = 0
    start_time = time.perf_counter()
    while True:
        i = random.randint(start_range, end_range)
        priv_key_hex = format(i, 'x').zfill(64)
        key = Key.from_hex(priv_key_hex)
        address = key.address
        hex_count += 1

        if address == target_address:
            print(f'\nPrivate Key: {priv_key_hex}, Address: {address}')
            result_string = f'Private Key: {priv_key_hex}, Address: {address}\n'
            with open(output_file, 'a') as f:
                f.write(result_string)
            found_flag.value = True
            for _ in range(5):
                os.system("say 'résolu, trouvé'")
            break

        # Print the progress every 20000 keys
        if hex_count % 100000 == 0:
            elapsed_time = time.perf_counter() - start_time
            elapsed_time = elapsed_time if elapsed_time > 0 else 1
            formatted_time = f'{int(elapsed_time // 3600)}:{int((elapsed_time % 3600) // 60):02d}:{int(elapsed_time % 60):02d}'
            formatted_hex_count = f'{hex_count:,}'.replace(',', '.')
            keys_per_second = hex_count / elapsed_time
            formatted_kps = format_keys_per_second(keys_per_second)
            change_count_str = ''
            display_key_hex = priv_key_hex.lstrip('0')
            display_key_hex = display_key_hex if display_key_hex else '0'  # ensure at least one zero remains if all zeros were stripped
            print(
                f'\r[Process {process_id}] {change_count_str} [Scanned {formatted_hex_count} keys in {formatted_time}] [{formatted_kps} Keys/s.] [Current Hex: {display_key_hex}]',
                end='')
        i += 1


def format_keys_per_second(kps):
    if kps < 1e3:
        return f"{kps:.2f}"
    elif kps < 1e6:
        return f"{kps / 1e3:.2f}K"
    elif kps < 1e9:
        return f"{kps / 1e6:.2f}M"
    else:
        return f"{kps / 1e9:.2f}B"


def load_data(puzzle_number: int) -> dict:
    df_ligne_puzzle = df.loc[df.puzzle_number == puzzle_number]
    hex = str(df_ligne_puzzle.hex.iloc[0])
    start_key = str(df_ligne_puzzle.start_key.iloc[0])
    stop_key = str(df_ligne_puzzle.stop_key.iloc[0])
    try:
        start_range = int(start_key, 16)
        stop_range = int(stop_key, 16)
    except ValueError as error:
        print("Error during conversion from hex to integer ! : ", error)
        print("start_key:", start_key)
        print("stop_key:", stop_key)
        print("Vérifier ces données, peut-être mal entré dans le fichier csv !")
        return {}

    print("Target : ", hex)
    print("Start_key : ", start_key)
    print("Stop_key: ", stop_key)
    print("Start_range : ", start_range)
    print("Stop_range : ", stop_range)

    return {
        'hex': hex,
        'start_key': start_key,
        'stop_key': stop_key,
        'start_range': start_range,
        'stop_range': stop_range
    }


def choisir_puzzle(nb=-1):
    while not 1 <= nb <= 160:
        try:
            nb = int(input("Veuillez entrer un numero de puzzle (entre 1 et 160) :"))
        except ValueError:
            print("Ce n'est pas un entier valide. Veuillez réessayer.")
    return nb


def verifier_numero_puzzle(nb_puzzle):
    return nb_puzzle in list(set(df["puzzle_number"]))


if __name__ == '__main__':
    nb_puzzle = choisir_puzzle()
    print("=" * 15, "BTC PUZZLE SOLVER", "=" * 15)
    print("Puzzle choisi : ", nb_puzzle)
    if not verifier_numero_puzzle(nb_puzzle):
        print("=" * 30)
        print("Pas de données trouvée pour le puzzle ", nb_puzzle)
        print("Ajoutez les données de ce puzzle à la fin du fichier csv !")
        print("Exemple : (séparer par des virgules) 'puzzle_number','hex','start_key','stop_key'")
        print("'126','1AWCLZAjKbV1P7AHvaPNCKiB7ZWVDMxFiz','20000000000000000000000000000000',"
              "'3fffffffffffffffffffffffffffffff'")
        print("Ou (avec les zéros) : ")
        print("'126','1AWCLZAjKbV1P7AHvaPNCKiB7ZWVDMxFiz',"
              "'0000000000000000000000000000000020000000000000000000000000000000',"
              "'000000000000000000000000000000003fffffffffffffffffffffffffffffff'")
        print("=" * 30)
        print("Liste des puzzles disponibles : ")
        print(sorted(list(set(df.puzzle_number))))
        sys.exit()
    else:
        data = load_data(nb_puzzle)
    print("Mode de recherche : Random")
    print("=" * 30)
    found_flag = multiprocessing.Value('i', 0)
    num_processes = multiprocessing.cpu_count()
    processes = []
    print("Nombre de coeurs cpu disponibles : ", num_processes)
    nb = -1
    while not 1 <= nb <= num_processes:
        try:
            nb = int(input(f"Veuillez entrer le nombre de coeurs à utiliser (entre 1 et {str(num_processes)}) : "))
        except ValueError:
            print("Ce n'est pas un entier valide. Veuillez réessayer.")
    print("-" * 30)
    num_processes = nb
    print("Nombre de coeurs choisi :", num_processes)
    print("-" * 30)
    start_range = data["start_range"]
    stop_range = data["stop_range"]
    target = data["hex"]
    nb_possibilite = stop_range - start_range
    nb_possibilite_formate = '{:,}'.format(nb_possibilite).replace(',', ' ')
    print("Nombre de possibilités : ", nb_possibilite_formate)
    print("-" * 30)
    print("Début de la recherche ! :")
    total_range = stop_range - start_range
    step = total_range // num_processes
    for i in range(num_processes):
        sub_start = start_range + int(i * step)
        sub_end = start_range + int((i + 1) * step) if i < (num_processes - 1) else stop_range
        print(f"range process {i} : ", sub_start, " -> ", sub_end)
        process = multiprocessing.Process(target=worker, args=(
            sub_start, sub_end, target, str(Path(DIR_DATA) / ("puzzle_" + str(nb_puzzle) + ".txt")), i, found_flag))
        processes.append(process)
        process.start()

    while not found_flag.value:
        time.sleep(10)  # Attendez une seconde avant de vérifier à nouveau
    for process in processes:
        process.terminate()  # Arrêtez tous les processus

    for process in processes:
        process.join()

    print("\nSuccessfully finished.")
