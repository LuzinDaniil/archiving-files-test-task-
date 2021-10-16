import os
import shutil
import time
from datetime import datetime, timedelta
import zipfile
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, filename="./service.log")

DEPTH_DIRECTORY = 3


class Transfer:
    def __init__(self):
        self.path_storage = os.getenv('STORAGE', './storage')
        self.path_archive = os.getenv('ARCHIVE', './archive')
        self.min_free_space_percent = 10
        self.aging_time = timedelta(days=90)
        self.file_extension = ['waw', 'mp3']

    def run(self):
        while True:
            if self.is_lack_of_space():
                data_now = datetime.now()
                self._archive(data_now - self.aging_time)
            time.sleep(1)

    def is_lack_of_space(self):
        total, used, free = shutil.disk_usage("/")
        return True if self.min_free_space_percent > ((free * 100) / total) else False

    def _archive(self, less_date):
        old_files = self._get_list_directory_with_condition(self.path_storage, less_date)
        for directory_file, files in old_files.items():
            self._archiving_files(directory_file, files)

    def _archiving_files(self, directory, files):
        if directory[0] == '/':
            directory = directory[1:]
        for file in files:
            os.makedirs(os.path.join(self.path_archive, directory), exist_ok=True)
            with zipfile.ZipFile(os.path.join(self.path_archive, directory,
                                              '{}.zip'.format(os.path.basename(file))), mode='a') as archive:
                try:
                    archive.write(file, os.path.basename(file))
                    os.remove(file)
                    logging.info(f"Файл {file} перенесен и заархивирован")
                except Exception:
                    logging.error('Файл {} не получилось добавить в архив'.format(file))

    def _get_list_directory_with_condition(self, path, less_date):
        files_to_archive = {}
        for root, dirs, files in os.walk(path):
            storage_directory = root[len(path):]
            if storage_directory.count(os.sep) == DEPTH_DIRECTORY:
                date_directory = storage_directory.split('/')[1:]
                if all([True if date.isdigit() else False for date in date_directory]):
                    year, month, day = map(int, date_directory)
                    if datetime(year=year, month=month, day=day) < less_date:
                        files_day = []
                        for file in files:
                            if file.split('.')[-1] in self.file_extension:
                                files_day.append(os.path.join(root, file))
                        if files_day:
                            files_to_archive[storage_directory] = files_day

        return files_to_archive


if __name__ == '__main__':
    Transfer().run()

