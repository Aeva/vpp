
import time
from threading import Thread
from subprocess import Popen, PIPE, STDOUT


SLICER = "/home/aeva/repraps/slic3r/bin/slic3r"
CONFIG = "/home/aeva/repraps/configs/ao_mod/hairspray_fine_solid_black_pla.ini"
SOURCE = "/home/aeva/library/models/calibration/hollow_cube.stl"


class Slic3rListener(Thread):
    def __init__(self, callback, status_bar, model_path, config_path):
        """
        Seems silly to wrap a subprocess with a thread, but the purpose is
        here is to listen for when slic3r finishes various stages of
        the slicing process so that it may trigger gtk events etc.
        """

        self.callback = callback
        self.model_path = model_path
        self.config_path = config_path
        self.status_bar = status_bar
        Thread.__init__(self)

    def run(self):
        args = (SLICER, "--load", self.config_path, self.model_path)
        proc = Popen(args, stdout=PIPE, stderr=STDOUT)
        # this list is derrived from Slic3r/lib/Slic3r/Print.pm
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
            "Generating support material",
            "Generating skirt",
            "Exporting G-code",
            "Running post-processing scripts",
            ]
        complete = False

        def get_step(line):
            #hack :P
            for label in labels:
                if line.startswith(label):
                    return labels.index(label)
            print "ERRROR", line

        output_file = None

        while proc.poll() is None:
            line = proc.stdout.readline().strip()
            print line
            if line.startswith("Done."):
                self.status_bar.set_text("Complete")
                self.status_bar.set_fraction(100.0)
                complete = True
            elif not complete:
                step = get_step(line[3:])
                if labels[step] == "Exporting G-code":
                    chaf, path = line.split("Exporting G-code to")
                    output_file = path.strip()
                percent = 100/(len(labels)+1)*step
                self.status_bar.set_text(labels[step])
                self.status_bar.set_fraction(percent/100.0)
            time.sleep(.01)
        if self.callback:
            self.callback(output_file)


def pdq_print_job(callback, status_bar, source=SOURCE, config=CONFIG):
    slic3r = Slic3rListener(callback, status_bar, source, config)
    slic3r.start()

