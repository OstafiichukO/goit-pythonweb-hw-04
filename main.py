import argparse
import asyncio
import logging
import os
from pathlib import Path
import shutil
from aiofiles import open as aio_open
from aiofiles.os import mkdir
from aiofiles.os import makedirs
from aiofiles.os import path as aiopath

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def copy_file(file_path: Path, output_folder: Path):
    try:
        extension = file_path.suffix.lstrip(".").lower() or "no_extension"
        destination_folder = output_folder / extension

        if not await aiopath.exists(destination_folder):
            await makedirs(destination_folder, exist_ok=True)

        destination_file = destination_folder / file_path.name
        async with aio_open(file_path, 'rb') as src_file:
            async with aio_open(destination_file, 'wb') as dest_file:
                while True:
                    chunk = await src_file.read(1024 * 1024)
                    if not chunk:
                        break
                    await dest_file.write(chunk)

        logger.info(f"Файл {file_path} успішно скопійовано до {destination_folder}")
    except Exception as e:
        logger.error(f"Помилка під час копіювання файлу {file_path}: {e}")

async def read_folder(source_folder: Path, output_folder: Path):
    try:
        for item in source_folder.rglob("*"):
            if item.is_file():
                await copy_file(item, output_folder)
    except Exception as e:
        logger.error(f"Помилка під час читання папки {source_folder}: {e}")

async def main(source_folder: str, output_folder: str):
    source_path = Path(source_folder)
    output_path = Path(output_folder)

    if not source_path.exists():
        logger.error(f"Вихідна папка {source_folder} не існує.")
        return

    if not output_path.exists():
        await mkdir(output_path)

    await read_folder(source_path, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument("source_folder", help="Шлях до вихідної папки, яку потрібно відсортувати.")
    parser.add_argument("output_folder", help="Шлях до цільової папки, куди будуть скопійовані файли.")

    args = parser.parse_args()

    try:
        asyncio.run(main(args.source_folder, args.output_folder))
    except Exception as e:
        logger.error(f"Помилка під час виконання: {e}")
