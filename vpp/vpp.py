
import sys
import os.path
import json
from gi.repository import Gtk, GObject
from dbus.mainloop.glib import DBusGMainLoop
from switchprint.switch_board import SwitchBoard
from switchprint.printer_interface import PrinterInterface
from .slicing import pdq_print_job


class PrinterWrapper(PrinterInterface):
    def __init__(self, *args, **kwargs):
        self.heater_bar = None
        self.progress_bar = None
        self.job_ready = False
        self.job_started = False
        self.temps = {"tool":None, "bed":None}
        self.output_path = None
        PrinterInterface.__init__(self, *args, **kwargs)

    def on_report(self, blob):
        data = json.loads(blob)

        def get_fraction(reading, thermistor):
            # also saves the fractional values for use elsewhere
            value, target = reading
            if target is None:
                self.temps[thermistor] = None
                return 0.0
            else:
                progress = max(min(value/target, 1.0), 0.0)
                self.temps[thermistor] = progress
                return progress

        tool_data = data["thermistors"]["tools"][0]
        bed_data = data["thermistors"]["bed"]
        tool = get_fraction(tool_data, "tool")
        bed = get_fraction(bed_data, "bed")

        combined = tool
        if bed_data[1] is not None:
            combined = (combined + bed) / 2.0

        if self.heater_bar:
            self.heater_bar.set_fraction(combined)
            self.heater_bar.set_text(
                "Nozzle: {0}, Bed: {1}".format(
                    tool_data[0], bed_data[0]))

        if self.job_ready and not self.job_started:
            self.try_start_job()

    def try_start_job(self):
        self.job_ready = True
        if self.temps["tool"] > .999 and not self.job_started:
            if self.temps["bed"] is None or self.temps["bed"] > .999:
                # lets do this
                self.job_started = True
                self.pdq_request_print(self.output_path)

    def warm_up(self):
        self.home()
        self.motors_off()
        self.set_tool_temp(0, 190)
        self.set_bed_temp(45)

    def cool_down(self):
        self.home(True, False, False)
        self.motors_off()
        self.set_tool_temp(0, 0)
        self.set_bed_temp(0)

    def connect(self, heater_bar, progress_bar):
        self.heater_bar = heater_bar
        self.progress_bar = progress_bar

    def on_pdq_print_progress(self, progress):
        self.progress_bar.set_fraction(float(progress)/100.0)

    def on_pdq_print_complete(self):
        # finally!
        self.progress_bar.set_fraction(1.0)
        self.cool_down()
        #Gtk.main_quit(*args)
    

class DemoHandler(SwitchBoard):
    def __init__(self, builder):
        self.builder = builder
        self.printer = None
        self.print_started = False
        self.job_ready = False
        self.output_path = None
        SwitchBoard.__init__(self, PrinterWrapper)

    def on_new_printer(self, printer):
        if not self.printer:
            print "Connected printer: %s" % printer.uuid
            heater_bar = self.builder.get_object("heater_progress")
            progress_bar = self.builder.get_object("job_progress")
            self.printer = printer
            self.printer.connect(heater_bar, progress_bar)
            self.printer.motors_off()
            if self.print_started:
                self.printer.warm_up()
                if self.job_ready:
                    self.printer.try_start_job()
                
    def onDeleteWindow(self, *args):
        #Gtk.main_quit(*args)
        pass

    def onCancel(self, *args):
        Gtk.main_quit(*args)

    def onPrint(self, *args):
        self.print_started = True
        print "Init print demo! :D"

        settings = self.builder.get_object("smoke_and_mirrors")
        progress = self.builder.get_object("print_progress")
        status_bar = self.builder.get_object("slice_progress")
        settings.destroy()
        progress.show_all()

        def on_slice_complete(output_path):
            # called by slic3r thread
            self.printer.output_path = self.output_path = output_path
            def callback():
                # called by main thread
                self.job_ready = True
                if self.printer:
                    self.printer.try_start_job()
                return False # ensures this is only scheduled once
            GObject.idle_add(callback)

        print_args = [on_slice_complete, status_bar]
        if len(sys.argv) == 2:
            print_args.append(sys.argv[1])

        # start slicing job
        pdq_print_job(*print_args)

        # warm up printer
        self.printer.warm_up()

    def onStopJob(self, *args):
        Gtk.main_quit(*args)


def populate_printer_list(builder):
    columns = ["Printer", "Location", "Status"]
    data = [
        ["Print to file", "", ""],

        ["Lulzbot TAZ", "", "Ready!"],
        ["Lulzbot AO-101", "", "Offline"],
        ["Generic Reprap", "", "Offline"],
    ]

    store = Gtk.ListStore(str, str, str)
    for row in data:
        store.append(row)

    tree = builder.get_object("printer_treeview")
    tree.set_model(store)
    renderer = Gtk.CellRendererText()

    for column in columns:
        tree.append_column(Gtk.TreeViewColumn(column, renderer))

    # ok... this doesn't quite work, but whatever.


def gui_main(*args):
    DBusGMainLoop(set_as_default=True)
    builder = Gtk.Builder()
    glade_path = os.path.abspath(
        os.path.join(__file__, "..", "print_dialog.glade"))
    builder.add_from_file(glade_path)
    builder.connect_signals(DemoHandler(builder))

    window = builder.get_object("smoke_and_mirrors")
    window.show_all()

    populate_printer_list(builder)
    
    Gtk.main()
