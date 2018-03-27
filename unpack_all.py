import sys
import os
import zipfile
import logging
import subprocess


def unzip_source_zip(source_zip_path, unzip_dir):
    logging.info('Making sure {} dir exists'.format(unzip_dir))
    os.makedirs(unzip_dir, exist_ok=True)
    logging.info('Extracting file {}'.format(source_zip_path))
    with zipfile.ZipFile(source_zip_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)
        root_dir = zip_ref.namelist()[0].strip('/')
        logging.debug('root_dir is {}'.format(root_dir))
    logging.debug('target dir - {}'.format(os.path.join(unzip_dir, root_dir)))
    return os.path.join(unzip_dir, root_dir)


def unzip_source_dir(target_dir):
    os.chdir(target_dir)
    logging.info('Extracting all .war, .ear and .jar under {}'.format(target_dir))
    for root, dirs, files in os.walk(target_dir, topdown=True):
        for f in files:
            absolute_file_name = os.path.join(root, f)
            if f.endswith('.war'):
                extract_dir = os.path.join(root, os.path.splitext(f)[0]) + '_war'
                os.makedirs(extract_dir, exist_ok=True)
                logging.debug('Found .war file: {}'.format(absolute_file_name))
                logging.debug('Extracting {} to {}'.format(absolute_file_name, extract_dir))
                subprocess.check_call(['unzip', '-d', extract_dir, absolute_file_name])
            elif f.endswith('.ear'):
                extract_dir = os.path.join(root, os.path.splitext(f)[0]) + '_ear'
                os.makedirs(extract_dir, exist_ok=True)
                logging.debug('Found .ear file: {}'.format(absolute_file_name))
                logging.debug('Extracting {} to {}'.format(absolute_file_name, extract_dir))
                subprocess.check_call(['jar', '-xf', absolute_file_name, '-C', extract_dir])
            elif f.endswith('.jar'):
                extract_dir = os.path.join(root, os.path.splitext(f)[0]) + '_jar'
                os.makedirs(extract_dir, exist_ok=True)
                logging.debug('Found .jar file: {}'.format(absolute_file_name))
                logging.debug('Extracting {} to {}'.format(absolute_file_name, extract_dir))
                subprocess.check_call(['jar', '-xf', absolute_file_name, '-C', extract_dir])


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    source_zip_path = sys.argv[1]
    unzip_dir = sys.argv[2]
    source_dir = unzip_source_zip(source_zip_path, unzip_dir)
    unzip_source_dir(source_dir)