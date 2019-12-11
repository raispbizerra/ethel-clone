# Third party imports
import os
from src.database.patient_dao import PatientDao
from src.database.device_dao import DeviceDao
from src.database.dynamic_exam_dao import DynamicExamDao
from src.models.dynamic_exam import DynamicExam
from src.database.static_exam_dao import StaticExamDao
from src.models.static_exam import StaticExam
import src.utilities.charts as charts
import src.utilities.calculos_los as calc_los
import src.utilities.calculos as calc
import src.utilities.wbb_calitera as wbb
import datetime as dt
import numpy as np
from cwiid import BATTERY_MAX
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

DT = 40
STATIC_SAMPLE = 10
LOS_SAMPLE = 200
MEAN_SAMPLE = LOS_SAMPLE // 2


class Handler:

    def __init__(self, window):
        self.window = window
        self.static_exam_dao = StaticExamDao()
        self.dynamic_exam_dao = DynamicExamDao()
        self.device_dao = DeviceDao()
        self.patient_dao = PatientDao()
        self.exam_counter = {'ON': 0, 'CN': 0, 'OF': 0, 'CF': 0}
        self.exams = {'ON': [None]*3, 'CN': [None]*3, 'OF': [None]*3, 'CF': [None]*3}
        self.dynamic_metrics = dict()
        self.static_metrics = dict()
        self.static_exam_cod = -1
        self.dynamic_exam_cod = -1
        self.axis_0, self.axis_1, self.axis_2 = None, None, None
        self.canvas_0, self.canvas_1, self.canvas_2 = None, None, None
        self.static_cop_x = np.zeros(0)
        self.static_cop_y = np.zeros(0)
        self.weight = 0.
        self.current_exam_labels = list()

    def on_show(self, window):
        """
        This method handles show event
        :param window:
        :return:
        """
        self.on_state_changed(self.window.app.exam_window.open_eyes)
        self.get_charts()
        self.clear_static_charts()
        self.clear_dynamic_chart()
        self.window.show_all()

    # def on_state_changed(self, button):
        

    def on_state_changed(self, button):
        for ctx in self.current_exam_labels:
            ctx.remove_class("yellow")

        if self.window.eyes_state.get_children()[0].get_active():
            ex_type = 'O'
        else:
            ex_type = 'C'

        if self.window.foam_state.get_children()[0].get_active():
            ex_type += 'N'
        else:
            ex_type += 'F'

        keys = ['ON', 'CN', 'OF', 'CF']
        i = keys.index(ex_type)
        j = self.exam_counter[ex_type]

        for k in range(1, 4):
            context = self.window.exam_grid.get_child_at(k, i + 2).get_child_at(j, 0).get_style_context()
            self.current_exam_labels.append(context)
            context.add_class("yellow")


    def on_row_selection_static_changed(self, selection):
        """
        This method handles selection change

        Parameters
        ----------
        selection : Gtk.TreeSelection
                The selection
        """
        # Get selection model (liststore)
        model, i = selection.get_selected()

        # Get exam_cod
        try:
            self.static_exam_cod = model[i][0]
        except TypeError:
            pass

        # Change button sensitivity
        self.window.load_static_exam_button.set_sensitive(True)

    def on_row_selection_dynamic_changed(self, selection):
        """
        This method handles selection change

        Parameters
        ----------
        selection : Gtk.TreeSelection
                The selection
        """
        # Get selection model (liststore)
        model, i = selection.get_selected()

        # Get exam_cod
        self.dynamic_exam_cod = model[i][0]

        # Change button sensitivity
        self.window.load_dynamic_exam_button.set_sensitive(True)

    def clear_exam_grid(self):
        # AP
        for i in range(2, 6):
            grid = self.window.app.main_window.exam_grid.get_child_at(1, i)
            for j in range(4):
                grid.get_child_at(j, 0).set_text('0.0')

        # ML
        for i in range(2, 6):
            grid = self.window.app.main_window.exam_grid.get_child_at(2, i)
            for j in range(4):
                grid.get_child_at(j, 0).set_text('0.0')

        # VM 
        for i in range(2, 6):
            grid = self.window.app.main_window.exam_grid.get_child_at(3, i)
            for j in range(4):
                grid.get_child_at(j, 0).set_text('0.0')

    def clear_static_metrics(self):
        for x in range(1, 16):
            self.window.metrics_grid.get_child_at(1, x).set_text('')

    def clear_dynamic_metrics(self):
        for i in range(1, 4):
            for j in range(1, 9):
                self.window.los_grid.get_child_at(i, j).set_text('')

    def clear_static_charts(self):
        """
        This method clears static exam charts
        """
        self.axis_0.clear()
        self.axis_0.set_title('Estatocinesiograma')
        self.axis_0.set_ylabel('Anteroposterior (cm)')
        self.axis_0.set_xlabel('Mediolateral (cm)')
        self.axis_0.set_xlim(-1, 1)
        self.axis_0.set_ylim(-1, 1)
        self.axis_0.axhline(0, color='grey')
        self.axis_0.axvline(0, color='grey')
        self.axis_0.set_autoscale_on(True)

        self.axis_1.clear()
        self.axis_1.set_title('Estabilograma')
        self.axis_1.set_xlim(0, 30)
        self.axis_1.set_ylabel('Amplitude (cm)')
        self.axis_1.set_xlabel('Tempo (s)')

    def clear_dynamic_chart(self):
        """
        This method clears dynamic exam chart
        """
        self.axis_2.clear()
        self.axis_2.set_title('Máxima Excursão')
        self.axis_2.set_ylim(0, 20)
        self.axis_2.set_aspect('equal', 'box')
        self.axis_2.set_theta_zero_location("N")  # theta=0 at the top
        self.axis_2.set_theta_direction(-1)  # theta increasing clockwise
        self.axis_2.set_rticks([0, 5, 10, 15, 20])

    def get_charts(self):
        """
        This method assigns and adds charts to main window
        """
        fig_0 = charts.fig()
        self.axis_0 = charts.axis(fig_0)
        self.axis_0.set_aspect('equal', 'box')
        self.canvas_0 = charts.canvas(fig_0)
        self.window.sw0.add(self.canvas_0)

        fig_1 = charts.fig()
        self.axis_1 = charts.axis(fig_1)
        self.canvas_1 = charts.canvas(fig_1)
        self.window.sw1.add(self.canvas_1)

        fig_2 = charts.fig()
        self.axis_2 = charts.axis(fig_2, 'polar')
        self.axis_2.set_aspect('equal', 'box')
        self.canvas_2 = charts.canvas(fig_2)
        self.window.sw2.add(self.canvas_2)

    def on_close_button_clicked(self, button: Gtk.Button):
        """
        This method handles click in quit button

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        self.window.app.on_quit(button)

    def on_new_device_activate(self, menu_item: Gtk.MenuItem):
        """
        This method handles activate menuitem event

        Parameters
        ----------
        menu_item : Gtk.MenuItem
                The menuitem
        """
        self.window.app.change_flags['device'] = False
        self.window.app.device_window.show()

    def on_load_device_activate(self, menu_item: Gtk.MenuItem):
        """
        This method handles activate menuitem event

        Parameters
        ----------
        menu_item : Gtk.MenuItem
                The menuitem
        """
        self.window.app.load_device_window.show()

    def on_edit_device_activate(self, menu_item: Gtk.MenuItem):
        """
        This method handles activate menuitem event

        Parameters
        ----------
        menu_item : Gtk.MenuItem
                The menuitem
        """
        self.window.app.change_flags['device'] = True
        self.window.app.device_window.show()

    def on_search_device_activate(self, menu_item: Gtk.MenuItem):
        """
        This method handles activate menuitem event

        Parameters
        ----------
        menu_item : Gtk.MenuItem
                The menuitem
        """
        self.window.app.search_device_window.show()

    def nullify_device(self):
        """
        This method nullify the device
        """
        self.window.app.connection_flags['device'] = False
        self.window.app.wiimote = None
        self.window.app.device.cod = None
        self.window.app.device.name = None
        self.window.app.device.mac = None
        self.window.app.device.calibrations = None
        self.window.app.device.is_default = None
        self.window.app.main_window.edit_device.set_sensitive(False)
        self.window.app.main_window.calibrate_device.set_sensitive(False)
        self.window.app.main_window.disconnect_device.set_sensitive(False)
        self.window.battery_label.set_text("Bateria:")
        self.window.connection_image.set_from_file(
            "media/bluetooth_disconnect.png")
        self.window.connection_label.set_text("Não conectado")

    def on_disconnect_device_activate(self, menu_item: Gtk.MenuItem):
        """
        This method handles activate menuitem event

        Parameters
        ----------
        menu_item : Gtk.MenuItem
                The menuitem
        """
        self.nullify_device()
        self.window.statusbar.set_text('Desconectado')

    def on_new_patient_activate(self, menu_item: Gtk.MenuItem):
        """
        This method handles activate menuitem event

        Parameters
        ----------
        menu_item : Gtk.MenuItem
                The menuitem
        """
        self.window.app.change_flags['patient'] = False
        self.window.app.patient_window.show()

    def on_load_patient_activate(self, menu_item: Gtk.MenuItem):
        """
        This method handles activate menuitem event

        Parameters
        ----------
        menu_item : Gtk.MenuItem
                The menuitem
        """
        self.window.app.load_patient_window.show()

    def on_edit_patient_activate(self, menu_item: Gtk.MenuItem):
        """
        This method handles activate menuitem event

        Parameters
        ----------
        menu_item : Gtk.MenuItem
                The menuitem
        """
        self.window.app.change_flags['patient'] = True
        self.window.app.patient_window.show()

    def on_calibrate_device_activate(self, menu_item: Gtk.MenuItem):
        """
        This method handles activate menuitem event

        Parameters
        ----------
        menu_item : Gtk.MenuItem
                The menuitem
        """
        self.window.app.calibration_window.show()

    def on_see_grid_button_clicked(self, button: Gtk.Button):
        """
        This method handles click on see_grid_button

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        visibility = not self.window.los_grid.get_visible()
        self.window.los_grid.set_visible(visibility)

    def show_static_exam(self):
        """
        This method shows static exam
        """

        try:
            # Estado dos olhos e espuma
            eyes = 0 if self.window.app.static_exam.state[0] != 'C' else 1
            self.window.eyes_state.get_children()[eyes].set_active(True)

            foam = 0 if self.window.app.static_exam.state[1] != 'F' else 1
            self.window.foam_state.get_children()[foam].set_active(True)

            # Preenchimento da janela principal com as métricas
            metrics = [
                self.static_metrics['AP_'], self.static_metrics['ML_'],
                self.static_metrics['dis_mediaAP'], self.static_metrics['dis_mediaML'], self.static_metrics['dis_media'],
                self.static_metrics['dis_rms_AP'], self.static_metrics['dis_rms_ML'], self.static_metrics['dis_rms_total'],
                self.static_metrics['mvelo_AP'], self.static_metrics['mvelo_ML'], self.static_metrics['mvelo_total'],
                self.static_metrics['amplitude_AP'], self.static_metrics['amplitude_ML'],
                self.static_metrics['amplitude_total'], 768
            ]

            ln = len(metrics) + 1
            for x in range(1, ln):
                self.window.metrics_grid.get_child_at(1, x).set_text(f"{round(metrics[x - 1], 2)}")

            self.axis_0.set_xlim(-self.static_metrics['max_absoluto'], self.static_metrics['max_absoluto'])
            self.axis_0.set_ylim(-self.static_metrics['max_absoluto'], self.static_metrics['max_absoluto'])
            self.axis_0.plot(self.static_metrics['MLs_Processado'], self.static_metrics['APs_Processado'], '.-',
                             label='CoP')
            self.axis_0.legend()
            self.canvas_0.draw()

            self.axis_1.set_ylim(-self.static_metrics['maximo'], self.static_metrics['maximo'])
            self.axis_1.set_xlim(self.static_metrics['tempo'][0], self.static_metrics['tempo'][-1])
            self.axis_1.plot(self.static_metrics['tempo'], self.static_metrics['APs_Processado'], '-', label='APs')
            self.axis_1.plot(self.static_metrics['tempo'], self.static_metrics['MLs_Processado'], '--', label='MLs')
            self.axis_1.plot(self.static_metrics['tempo'], self.static_metrics['dis_resultante_total'], ':', label='DRT')
            self.axis_1.legend()
            self.canvas_1.draw()
        except ValueError as e:
            self.window.app.statusbar.set_text("Erro na aquisição, tente novamente.")
            raise(e)

    def on_load_static_exam_button_clicked(self, button):
        """
        This method handles load_exam_button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        # for col in self.window.static_exams_tree.get_columns():
        #     context = col.get_cell_renderers()[0].get_style_context()
        #     context.remove_class('blue')

        self.window.app.static_exam = self.static_exam_dao.read_exam(self.static_exam_cod)
        self.clear_static_charts()
        self.static_metrics = calc.computes_metrics(self.window.app.static_exam.aps, self.window.app.static_exam.mls)
        self.show_static_exam()
        self.window.static_notebook.set_current_page(1)
        self.window.app.statusbar.set_text('Exame carregado')

    def show_dynamic_exam(self):
        """
        This method shows static exam
        """
        for i in range(8):
            self.window.los_grid.get_child_at(1, i + 1).set_text(
                f"{round(self.dynamic_metrics['reaction_time'][i], 2)}")
            self.window.los_grid.get_child_at(2, i + 1).set_text(
                f"{round(self.dynamic_metrics['maximum_excursion'][i], 2)}")
            self.window.los_grid.get_child_at(3, i + 1).set_text(
                f"{round(self.dynamic_metrics['directional_control'][i], 2)}")

        angles = np.radians(np.arange(0., 405., 45.))
        # angles = np.radians(np.array([315., 0., 45., 90., 135., 180., 225., 270., 315.]))

        maximum_excursion = np.append(
            self.dynamic_metrics['maximum_excursion'], self.dynamic_metrics['maximum_excursion'][0])
        self.axis_2.plot(angles, maximum_excursion, '*-')
        self.canvas_2.draw()

    def get_amplitude(self):
        exams = self.static_exam_dao.read_last_exams_from_patient(self.window.app.patient.cod)
        if len(exams) < 3:
            self.window.app.statusbar.set_text('Realize mais exames estáticos!')
            self.window.notebook.set_current_page(0)
            self.window.app.amplitude = (self.static_metrics['amplitude_AP'] * 2 / 3,
                                         self.static_metrics['amplitude_AP'] / 3,
                                         self.static_metrics['amplitude_ML'] / 2)
            return

        amplitude_ap = np.zeros(3)
        amplitude_ml = np.zeros(3)
        for i, exam in enumerate(exams):
            amplitude_ap[i], amplitude_ml[i] = calc.get_amplitude(exam.aps, exam.mls)

        self.window.app.amplitude = (amplitude_ap.mean() * 2 / 3,
                                     amplitude_ap.mean() / 3,
                                     amplitude_ml.mean() / 2)

    def on_load_dynamic_exam_button_clicked(self, button):
        """
        This method handles load_exam_button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        """

        self.window.app.dynamic_exam = self.dynamic_exam_dao.read_exam(
            self.dynamic_exam_cod)
        self.clear_dynamic_chart()
        self.get_amplitude()
        self.dynamic_metrics = calc_los.computes_metrics(self.window.app.dynamic_exam.cop_x,
                                                         self.window.app.dynamic_exam.cop_y,
                                                         self.window.app.patient.height, self.window.app.amplitude)
        self.show_dynamic_exam()
        self.window.app.statusbar.set_text('Exame carregado')

    def static_posturography(self):
        """
        This method performs static posturography
        """
        i = len(self.static_cop_x)
        if i <= STATIC_SAMPLE:
            # Capture
            readings = wbb.captura1(self.window.app.wiimote)
            # Weight computation
            self.weight += wbb.calcWeight(
                readings, self.window.app.device.calibrations, wbb.escala_eu)
            # Cop computation
            cop_x, cop_y = wbb.calCoP_(
                readings, self.window.app.device.calibrations, wbb.escala_eu)
            self.static_cop_x = np.append(self.static_cop_x, cop_x)
            self.static_cop_y = np.append(self.static_cop_y, cop_y)
            print(self.static_cop_x, self.static_cop_y)
            # Progressbar fraction
            self.window.progressbar.set_fraction(i / STATIC_SAMPLE)
            self.window.app.exam_window.drawing_area.queue_draw()

            return True
        else:
            duration = .08  # second
            freq = 440  # Hz
            for _ in range(3):
                os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
            self.window.app.wiimote.led = 0
            self.weight /= STATIC_SAMPLE
            self.weight = round(self.weight, 2)
            height = self.window.app.patient.height / 100
            self.imc = self.weight / height ** 2
            date = dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S.%f')
            self.window.points_entry.set_text(str(STATIC_SAMPLE))

            if self.window.app.exam_window.open_eyes:
                ex_type = 'O'
            else:
                ex_type = 'C'

            if self.window.foam_state.get_children()[0].get_active():
                ex_type += 'N'
            else:
                ex_type += 'F'

            self.window.app.static_exam = StaticExam(aps=self.static_cop_y,
                                                     mls=self.static_cop_x,
                                                     date=date, pat_cod=self.window.app.patient.cod,
                                                     state=ex_type)
            self.static_metrics = calc.computes_metrics(self.static_cop_y, self.static_cop_x)
            self.window.app.exam_window.hide()
            self.show_static_exam()
            self.fill_grid()
            self.window.save_static_exam_button.set_sensitive(True)
            self.window.save_static_exam_button.grab_focus()

            return False

    def on_start_static_exam_button_clicked(self, button):
        """
        This method handles start_static_exam_button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        self.window.static_notebook.set_current_page(0)
        self.window.statusbar.set_text('Começando exame...')
        # Mudança na visibilidade da janela
        self.window.app.exam_window.open_eyes = self.window.eyes_state.get_children()[
            0].get_active()
        self.window.app.exam_window.show()

        # Limpeza dos gráficos
        self.clear_static_charts()

        # Cop arrays
        self.static_cop_x = np.zeros(0)
        self.static_cop_y = np.zeros(0)
        self.weight = 0.

        self.window.app.wiimote.led = 1
        self.window.method_id = GLib.timeout_add(1000, self.counter)

    def counter(self):
        if self.window.app.exam_window.time > 0:
            # print(f"{self.window.app.exam_window.time}", self.window.app.exam_window.counting)
            self.window.app.exam_window.drawing_area.queue_draw()
            self.window.app.exam_window.time -= 1
            duration = .1  # second
            freq = 440  # Hz
            os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
            return True
        else:
            duration = .5  # second
            freq = 440  # Hz
            os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
            self.window.app.exam_window.counting = False
            self.window.app.exam_window.r, self.window.app.exam_window.g, self.window.app.exam_window.b = .3, .73, .09
            GLib.source_remove(self.window.method_id)
            self.window.method_id = GLib.timeout_add(DT, self.static_posturography)
        return False

    def fill_grid(self):
        keys = ['ON', 'CN', 'OF', 'CF']
        i = keys.index(self.window.app.static_exam.state)
        j = self.exam_counter[self.window.app.static_exam.state]

        # metrics = (self.static_metrics['amplitude_AP'], self.static_metrics['amplitude_ML'], self.static_metrics['mvelo_total'])
        # metrics = (self.static_metrics['dis_mediaAP'], self.static_metrics['dis_mediaML'], self.static_metrics['mvelo_total'])
        
        # self.current_exam_labels = list()
        # for k in range(1, 4):
        #     self.current_exam_labels.append(self.window.exam_grid.get_child_at(k, i + 2).get_child_at(j, 0))
        #     context = self.window.exam_grid.get_child_at(k, i + 2).get_child_at(j, 0).get_style_context()
        #     context.add_class("orange")
        #     self.window.exam_grid.get_child_at(k, i + 2).get_child_at(j, 0).set_text(f"{round(metrics[k-1], 2)}")
        #     m = 0.
        #     for l in range(j + 1):
        #         m += float(self.window.exam_grid.get_child_at(1, i + 2).get_child_at(l, 0).get_text())
        #     m /= j + 1
        #     self.window.exam_grid.get_child_at(k, i + 2).get_child_at(3, 0).set_text(f"{round(m, 2)}")

        # self.current_exam_labels.append(self.window.exam_grid.get_child_at(1, i + 2).get_child_at(j, 0))
        # self.current_exam_labels.append(self.window.exam_grid.get_child_at(2, i + 2).get_child_at(j, 0))
        # self.current_exam_labels.append(self.window.exam_grid.get_child_at(3, i + 2).get_child_at(j, 0))

        context = self.window.exam_grid.get_child_at(1, i + 2).get_child_at(j, 0).get_style_context()
        self.current_exam_labels.append(context)
        context.add_class("orange")

        self.window.exam_grid.get_child_at(1, i + 2).get_child_at(j, 0).set_text(
            f"{round(self.static_metrics['dis_mediaAP'], 2)}")
        m = 0.
        for l in range(j + 1):
            m += float(self.window.exam_grid.get_child_at(1, i + 2).get_child_at(l, 0).get_text())
        m /= j + 1
        self.window.exam_grid.get_child_at(1, i + 2).get_child_at(3, 0).set_text(f"{round(m, 2)}")

        context = self.window.exam_grid.get_child_at(2, i + 2).get_child_at(j, 0).get_style_context()
        self.current_exam_labels.append(context)
        context.add_class("orange")
        self.window.exam_grid.get_child_at(2, i + 2).get_child_at(j, 0).set_text(
            f"{round(self.static_metrics['dis_mediaML'], 2)}")
        m = 0.
        for l in range(j + 1):
            m += float(self.window.exam_grid.get_child_at(2, i + 2).get_child_at(l, 0).get_text())
        m /= j + 1
        self.window.exam_grid.get_child_at(2, i + 2).get_child_at(3, 0).set_text(f"{round(m, 2)}")

        context = self.window.exam_grid.get_child_at(3, i + 2).get_child_at(j, 0).get_style_context()
        self.current_exam_labels.append(context)
        context.add_class("orange")
        self.window.exam_grid.get_child_at(3, i + 2).get_child_at(j, 0).set_text(
            f"{round(self.static_metrics['mvelo_total'], 2)}")
        m = 0.
        for l in range(j + 1):
            m += float(self.window.exam_grid.get_child_at(3, i + 2).get_child_at(l, 0).get_text())
        m /= j + 1
        self.window.exam_grid.get_child_at(3, i + 2).get_child_at(3, 0).set_text(f"{round(m, 2)}")

    def on_save_static_exam_button_clicked(self, button):
        """
        This method handles save_static_exam_button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        print(self.exam_counter[self.window.app.static_exam.state])
        exam = self.exams[self.window.app.static_exam.state][self.exam_counter[self.window.app.static_exam.state]]
        last_exam = self.exams[self.window.app.static_exam.state][self.exam_counter[self.window.app.static_exam.state]-1]
        if exam:
            print(exam.date)
            if last_exam != self.window.app.static_exam:
                self.window.app.static_exam.cod = exam.cod
                self.static_exam_dao.update_exam(self.window.app.static_exam)
                print('\n\nupdate\n')
        else:
            if self.window.app.static_exam.state == 'ON':
                self.window.app.patient.weight = round(self.weight, 2)
                self.window.app.patient.imc = round(self.imc, 2)
                self.patient_dao.update_patient(self.window.app.patient)
            self.static_exam_dao.create_exam(self.window.app.static_exam)
            print('\n\nsave\n')
        self.exams[self.window.app.static_exam.state][self.exam_counter[self.window.app.static_exam.state]] = self.window.app.static_exam
        self.window.statusbar.set_text('Exame salvo!')
        # self.window.save_static_exam_button.set_sensitive(False)
        self.window.app.load_patient_window.handler.load_static_exams()
        for context in self.current_exam_labels:
            # context = label.get_style_context()
            context.remove_class("orange")
        self.exam_counter[self.window.app.static_exam.state] = (self.exam_counter[
                                                                    self.window.app.static_exam.state] + 1) % 3
        self.on_state_changed(self.window.app.exam_window.open_eyes)

    def on_start_dynamic_exam_button_clicked(self, button):
        """
        This method handles start_dynamic_exam_button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        self.get_amplitude()
        date = datetime.now()
        self.window.app.dynamic_exam = DynamicExam(
            date=date, pat_cod=self.window.app.patient.cod)
        self.clear_dynamic_chart()
        self.window.app.los_window.show()

    def on_save_dynamic_exam_button_clicked(self, button):
        """
        This method handles save_dynamic_exam_button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        self.dynamic_exam_dao.create_exam(self.window.app.dynamic_exam)
        self.window.statusbar.set_text('Exame salvo!')
        self.window.save_dynamic_exam_button.set_sensitive(False)
        self.window.app.load_patient_window.handler.load_dynamic_exams()

    def on_exam_tab_toggled(self, button):
        """
        This method handles save_dynamic_exam_button click

        Parameters
        ----------
        button : Gtk.Button
                The button
        """
        self.window.metrics_grid.set_visible(not self.window.metrics_grid.get_visible())
        self.window.exams_list.set_visible(not self.window.exams_list.get_visible())

    def on_report_select(self, item):
        self.window.app.report_window.show_all()

    def verify_connection(self):
        """
        This method verifies device's connection
        """
        if self.window.app.wiimote:
            try:
                self.window.app.wiimote.request_status()
                battery = (self.window.app.wiimote.state['battery'] * 100) // BATTERY_MAX
                self.window.battery_label.set_text("Bateria: " + str(battery) + "%")
                self.window.connection_label.set_text("Conectado")
                self.window.connection_image.set_from_file("media/bluetooth_connect.png")
            except RuntimeError:
                self.nullify_device()
                self.window.statusbar.set_text('Perda de conexão, tente novamente.')
                return False
        else:
            return False
        return True

    def on_static_exams_tree_row_activated(self, tree, path, column):
        if tree.get_columns().index(column) == 3:
            self.static_exam = self.static_exam_dao.read_exam(tree.get_model()[path][0])
            self.window.dialog.format_secondary_text(f'{self.static_exam.cod} do paciente {self.window.app.patient.name}')
            self.window.dialog.show()

    def on_static_exams_tree_button_press_event(self, treeview, event):
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            selection = treeview.get_selection()
            model, i = selection.get_selected()
            if i == None: #note 3
                return True
            model = treeview.get_model()
            self.static_exam_cod = model[i][0]
            self.on_load_static_exam_button_clicked(self.window.load_static_exam_button)

    def on_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.YES:
            self.static_exam.pat_cod = -1
            self.static_exam_dao.update_exam(self.static_exam)
            self.window.app.load_patient_window.handler.load_static_exams()
        dialog.hide()