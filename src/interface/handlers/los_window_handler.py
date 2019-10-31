# Default library imports
import sys
import math
import cairo

# Third party imports
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import numpy as np
from random import shuffle

# Local imports
import src.utilities.wbb_calitera as wbb
import src.utilities.calculos_los as calc_los

RADIUS = 15
LOS_SAMPLE = 200
MEAN_SAMPLE = LOS_SAMPLE // 2
RETURN_SAMPLE = 25
DT = 40

class Monitor():
    """docstring for Monitor"""
    def __init__(self, monitor):
        self.width, self.height = monitor.get_geometry().width, monitor.get_geometry().height
        self.x, self.y = monitor.get_geometry().x, monitor.get_geometry().y
        self.mm_size = (monitor.get_width_mm(), monitor.get_height_mm())
        self.center = Position(self.width//2, self.height//2)

    def __str__(self):
        return f"width: {self.width}\nheight: {self.height}\n\nx: {self.x}\ny: {self.y}\n\nmm_size: {self.mm_size}\n\ncenter: {self.center}\n"


class Position():
    """docstring for Position"""
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x}, {self.y}"

    def get_pos(self):
        return (self.x, self.y)


class ImageSurface():
    """docstring for ImageSurface"""
    def __init__(self, img):
        self.img = img
        self.pos = Position()

    def set_position(self, x, y):
        self.pos.x = x - self.img.get_width()//2
        self.pos.y = y - self.img.get_height()//2


class Handler():
    """This class implements Los Window Handler
    """

    def __init__(self, window):
        self.window = window
        # self.yellow = ImageSurface(cairo.ImageSurface.create_from_png("media/yellow_target.png"))
        self.yellow = ImageSurface(cairo.ImageSurface.create_from_png("media/yellow.png"))
        # self.green = ImageSurface(cairo.ImageSurface.create_from_png("media/green_target.png"))
        self.green = ImageSurface(cairo.ImageSurface.create_from_png("media/red.png"))
        self.target = ImageSurface(cairo.ImageSurface.create_from_png("media/ball.png"))

    def on_show(self, window):
        '''
        This method handles show event
        '''
        self.mean = True
        self.dynamic_cop_x = np.zeros((8, LOS_SAMPLE))
        self.dynamic_cop_y = np.zeros((8, LOS_SAMPLE))
        self.x_mean, self.y_mean = 0., 0.
        self.i, self.j = 0, 0
        self.cur_pos = list(range(8))
        # shuffle(self.cur_pos)
        self.cur_pos = self.outersperse(self.cur_pos, 8)
        self.set_monitor()
        self.cur_line = Position(self.monitor.center.x, self.monitor.center.y)
        diff = (self.monitor.width-self.monitor.height)//2
        self.set_line_pos(diff)
        self.set_signals()
        self.init_los()
        self.a, self.b, self.r = self.window.app.amplitude
        # self.a *= 10
        # self.b *= 10
        # self.r *= 10
        self.center_counter = 0

    def set_monitor(self):
        display = self.window.get_screen().get_display()
        monitors = list()
        for i in range(display.get_n_monitors()):
            monitors.append(Monitor(display.get_monitor(i)))

        self.monitor = monitors[-1]
        self.window.move(self.monitor.x, self.monitor.y)

    def set_signals(self):
        self.window.drawing_area.connect('draw', self.on_draw)
        self.window.connect('key-press-event', self.on_key_press)

    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval).upper()
        if key == 'ESCAPE':
            self.window.app.wiimote.led = 0
            GLib.source_remove(self.id)
            self.window.app.statusbar.set_text('Exame interrompido.')
            self.window.hide()

    def set_line_pos(self, diff):
        width, height = self.monitor.width, self.monitor.height
        radius = height//2
        catetus = radius//math.sqrt(2)
        self.diff2 = radius - catetus

        front_left  = Position(0 + diff + self.diff2, self.diff2)
        front       = Position(width//2, 0)
        front_right = Position(width - diff - self.diff2, self.diff2)
        right       = Position(width - diff, radius)
        rear_right  = Position(width - diff - self.diff2*2, height-self.diff2*2)
        rear        = Position(width//2, height-self.diff2*2)
        rear_left   = Position(0 + diff + self.diff2*2, height-self.diff2*2)
        left        = Position(0 + diff, radius)

        self.line_pos = list()
        for pos in [front_left,front,front_right,right,rear_right,rear,rear_left,left]:
            self.line_pos.append(pos)

    def init_los(self):
        self.target.set_position(self.monitor.center.x, self.monitor.center.y)
        self.yellow.set_position(self.monitor.center.x, self.monitor.center.y)
        self.id = GLib.timeout_add(DT, self.get_mean)
        self.window.app.wiimote.led = 1

    def get_mean(self):
        '''Calculates the mean of center of pressure (cop)
        '''
        if self.i < MEAN_SAMPLE:
            # Gets wbb readings
            readings = wbb.captura1(self.window.app.wiimote)
            # Gets CoP
            cop_x, cop_y = wbb.calCoP(readings, self.window.app.device.calibrations, wbb.escala_eu)

            self.x_mean += cop_x
            self.y_mean += cop_y
            self.i += 1
            return True
        else:
            self.mean = False
            self.x_mean /= MEAN_SAMPLE
            self.y_mean /= MEAN_SAMPLE

            self.i = 0
            self.k = 0
            self.id = GLib.timeout_add(DT, self.get_cop_pos)
            return False

    def get_cop_pos(self):
        self.k += 1
        if self.i < len(self.cur_pos):
            cur_pos = self.cur_pos[self.i]
            sample = RETURN_SAMPLE if cur_pos == 8 else LOS_SAMPLE

            if self.j < sample:
                # Gets wbb readings
                readings = wbb.captura1(self.window.app.wiimote)

                # Gets CoP
                cop_x, cop_y = wbb.calCoP(readings, self.window.app.device.calibrations, wbb.escala_eu)
                cop_x -= self.x_mean
                cop_y -= self.y_mean
                x_pos, y_pos = self.cop_to_pos(self.window.app.patient.height, cop_x, cop_y)
                self.green.set_position(x_pos, y_pos)
                self.window.drawing_area.queue_draw()

                if cur_pos != 8:
                    self.dynamic_cop_x[cur_pos][self.j], self.dynamic_cop_y[cur_pos][self.j] = cop_x, cop_y
                    self.target.set_position(self.line_pos[cur_pos].x, self.line_pos[cur_pos].y)
                    self.cur_line = self.line_pos[cur_pos]
                    # Progressbar fraction
                    self.window.app.main_window.progressbar.set_fraction(self.k / (sample * 8))
                    if calc_los.distance_points((x_pos, y_pos), self.cur_line.get_pos()) <= RADIUS:
                        print(cop_x, cop_y, math.sqrt(cop_x**2 + cop_y**2))
                        self.j = sample - 1
                else:
                    if calc_los.belongs_to_ellipsis(cop_x/10, cop_y/10, self.a, self.b, self.r):
                        self.center_counter += 1
                        if self.center_counter >= 20:
                            self.j = sample - 1
                    else:
                        self.center_counter = 0
                        self.j = 0
                    #print(self.center_counter, self.j, cop_x, cop_y)
                    self.target.set_position(self.monitor.center.x, self.monitor.center.y)
                    self.cur_line = Position(self.monitor.center.x, self.monitor.center.y)
                # Converts cop to screen pos
                # x_pos, y_pos = self.cop_to_pos(cop_x, cop_y, self.x_mean, self.y_mean)
                self.j += 1
            else:
                self.j = 0
                self.i += 1
                self.center_counter = 0
            return True
        else:
            self.window.app.dynamic_exam.cop_x = self.dynamic_cop_x
            self.window.app.dynamic_exam.cop_y = self.dynamic_cop_y
            self.window.app.main_window.handler.dynamic_metrics = calc_los.computes_metrics(
                self.window.app.dynamic_exam.cop_x,
                self.window.app.dynamic_exam.cop_y,
                self.window.app.patient.height, self.window.app.amplitude)
            self.window.app.main_window.handler.show_dynamic_exam()
            self.window.hide()
            self.window.app.main_window.save_dynamic_exam_button.set_sensitive(True)
            self.window.app.wiimote.led = 0
            return False

    def on_draw(self, widget, cr):
        # cr = widget.get_window().cairo_create()

        cr.set_source_rgb(.15, .15, .15)
        cr.paint()

        cr.set_source_rgb(.75, .75, .75)
        cr.rectangle(self.line_pos[7].x, 0, self.monitor.height, self.monitor.height)
        cr.fill()

        # cr.save()
        # cr.scale(1, .5)
        # cr.arc(self.monitor.center.x, self.monitor.center.y, self.monitor.center.y, 0, math.pi)
        # cr.set_source_rgb(.7,.7,.7)
        # cr.restore()
        # cr.scale(1, 2)

        cr.arc(self.monitor.center.x, self.monitor.center.y, self.monitor.center.y, 0, 2*math.pi)
        cr.set_source_rgb(.7,.7,.7)
        cr.fill()

        cr.set_line_width(25)
        cr.set_source_rgb(.5,.5,.5)
        for i, pos in enumerate(self.line_pos):
            if i == 4:
                cr.move_to(pos.x+self.diff2, pos.y+self.diff2)
            elif i == 5:
                cr.move_to(pos.x, self.monitor.height)
            elif i == 6:
                cr.move_to(pos.x-self.diff2, pos.y+self.diff2)
            else:
                cr.move_to(pos.x, pos.y)
            cr.line_to(self.monitor.center.x, self.monitor.center.y)
            cr.stroke()

        # cr.set_source_rgb(0,0,1)
        cr.set_source_rgb(.035, .129, .196)
        cr.move_to(self.cur_line.x, self.cur_line.y)
        cr.line_to(self.monitor.center.x, self.monitor.center.y)
        cr.stroke()

        cr.set_source_surface(self.target.img, self.target.pos.x, self.target.pos.y)
        cr.paint()

        if self.mean:
            cr.set_source_surface(self.yellow.img, self.yellow.pos.x, self.yellow.pos.y)
            cr.paint()
        else:
            cr.set_source_surface(self.green.img, self.green.pos.x, self.green.pos.y)
            cr.paint()

        cog = calc_los.center_of_gravity(self.window.app.patient.height)
        angle = np.radians(8.)
        R = cog*np.sin(angle)

        r = (self.r/R) * self.monitor.center.y
        a = (self.a/R) * self.monitor.center.y
        b = (self.b/R) * self.monitor.center.y

        cr.save()
        cr.translate(self.monitor.center.x, self.monitor.center.y)
        cr.scale(1, a/r)
        cr.arc(0., 0., r, math.pi, 2 * math.pi)
        cr.set_source_rgb(.25,.25,.25)
        cr.set_line_width(1)
        cr.stroke()
        #cr.fill()
        cr.restore()

        # cr.save()
        # cr.scale(1, a/r)
        # cr.arc(self.monitor.center.x, self.monitor.center.y, r, math.pi, 2*math.pi)
        # cr.set_source_rgb(.25,.25,.25)
        # cr.fill()
        # cr.restore()

        cr.save()
        cr.translate(self.monitor.center.x, self.monitor.center.y)
        cr.scale(1, b/r)
        cr.arc(0, 0, r, 0, math.pi)
        cr.set_source_rgb(.25,.25,.25)
        cr.set_line_width(1)
        cr.stroke()
        #cr.fill()
        cr.restore()

    def cop_to_pos(self, height, x, y, x_med = 0, y_med = 0):
        '''Converts center of pressure (cop) to screen position

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
        '''
        # X = 433 / 2 # mm
        # Y = -1 * 238 / 2 # mm

        cog = calc_los.center_of_gravity(height)
        angle = np.radians(8.)
        R = cog*np.sin(angle)*10
        #print("R = ", R)

        # xpos = (( x - x_med ) / X ) * self.monitor.center.x + self.monitor.center.x
        # ypos = (( y - y_med ) / Y ) * self.monitor.center.y + self.monitor.center.y

        #xpos = (( x - x_med ) / R ) * self.monitor.center.x + self.monitor.center.x
        #ypos = (( y - y_med ) / (-1*R) ) * self.monitor.center.y + self.monitor.center.y

        xpos = (x  / R ) * self.monitor.center.y + self.monitor.center.x
        ypos = (y  / (-1*R) ) * self.monitor.center.y + self.monitor.center.y

        diff = (self.monitor.width-self.monitor.height)//2
        if xpos > self.monitor.width - diff:
            xpos = self.monitor.width - diff
        if xpos < diff:
            xpos = diff
        if ypos > self.monitor.height:
            ypos = self.monitor.height
        if ypos < 0:
            ypos = 0

        return (xpos, ypos)

    def outersperse(self, lst, item):
        """
        Inserts a item at tail and between each list element

        Parameters
        ----------
        lst: list
            The list
        item: any
            The item to be outerspersed

        Returns
        -------
        list
            The list outerpersed with item
        """

        result = [item] * (len(lst) * 2 + 1)
        result[1::2] = lst
        result = result[1:-1]
        return result

    def on_delete_event(self, window, event):
        print('\n\n\n{}\n\n\n'.format(self.id))
        self.window.app.wiimote.led = 0
        GLib.source_remove(self.id)
        window.hide()
        return True
