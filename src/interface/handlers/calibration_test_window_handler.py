# Default library imports
import src.utilities.wiimotelib as wbblib
import src.utilities.wbb_calitera as wbb
import numpy as np
from gi.repository import Gtk, Gdk, GLib
import sys
import math
import cairo

# Third party imports
import gi

gi.require_version("Gtk", "3.0")

# Local imports

DT = 50
SAMPLE = 100
MEAN_SAMPLE = 100


class Monitor:
    """docstring for Monitor"""

    def __init__(self, monitor):
        self.width, self.height = (
            monitor.get_geometry().width,
            monitor.get_geometry().height,
        )
        self.x, self.y = monitor.get_geometry().x, monitor.get_geometry().y
        self.mm_size = (monitor.get_width_mm(), monitor.get_height_mm())
        self.center = Position(self.width // 2, self.height // 2)

    def __str__(self):
        return f"Res: {self.width, self.height}\nGeo: {self.x, self.y}\nmm_size: {self.mm_size}\nCenter: {self.center}"


class Position:
    """docstring for Position"""

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x, self.y}"


class ImageSurface:
    """docstring for ImageSurface"""

    def __init__(self, img):
        self.img = img
        self.pos = Position()

    def __str__(self):
        return f"{self.pos}"

    def set_position(self, x, y):
        self.pos.x = x - self.img.get_width() // 2
        self.pos.y = y - self.img.get_height() // 2


class Handler:
    """This class implements Los Window Handler"""

    def __init__(self, window):
        self.window = window
        self.default_target = ImageSurface(
            cairo.ImageSurface.create_from_png("media/target.png")
        )
        self.calibrated_target = ImageSurface(
            cairo.ImageSurface.create_from_png("media/target1.png")
        )
        self.default_weight = 0.0
        self.calibrated_weight = 0.0
        self.history = np.zeros(100)
        self.history_best = 1
        self.history_cursor = -1
        self.zeroed_weight = 0.0

    def on_show(self, window):
        """
        This method handles show event
        """
        self.x_mean, self.y_mean = 0.0, 0.0
        self.i = 0
        self.default_weight, self.calibrated_weight = 0.0, 0.0
        self.set_monitor()
        self.set_line_pos(self.monitor.width, self.monitor.height)
        self.set_signals()
        cal = self.window.app.wiimote.get_balance_cal()
        self.calibrations = dict()
        for i, sensor in enumerate(
            ("right_top", "right_bottom", "left_top", "left_bottom")
        ):
            self.calibrations[sensor] = cal[i]

        self.on_mean = True
        self.id = GLib.timeout_add(DT, self.get_mean)

    def set_monitor(self):
        screen = self.window.get_screen()
        display = screen.get_display()
        n = 0 if display.get_n_monitors() == 1 else 1
        monitor = display.get_monitor(n)
        self.monitor = Monitor(monitor)
        self.window.fullscreen_on_monitor(screen, n)

    def set_signals(self):
        self.window.drawing_area.connect("draw", self.on_draw)
        self.window.connect("key-press-event", self.on_key_press)

    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval).upper()
        if key == "ESCAPE":
            GLib.source_remove(self.id)
            self.window.hide()

    def set_line_pos(self, width, height):
        front = Position(width // 2, 0)
        right = Position(width, self.monitor.center.y)
        rear = Position(width // 2, height)
        left = Position(0, self.monitor.center.y)

        self.line_pos = [front, right, rear, left]

    def get_tara(self):
        dx = np.zeros(4)
        readings = dict()
        for j, sensor in enumerate(
            ("right_top", "right_bottom", "left_top", "left_bottom")
        ):
            readings[sensor] = self.window.app.calibration[sensor][0]

        for j, sensor in enumerate(
            ("right_top", "right_bottom", "left_top", "left_bottom")
        ):
            dx[j] = wbb.gsc(readings, sensor, self.calibrations, wbb.escala_eu)
        tara = dx.sum()
        return tara / 100

    def get_mean(self):
        """Calculates the mean of center of pressure (cop)"""
        if self.i < MEAN_SAMPLE:
            # Gets wbb readings
            readings = wbb.captura1(self.window.app.wiimote)
            # Gets CoP
            cop_x, cop_y = wbb.calCoP(
                readings, self.window.app.device.calibrations, wbb.escala_eu
            )

            self.default_weight += wbb.calcWeight(
                readings, self.calibrations, wbb.escala_eu
            )
            self.calibrated_weight += wbb.calcWeight(
                readings, self.window.app.calibration, wbb.escala_eu
            )

            self.x_mean += cop_x
            self.y_mean += cop_y
            self.i += 1
            return True
        else:
            self.on_mean = False
            self.x_mean /= MEAN_SAMPLE
            self.y_mean /= MEAN_SAMPLE

            self.default_weight /= MEAN_SAMPLE
            self.default_weight -= self.get_tara()
            self.calibrated_weight /= MEAN_SAMPLE

            self.id = GLib.timeout_add(DT, self.get_data)
            return False

    def get_data(self):
        # Get wbb readings
        readings = wbb.captura1(self.window.app.wiimote)
        # Get CoP
        def_cop_x, def_cop_y = wbb.calCoP_(readings, self.calibrations, wbb.escala_eu)
        cal_cop_x, cal_cop_y = wbb.calCoP_(
            readings, self.window.app.calibration, wbb.escala_eu
        )
        # Convert cop to screen pos
        def_cop_x, def_cop_y = self.cop_to_pos(
            def_cop_x, def_cop_y, self.x_mean, self.y_mean
        )
        cal_cop_x, cal_cop_y = self.cop_to_pos(
            cal_cop_x, cal_cop_y, self.x_mean, self.y_mean
        )
        self.default_target.set_position(def_cop_x, def_cop_y)
        self.calibrated_target.set_position(cal_cop_x, cal_cop_y)
        self.window.drawing_area.queue_draw()
        return True

    def on_draw(self, widget, cr):
        # cr = widget.get_window().cairo_create()

        cr.set_source_rgb(0.75, 0.75, 0.75)
        cr.paint()

        cr.set_line_width(5)
        cr.set_source_rgb(0.25, 0.25, 0.25)
        for pos in self.line_pos:
            cr.move_to(pos.x, pos.y)
            cr.line_to(self.monitor.center.x, self.monitor.center.y)
            cr.stroke()

        cr.set_source_surface(
            self.default_target.img,
            self.default_target.pos.x,
            self.default_target.pos.y,
        )
        cr.paint()

        cr.set_source_surface(
            self.calibrated_target.img,
            self.calibrated_target.pos.x,
            self.calibrated_target.pos.y,
        )
        cr.paint()

        if not self.on_mean:
            cr.set_source_rgb(1, 0, 0)
            cr.move_to(self.monitor.width - 100, self.monitor.height - 110)
            cr.show_text(str(self.calibrated_weight))

            cr.set_source_rgb(0, 0, 0)
            cr.move_to(self.monitor.width - 100, self.monitor.height - 100)
            cr.show_text(str(self.default_weight))

    def cop_to_pos(self, x, y, x_med=0, y_med=0):
        """Converts center of pressure (cop) to screen position

        Parameters
        ----------
        x: float
            cop position on wiimote x-axis
        y: float
            cop position on wiimote y-axis

        Returns
        -------
        tuple
            cop position on the screen
        """
        X = 433 / 2  # mm
        Y = -1 * 238 / 2  # mm

        xpos = ((x - x_med) / X) * self.monitor.center.x + self.monitor.center.x
        ypos = ((y - y_med) / Y) * self.monitor.center.y + self.monitor.center.y

        return (xpos, ypos)

    def on_delete_event(self, window, event):
        print("\n\n\n{}\n\n\n".format(self.id))
        GLib.source_remove(self.id)
        window.hide()
        return True

    def on_reset_button_clicked(self, button: Gtk.Button):
        """
        This method handles reset button click

        Parameters
        ----------
        button : Gtk.Button
            The button
        """
        GLib.source_remove(self.id)
        self.x_mean, self.y_mean = 0.0, 0.0
        self.i = 0
        self.on_mean = True
        self.default_weight, self.calibrated_weight = 0.0, 0.0
        self.id = GLib.timeout_add(DT, self.get_mean)

    def connect_balance_board(self, was_just_connected, readings):
        self.zeroed_weight = 0.0
        if was_just_connected:
            count_max = 100
        else:
            count_max = 50
        for init_weight_count in range(1, count_max + 1):
            weight = wbblib.calcWeight(readings, calibrations)
            if weight == 0.0 or weight < -200:
                break
            self.zeroed_weight += weight
        self.zeroed_weight /= init_weight_count

        # start with half full quality bar
        self.history_cursor = self.history_best = len(self.history) // 2
        for i in range(len(self.history)):
            if i > self.history_cursor:
                self.history[i] = 0.0
            else:
                self.history[i] = self.zeroed_weight

    def board_timer_tick(self, readings, calibrations):
        # Cálculo do peso
        kg = wbblib.calcWeight(readings, calibrations)

        # Somatório do histórico
        history_sum = 0.0
        # Máximo
        max_hist = kg
        # Mínimo
        min_hist = kg
        # Máxima diferença
        max_diff = 0.0

        # Peso menor que -200kg
        if kg < -200:
            self.connect_balance_board(False, readings)
            return

        # Cursor do histórico (índice)
        self.history_cursor += 1
        # Preenche o array de histórico com o peso corrente
        self.history[self.history_cursor % len(self.history)] = kg

        # Percorre o vetor de histórico
        for self.history_best in range(len(self.history)):
            history_entry = self.history[
                (self.history_cursor + len(self.history) - self.history_best)
                % len(self.history)
            ]
            if abs(max_hist - history_entry) > 1.0:
                break
            if abs(min_hist - history_entry) > 1.0:
                break
            if history_entry > max_hist:
                max_hist = history_entry
            if history_entry < min_hist:
                min_hist = history_entry

            diff = max(
                abs(history_entry - kg),
                abs((history_sum + history_entry) / (self.history_best + 1) - kg),
            )
            if diff > max_diff:
                max_diff = diff
            if diff > 1.0:
                break
            history_sum += history_entry

        kg = history_sum / self.history_best - self.zeroed_weight

        accuracy = 1.0 / self.history_best
        kg = math.floor(kg / accuracy + 0.5) * accuracy

        return kg

    def btn_reset_click(self):
        # history_sum = 0.
        # for i in range(self.history_best):
        #   history_sum += self.history[(self.history_cursor + len(self.history) - i) % len(self.history)]
        # return history_sum / self.history_best
        pass
