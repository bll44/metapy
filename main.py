import logging
import argparse
import os
from mutagen.mp4 import MP4, MP4Tags, MutagenError
import time
import json

config = None
with open('config', 'r') as f:
    config = json.loads(f.read())

_logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s> %(message)s'))
_logger.setLevel(logging.INFO)
_logger.addHandler(ch)


_args = None

def scan_meta():
    _logger.debug('Valid extensions: %s' % config['extensions'])
    with open(os.path.abspath(os.path.join(__file__, '..', 'directories.txt'))) as f:
        directories = [line.rstrip() for line in f.readlines()]
    for d in directories:
        _logger.info('Scanning directory %s' % d)
        for filename in os.listdir(d):
            path, ext = os.path.splitext(os.path.join(d, filename))
            if ext in config['extensions']:
                try:
                    _logger.info('Checking file: %s' % filename)
                    data = filename.split('-')
                    name = data[2].strip()
                    name = name.replace(ext, '')
                    _logger.debug('NAME: %s' % name)
                    mp4file = MP4(os.path.join(d, filename))
                    try:
                        meta_name = mp4file['\xa9nam'][0]
                        _logger.debug('META NAME: %s' % meta_name)
                    except KeyError:
                        _logger.debug('Meta name for "%s" does not exist, setting to None' % filename)
                        meta_name = None
                    if name != meta_name or meta_name is None:
                        mp4file['\xa9nam'][0] = name
                        _logger.debug('Name was %s, changed to %s' % (meta_name, name))
                    MP4.save(mp4file)
                except MutagenError as e:
                    _logger.info('Failed to save the file: %s' % filename)
                    _logger.error(e)
                except IndexError:
                    _logger.warning('Skipping file %s' % filename)
                    pass
        _logger.info('Completed scan of %s' % d)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Enable verbose logging',
                        action='store_true', dest='v')
    parser.add_argument('--perpetual', help='Enable perpetual directory scanning',
                        action='store_true', dest='perpetual')
    parser.add_argument('-i', '--interval', help='Set the interval to scan directories at (seconds)[default = 5]',
                        type=int, dest='i')

    _args = parser.parse_args()

    if _args.v:
        _logger.setLevel(logging.DEBUG)

    if _args.perpetual:
        _logger.info('Perpetual mode enabled')
        while True:
            scan_meta()
            if _args.i:
                time.sleep(_args.i)
            else:
                time.sleep(5)
    else:
        scan_meta()

if __name__ == '__main__':
    main()