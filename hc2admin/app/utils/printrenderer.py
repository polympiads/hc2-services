
import os
import random
import string
import tempfile
import subprocess

import time

from telemetry.traces import get_tracer
import logging

tracer = get_tracer("print.renderer")
logger = logging.getLogger("print.renderer")

def read_bytes (file: str):
    with open(file, "rb") as f:
        return f.read()
def write_bytes (file: str, b: bytes):
    with open(file, "wb") as f:
        f.write(b)
def write (file: str, content: str):
    with open(file, "w") as f:
        f.write(content)

def find_random_file (dir: str, name_format: str):
    for i in range(1000):
        rng = ''.join([ random.choice(string.ascii_letters) for _ in range(16) ])

        file = name_format.format(rng)
        path = os.path.join(dir, file)
        if os.path.exists(path): continue

        return file
    assert False, f"Maybe the name format is wrong {name_format}"

def render_template (id: str, name: str, location: str, code: str):
    with tracer.start_as_current_span("render_template") as span:
        span.set_attribute("print.id", id)
        span.set_attribute("print.name", name)
        span.set_attribute("print.location", location)

        file = __file__
        dir  = os.path.dirname(file)
        if not dir.endswith('/'):
            dir = dir + '/'
        
        with tempfile.TemporaryDirectory(prefix=dir + "/") as ndir:
            logger.info(f"Storing into {ndir}")

            write(os.path.join(ndir, "code"), code)
            write(os.path.join(ndir, "id"), id)
            write(os.path.join(ndir, "name"), name)
            write(os.path.join(ndir, "location"), location)
            write(os.path.join(ndir, "teamparams"), f"{id} ({location}) - {name}")

            write_bytes(os.path.join(ndir, "main.tex"), read_bytes(os.path.join(dir, "template.tex")))

            with tracer.start_as_current_span("Compiling PDF"):
                logging.info("Starting pdflatex")
                subprocess.run([ "pdflatex", "-no-shell-escape", "main.tex" ], cwd=ndir, stdout=subprocess.DEVNULL)

            tar_dir = os.path.join(os.path.dirname(os.path.dirname(dir)), "bucket")
            os.makedirs(tar_dir, exist_ok = True)
            tar_fle = find_random_file(tar_dir, "printout{}.pdf")
            tar_pth = os.path.join(tar_dir, tar_fle)
            try:
                logging.info(f"Trying to copy the PDF into {tar_fle}")
                span.set_attribute("print.target", tar_fle)
                write_bytes( tar_pth, read_bytes(os.path.join(ndir, "main.pdf")) )
            except IOError:
                logging.critical("Could not copy the pdf into the bucket folder")

            return tar_fle
