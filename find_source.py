import sys
import os


def find_files(search_dir, str_pattern):
    file_list = []
    os.chdir(search_dir)
    for root, dirs, files in os.walk(search_dir, topdown=True):
        for file in files:
            if file.endswith('.java'):
                absolute_path = os.path.join(root, file)
                with open(absolute_path, 'r', encoding='latin-1') as file_handle:
                    for line in file_handle:
                        if str_pattern in line:
                            file_list.append(absolute_path)
                            break
    return file_list


if __name__ == '__main__':

    search_dir = sys.argv[1]
    str_pattern = sys.argv[2]
    l = [print(f) for f in find_files(search_dir, str_pattern)]
