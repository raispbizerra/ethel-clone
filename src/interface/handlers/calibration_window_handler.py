# Default library imports
import src.utilities.utils as utils
from src.database.device_dao import DeviceDao
import src.utilities.wbb_calitera as wbb
import numpy as np
from gi.repository import Gtk, GLib, Gdk
from datetime import datetime

# Third party imports
import gi
gi.require_version('Gtk', '3.0')

# Local imports

DT = 50
MIN_REP = 1000
MED_REP = 100
MAX_REP = 10
TESTING = False
PAD = False


class Handler():
    """This class implements Los Window Handler
    """

    def __init__(self, window):
        self.window = window
        self.device_dao = DeviceDao()
        self.current_calibration = 0
        self.clicked_signal = None
        self.gauge_id = None

    def redefine(self):
        if TESTING:
            if PAD:
                cal = self.window.app.wiimote.get_balance_cal()
                self.window.app.calibration = dict()
                for i, sensor in enumerate(('right_top', 'right_bottom', 'left_top', 'left_bottom')):
                    self.window.app.calibration[sensor] = cal[i]
            else:
                self.window.app.calibration = self.window.app.device.calibrations

        else:
            self.window.test_button.hide()
            self.window.app.calibration = {'right_top': np.zeros(3), 'right_bottom': np.zeros(
                3), 'left_top': np.zeros(3), 'left_bottom': np.zeros(3)}

        # Images
        self.images = ('test_pontos_rt.png', 'test_pontos_rb.png',
                       'test_pontos_lt.png', 'test_pontos_lb.png')
        # Sensors
        self.sensors = ('RT', 'RB', 'LT', 'LB')
        self.current_weight = 0
        self.current_sensor = 0
        # Initial image
        self.window.calibration_image.set_from_file('media/test_pontos.png')
        # Set label text
        self.window.calibration_label.set_text('Nova calibração')
        # Set button label
        self.window.calibration_button.set_label('Iniciar')
        # Set saved and new calibration labels
        self.window.new_calibration_label.set_text('')
        self.window.saved_calibration_label.set_text(
            str(self.window.app.device.calibrations))
        self.window.saved_calibration_date_label.set_text('CALIBRAÇÃO SALVA ({}):'.format(
            utils.datetime_to_str(self.window.app.device.calibration_date)))
        # Get and connect signal
        if self.clicked_signal:
            self.window.calibration_button.disconnect(self.clicked_signal)
        self.clicked_signal = self.window.calibration_button.connect(
            'clicked', self.on_start_calibration)
        self.window.calibration_button.set_sensitive(True)
        # Set progressbar fraction
        self.window.progress_bar.set_fraction(0)
        # Set spins sensitivity
        self.window.med_weight_spin.set_sensitive(True)
        self.window.max_weight_spin.set_sensitive(True)
        # Verify connection
        self.verify_id = GLib.timeout_add(DT, self.verify_connection)

    def on_show(self, window):
        '''
        This method handles show event
        '''
        self.redefine()

    def on_start_calibration(self, button):
        '''
        This method handles start calibration button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        '''
        # Set spins sensitivity
        self.window.med_weight_spin.set_sensitive(False)
        self.window.max_weight_spin.set_sensitive(False)
        # Weights
        med_weight = float(
            self.window.med_weight_spin.get_text().replace(',', '.', 1))
        max_weight = float(
            self.window.max_weight_spin.get_text().replace(',', '.', 1))
        self.weights = (med_weight, max_weight)
        # Set label text
        self.window.calibration_label.set_text(
            'Posicione o dispositivo sem nenhum peso')
        # Set button label
        self.window.calibration_button.set_label('Medir')
        # Disconnect, get and connect signal
        self.window.calibration_button.disconnect(self.clicked_signal)
        self.clicked_signal = self.window.calibration_button.connect(
            'clicked', self.on_gauge_min)

    def capture(self, i, calibre):
        # Read signal
        readings = wbb.captura1(self.window.app.wiimote)
        # Assign signal by sensor
        for j, sensor in enumerate(self.window.app.calibration.keys()):
            calibre[i, j] = readings[sensor]

    def gauge_minimum(self):
        if self.i < MIN_REP:
            self.capture(self.i, self.calibre)
            # Increments counter
            self.i += 1
            # Set progressbar fraction
            self.window.progress_bar.set_fraction(self.i/MIN_REP)
            return True
        else:
            self.repeat = {'sensor': self.current_sensor,
                           'weight': self.current_weight}
            # print(self.calibre)
            # Set counter to 0
            self.i = 0
            # Computes calibration
            saida = wbb.saida_(self.calibre, min=True)
            medium = saida + wbb.escala_eu
            maximum = medium + wbb.escala_eu

            # Assign calibration to dict
            for j, sensor in enumerate(self.window.app.calibration.keys()):
                self.window.app.calibration[sensor] = np.array(
                    [saida[j], medium[j], maximum[j]])

            # Reset calibre
            self.calibre = np.zeros((4, MED_REP, 4))
            self.signal = np.zeros(4)
            self.readings = [{'right_top': 0, 'right_bottom': 0, 'left_top': 0, 'left_bottom': 0}, {'right_top': 0, 'right_bottom': 0, 'left_top': 0, 'left_bottom': 0}, {
                'right_top': 0, 'right_bottom': 0, 'left_top': 0, 'left_bottom': 0}, {'right_top': 0, 'right_bottom': 0, 'left_top': 0, 'left_bottom': 0}]

            # Show partial calibration
            self.window.new_calibration_date_label.set_text(
                'CALIBRAÇÃO PARCIAL - MÍNIMOS')
            self.window.new_calibration_label.set_text(
                str(self.window.app.calibration))

            # Disconnect, get and connect signal
            self.window.calibration_button.disconnect(self.clicked_signal)
            self.clicked_signal = self.window.calibration_button.connect(
                'clicked', self.on_gauge_med)

            # Change label and image
            self.window.calibration_label.set_text('Posicione o peso de {}kg no sensor {}'.format(
                self.weights[self.current_weight], self.sensors[self.current_sensor]))
            self.window.calibration_image.set_from_file(
                'media/{}'.format(self.images[self.current_sensor]))
            self.window.calibration_button.set_sensitive(True)
            return False

    def on_gauge_min(self, button):
        '''
        This method handles start calibration button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        '''
        print("Calibrando o sinal mínimo")
        self.window.calibration_button.set_sensitive(False)
        self.i = 0
        self.calibre = np.zeros((MIN_REP, 4))
        self.gauge_id = GLib.timeout_add(DT, self.gauge_minimum)

    def gauge_medium(self):
        if self.i < MED_REP:
            # Capture
            self.capture(self.i, self.calibre[self.current_sensor])
            # Increments counter
            self.i += 1
            # Set progressbar fraction
            self.window.progress_bar.set_fraction(self.i/MED_REP)
            return True
        else:
            self.repeat = {'sensor': self.current_sensor,
                           'weight': self.current_weight}
            # Set counter to 0
            self.i = 0
            # Computes calibration
            saida = wbb.saida_(self.calibre[self.current_sensor])
            for j, sensor in enumerate(self.window.app.calibration.keys()):
                self.readings[self.current_sensor][sensor] = saida[j]
            # print(self.calibre[self.current_sensor], saida, self.readings)
            # Compute sensor
            self.current_sensor = (self.current_sensor + 1) % 4
            if not self.current_sensor:
                nome = f"iteracoes {self.window.app.device.mac}.txt"
                f = open(nome, 'w')
                cal = self.window.app.calibration
                erro = 100.
                for i in range(100):
                    for j, sensor in enumerate(self.window.app.calibration.keys()):
                        wbb.p_res(self.readings[j], sensor, self.window.app.calibration, wbb.escala_eu, int(
                            self.weights[self.current_weight] * 100), 1)
                    f.write(f"Calibração {i}: {self.window.app.calibration}")
                    for sensor in self.window.app.calibration.keys():
                        f.write(
                            f"Erro relativo {sensor}: {abs((self.window.app.calibration[sensor][1] - cal[sensor][1])/cal[sensor][1]) * 100.}")
                    cal = self.window.app.calibration

                calibration = self.window.app.wiimote.get_balance_cal()
                cal = dict()
                for i, sensor in enumerate(('right_top', 'right_bottom', 'left_top', 'left_bottom')):
                    cal[sensor] = calibration[i]
                    f.write(
                        f"Erro relativo {sensor}: {abs((self.window.app.calibration[sensor][1] - cal[sensor][1])/cal[sensor][1]) * 100.}")
                f.close()

                self.current_weight = 1
                # Disconnect, get and connect signal
                self.window.calibration_button.disconnect(self.clicked_signal)
                self.clicked_signal = self.window.calibration_button.connect(
                    'clicked', self.on_gauge_max)
                # Reset calibre
                self.calibre = np.zeros((4, MAX_REP, 4))
                self.window.new_calibration_label.set_text(
                    str(self.window.app.calibration))
                self.window.new_calibration_date_label.set_text(
                    'CALIBRAÇÃO PARCIAL - MÍNIMOS E MÉDIOS')
            # Change label and image
            self.window.calibration_label.set_text('Posicione o peso de {}kg no sensor {}'.format(
                self.weights[self.current_weight], self.sensors[self.current_sensor]))
            self.window.calibration_image.set_from_file(
                'media/{}'.format(self.images[self.current_sensor]))
            self.window.calibration_button.set_sensitive(True)
            return False

    def on_gauge_med(self, button):
        '''
        This method handles start calibration button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        '''
        print("Calibrando o sinal médio")
        self.window.calibration_button.set_sensitive(False)
        self.gauge_id = GLib.timeout_add(DT, self.gauge_medium)

    def gauge_maximum(self):
        if self.i < MAX_REP:
            # Capture
            self.capture(self.i, self.calibre[self.current_sensor])
            # Increments counter
            self.i += 1
            # Set progressbar fraction
            self.window.progress_bar.set_fraction(self.i/MAX_REP)
            return True
        else:
            self.repeat = {'sensor': self.current_sensor,
                           'weight': self.current_weight}
            # Set counter to 0
            self.i = 0
            # Computes calibration
            saida = wbb.saida_(self.calibre[self.current_sensor])
            for j, sensor in enumerate(self.window.app.calibration.keys()):
                self.readings[self.current_sensor][sensor] = saida[j]
            # Change label and image
            self.current_sensor = (self.current_sensor + 1) % 4
            if not self.current_sensor:
                for j, sensor in enumerate(self.window.app.calibration.keys()):
                    wbb.p_res(self.readings[j], sensor, self.window.app.calibration, wbb.escala_eu, int(
                        self.weights[self.current_weight] * 100), 2, max=True)
                self.window.test_button.show()
                self.window.calibration_label.set_text(
                    'Calibração finalizada!')
                self.window.calibration_image.set_from_file(
                    'media/test_pontos.png')
                # Disconnect, get and connect signal
                self.window.calibration_button.set_label('Salvar')
                self.window.calibration_button.disconnect(self.clicked_signal)
                self.clicked_signal = self.window.calibration_button.connect(
                    'clicked', self.on_save)
                self.window.new_calibration_label.set_text(
                    str(self.window.app.calibration))
                self.window.new_calibration_date_label.set_text(
                    'CALIBRAÇÃO FINAL')
            else:
                self.window.calibration_label.set_text('Posicione o peso de {}kg no sensor {}'.format(
                    self.weights[self.current_weight], self.sensors[self.current_sensor]))
                self.window.calibration_image.set_from_file(
                    'media/{}'.format(self.images[self.current_sensor]))
            self.window.calibration_button.set_sensitive(True)
            return False

    def on_gauge_max(self, button):
        '''
        This method handles start calibration button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        '''
        print("Calibrando o sinal máximo")
        self.window.calibration_button.set_sensitive(False)
        self.gauge_id = GLib.timeout_add(DT, self.gauge_maximum)

    def on_save(self, button):
        '''
        This method handles save button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        '''
        # Update calibrations
        # self.device_dao.update_device_calibrations(self.window.app.device.cod, self.window.app.calibration, datetime.now())
        self.device_dao.create_device_calibrations(
            self.window.app.device.cod, self.window.app.calibration, datetime.now())
        # Show status
        self.window.app.statusbar.set_text('Dispositivo calibrado!')
        # Disconnect signal
        self.window.calibration_button.disconnect(self.clicked_signal)
        GLib.source_remove(self.verify_id)
        # Hide window
        self.window.hide()

    def on_connect_device(self, button):
        '''
        This method handles connect button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        '''
        self.window.app.load_device_window.show()

    def verify_connection(self):
        if self.window.app.connection_flags['device']:
            return True
        else:
            # Show status
            self.window.calibration_label.set_text(
                'Perda de conexão com o dispositivo, tente novamente')
            # Set button label
            self.window.calibration_button.set_label('Conectar')
            # Disconnect, get and connect signal
            self.window.calibration_button.disconnect(self.clicked_signal)
            self.clicked_signal = self.window.calibration_button.connect(
                'clicked', self.on_connect_device)
            self.window.calibration_button.set_sensitive(True)
            return False

    def cancel(self):
        print('Cancelado')
        if self.gauge_id:
            GLib.source_remove(self.gauge_id)
        self.window.calibration_button.disconnect(self.clicked_signal)
        self.redefine()

    def on_cancel_button_clicked(self, button):
        '''
        This method handles cancel button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        '''
        self.cancel()
        GLib.source_remove(self.verify_id)
        self.window.hide()

    def on_test_button_clicked(self, button):
        '''
        This method handles test button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        '''
        self.window.app.calibration_test_window.show_all()

    def on_repeat_button_clicked(self, button):
        '''
        This method handles repeat button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        '''

        self.current_weight = self.repeat['weight']
        self.current_sensor = self.repeat['sensor']

    def on_key_press_event(self, widget, event):
        key = Gdk.keyval_name(event.keyval).upper()
        if key == 'ESCAPE':
            self.cancel()
