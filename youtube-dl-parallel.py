from __future__ import unicode_literals

from queue import Queue
from threading import Thread
import youtube_dl
import argparse

'''
This code was based on example from https://www.toptal.com/python/beginners-guide-to-concurrency-and-parallelism-in-python

The idea behind parallelizing is to improve download speed, as youtube limited it
'''

class DownloadWorker(Thread):
    def __init__(self, queue, audio):
        Thread.__init__(self)
        self.queue = queue
        self.audio = audio

    def run(self):
        while True:
            link = self.queue.get()

            try:
                download(link, self.audio)
            finally:
                self.queue.task_done()


def download(link, audio):
    ydl_opts_default = {}

    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    ydl_opts = ydl_opts_audio if audio else ydl_opts_default

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])


def main():
    parser = argparse.ArgumentParser(description='''Youtube downloader based on youtube-dl (https://github.com/ytdl-org/youtube-dl) that utilizes concurrency to maximize download throughput.

Input file should contain links, separated as lines.
    
Example:
https://youtube.com/link1
https://youtube.com/link2''', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('links_file_path', help='Path to file containing links')

    parser.add_argument('--workers', type=int, default=20, help='Number of concurrent downloads.\nDefault value is 20.\nThe optimal value is MAX_DOWNLOAD_SPEED / YOUTUBE_LIMIT.')
    parser.add_argument('--audio', action='store_true', help='Download only audio')

    args = parser.parse_args()

    queue = Queue()

    for x in range(args.workers):
        worker = DownloadWorker(queue, args.audio)
        worker.daemon = True
        worker.start()

    links = open(args.links_file_path, 'r')

    for l in links.readlines():
        queue.put(l)

    # wait for all queue jobs to be processed and exit
    queue.join()


if __name__ == '__main__':
    main()

