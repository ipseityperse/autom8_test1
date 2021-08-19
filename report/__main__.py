from . import *
import os, threading, time

def thread(pdf):
    print(f"Scanning {pdf['type']} in {pdf['region']}")
    Scanner(path=pdf['path'], save=True, template=PDF_REPORT_TYPES[pdf['type']],
        output_filename=f"{pdf['region']} - {pdf['type']}",
        output_path=f"{output}\\{(SCANNER_OUTPUT_IN_FOLDERS and pdf['region'] or '/')}")

path = input("Path to reports dictionary: ")
output = input("Output dictionary: ")
pdfs = Discover(path).pdfs
threads = []
ts = time.time()

for pdf in pdfs:
    threads.append(threading.Thread(
        target=thread,
        args=(pdf,)))
    threads[-1].start()

for t in threads:
    t.join()

print(f'Compleated in {time.time() - ts} seconds using {len(threads)} threads')
