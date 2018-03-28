import sys
import os
import logging


def find_files(search_dir, str_pattern):
    file_list = []
    os.chdir(search_dir)
    for root, dirs, files in os.walk(search_dir, topdown=True):
        for file in files:
            if file.endswith('.java'):
                for line in file:
                    if str_pattern in line:
                        file_list.append(file)
    return file_list



if __name__ == '__main__':
    logger = logging.getLogger('find_constants_usage')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    search_dir = sys.argv[1]
    str_pattern = sys.argv[2]
    find_files(search_dir, str_pattern)