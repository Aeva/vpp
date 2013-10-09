
import time
from threading import Thread
from subprocess import Popen, PIPE, STDOUT


SLICER = "/home/aeva/repraps/slic3r/bin/slic3r"
CONFIG = "/home/aeva/repraps/configs/ao_mod/hairspray_translucent_pla.ini"
SOURCE = "/home/aeva/library/models/calibration/hollow_cube.stl"


class Slic3rListener(Thread):
    def __init__(self, status_bar, model_path, config_path):
        """
        Seems silly to wrap a subprocess with a thread, but the purpose is
        here is to listen for when slic3r finishes various stages of
        the slicing process so that it may trigger gtk events etc.
        """

        self.model_path = model_path
        self.config_path = config_path
        self.status_bar = status_bar
        Thread.__init__(self)

    def run(self):
        args = (SLICER, "--load", self.config_path, self.model_path)
        proc = Popen(args, stdout=PIPE, stderr=STDOUT)
        labels = [
            "Processing triangulated mesh",
            "Simplifying input",
            "Generating perimeters",
            "Detecting solid surfaces",
            "Preparing infill surfaces",
            "Detect bridges",
            "Generating horizontal shells",
            "Combining infill",
            "Infilling layers",
            "Generating skirt",
            "Exporting G-code",
            ]
        count = -1
        complete = False

        while proc.poll() is None:
            line = proc.stdout.readline().strip()
            count += 1
            percent = 100/(len(labels))*count
            print line

            if count < len(labels):
                self.status_bar.set_text(labels[count])

            if line.startswith("Done") or complete:
                self.status_bar.set_text("Complete")
                complete = True
                percent = 100

            self.status_bar.set_fraction(percent/100.0)


            time.sleep(.01)



def pdq_print_job(status_bar, source=SOURCE, config=CONFIG):
    slic3r = Slic3rListener(status_bar, source, config)
    slic3r.start()

