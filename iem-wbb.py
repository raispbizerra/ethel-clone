#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Importação dos módulos
import sys

sys.path.append('src')
sys.path.append('media')

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

import calculos as calc
import conexao as connect
import ManipularArquivo as manArq
import bancoDeDados as bd

from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

from bluetooth.btcommon import is_valid_address as iva
from validate_email import validate_email

import wbb_calitera as wbb
import numpy as np
import time as ptime

BATTERY_MAX = 208
TESTING = False

class iemWbb:
    """
        registro de novos pacientes
        captura dos sinais
        calculo das metricas
        representação grafica do resultados
        armazenamento dos resultados no banco de dados
    """

    # REGISTRO DE PACIENTES #

    # Evento de clique do botão 'SALVAR PACIENTE'
    def on_savepacient_button_clicked(self, widget):

        # Define pai transitório para diálogo
        self.message_dialog_window.set_transient_for(self.main_window)

        # Definição a flag de paciente carregado como falsa
        self.flags['is_pacient'] = False

        # Recuperação os dados de entrada
        pacient = {'Nome': self.name_entry.get_text(),
                   'Sexo': self.sex_combobox.get_active_text(),
                   'Idade': self.age_entry.get_text(),
                   'Altura': self.height_entry.get_text().replace(',', '.', 1)}

        # Recuperação das 'entrys'
        childList = self.name_entry.get_parent().get_children()

        # Teste de dados inválidos
        for i, data in enumerate(pacient.items()):
            if data[1] == '' or data[1] is None:
                self.message_dialog_window.format_secondary_text("Dados inválidos, tente novamente.")
                self.message_dialog_window.show()
                childList[i].grab_focus()

                return

        pacient['Peso'] = self.weight.get_text()
        pacient['IMC'] = self.imc.get_text()

        # Redefinição da entrada de altura para facilitar os cálculos
        self.height_entry.set_text(pacient['Altura'])

        # Teste se o paciente está sendo modificado
        if not self.flags['modifying']:
            # Inserção do paciente no banco de dados
            self.cur.execute("INSERT INTO pacients (name, sex, age, height) VALUES (%s, %s, %s, %s);",
                             (pacient['Nome'].upper(), pacient['Sexo'].upper(), pacient['Idade'], pacient['Altura']))
            self.conn.commit()

            # Recuperação do ID do paciente no BD
            self.cur.execute("SELECT last_value FROM pacients_id_seq;")
            row = self.cur.fetchall()
            pacient['ID'] = row[0][0]
        else:
            # Atualização dos dados do paciente
            self.cur.execute("UPDATE pacients SET name = (%s), sex = (%s), age = (%s), height = (%s) WHERE id = (%s);",
                             (pacient['Nome'].upper(), pacient['Sexo'].upper(), pacient['Idade'], pacient['Altura'],
                              self.pacient['ID']))
            self.conn.commit()
            pacient['ID'] = self.pacient['ID']
            self.flags['modifying'] = False  

        # Definição do dicionário global
        self.pacient = pacient

        # Mudança na sensibilidade dos elementos
        for i in range(len(childList) - 2):
            childList[i].set_sensitive(False)
        self.savepacient_button.set_sensitive(False)
        self.changepacientbutton.set_sensitive(True)

        # Mudança na flag de paciente carregado
        self.flags['is_pacient'] = True

        self.toastLabel.set_text("Salvo")
        self.toast.set_reveal_child(True)
        print("Paciente salvo")

    # Evento de clique no botão 'MODIFICAR PACIENTE'
    def on_changepacientbutton_clicked(self, widget):
        # Mudança na flag de modificação
        self.flags['modifying'] = True

        # Recuperação das 'entrys'
        childList = self.name_entry.get_parent().get_children()

        # Mudança na sensibilidade dos elementos
        for i in range(len(childList) - 2):
            childList[i].set_sensitive(True)
        self.savepacient_button.set_sensitive(True)
        self.changepacientbutton.set_sensitive(False)

    # Evento de clique no botão 'CARREGAR PACIENTE'
    def on_load_pacient_button_clicked(self, widget):
        # Limpeza da janela de seleção de paciente
        self.pacient_label_in_load.set_text("")

        # Limpeza do combobox de seleção de exame
        self.combo_box_set_exam.remove_all()

        # Preenchimento da janela principal com os dados do paciente
        self.name_entry.set_text(self.pacient['Nome'])
        self.age_entry.set_text(str(self.pacient['Idade']))
        self.height_entry.set_text(str(self.pacient['Altura']))
        if self.pacient['Sexo'] == 'MASCULINO':
            self.sex_combobox.set_active_id('0')
        elif self.pacient['Sexo'] == 'FEMININO':
            self.sex_combobox.set_active_id('1')
        else:
            self.sex_combobox.set_active_id('2')

        self.weight.set_text(str(self.pacient['Peso']))
        self.imc.set_text(str(self.pacient['IMC']))

        # Recuperação das 'entrys'
        childList = self.name_entry.get_parent().get_children()

        # Mudança na sensibilidade dos elementos
        for i in range(len(childList) - 2):
            childList[i].set_sensitive(False)

        self.savepacient_button.set_sensitive(False)
        self.changepacientbutton.set_sensitive(True)

        # Preenchimento do combobox de seleção de exames
        self.cur.execute("SELECT * FROM exams WHERE pac_id = (%s)", (str(self.pacient['ID'])))
        rows = self.cur.fetchall()
        i = 1
        for row in rows:
            self.combo_box_set_exam.append(str(row[0]), str(i) + ' - ' + str(row[3]))
            i += 1

        # Mudança secundária na sensibilidade dos elementos
        self.combo_box_set_exam.set_sensitive(False)
        if len(rows):
            self.combo_box_set_exam.set_sensitive(True)

        # Mudança na flag de paciente carregado
        self.flags['is_pacient'] = True

        # Mudança na visibilidade da janela de seleção de paciente
        self.load_pacient_window.hide()

    # Evento de ativação da opção de menu 'ABRIR'
    def on_open_activate(self, menuitem, data=None):

        self.flags['is_pacient'] = False

        self.pacient_label_in_load.set_text("")

        # Preenchimento do combobox de seleção de paciente
        self.combobox_in_load_pacient.remove_all()
        self.cur.execute("SELECT id, name FROM pacients ORDER BY id;")
        rows = self.cur.fetchall()
        for row in rows:
            self.combobox_in_load_pacient.append(str(row[0]), str(row[0]) + ' - ' + row[1])

        # Mudança na visibilidade da janela de seleção de paciente
        self.load_pacient_window.show()

    # Evento de mudança no combobox de seleção do paciente
    def on_combobox_in_load_pacient_changed(self, widget):
        self.load_exam_button.set_sensitive(False)

        self.pacient_label_in_load.set_text("")

        # Recuperação do ID ativo no combobox
        self.pacient['ID'] = str(self.combobox_in_load_pacient.get_active_id())

        if self.pacient['ID'] != "None":
            # Recupera o paciente selecionado do BD
            select = "SELECT * FROM pacients WHERE id = %s;" % self.pacient['ID']
            self.cur.execute(select)
            row = self.cur.fetchall()

            self.pacient = {}
            text = ""
            for i, key in enumerate(['ID', 'Nome', 'Sexo', 'Idade', 'Altura', 'Peso', 'IMC']):
                self.pacient[key] = row[0][i]
                if i != 0:
                    text += str(list(self.pacient.items())[i][0]) + ': ' + str(list(self.pacient.items())[i][1]) + '\n'

            self.pacient_label_in_load.set_text(text)

    # Evento de clique do botão cancelar na tela de carregar paciente
    def on_cancel_in_load_button_clicked(self, widget):
        self.pacient_label_in_load.set_text("")
        self.load_pacient_window.hide()

    # CAPTURA DE SINAIS, CÁLCULO DAS MÉTRICAS E APRESENTAÇÃO DOS RESULTADOS #

    def on_start_capture_button_clicked(self, widget):
        # Mudança na visibilidade da janela
        self.stand_up_window.hide()

        # Limpeza dos gráficos
        self.clear_charts()

        # Definição do tamanho da amostra
        self.amostra = 768
        self.MLs = np.zeros(self.amostra)
        self.APs = np.zeros(self.amostra)
        peso = 0.0
        peso_ = 0.0

        cal = self.wiimote.get_balance_cal()
        calibration = { 'right_top': cal[0],
                        'right_bottom': cal[1],
                        'left_top': cal[2],
                        'left_bottom': cal[3]}

        t1 = ptime.time() + self.metricas['dt']

        # Início da captura
        for i in range(self.amostra):

            # Espera de eventos enquanto são feitos os cálculos pesados
            while Gtk.events_pending():
                Gtk.main_iteration()
                self.progressbar.set_fraction(i / self.amostra)

            # Realização de captura
            readings = wbb.captura1(self.wiimote)

            # Cálculo do peso
            peso += wbb.calcWeight(readings, self.WBB['Calibração'], wbb.escala_eu)
            peso_ += wbb.calcWeight(readings, calibration, wbb.escala_eu)

            # Cálculo dos APs, MLs
            CoP_x, CoP_y = wbb.calCoP(readings, self.WBB['Calibração'], wbb.escala_eu)

            self.MLs[i] = CoP_x
            self.APs[i] = CoP_y

            # Verificação do intervalo de self.metricas['tempo']
            while ptime.time() < t1:
                pass

            t1 += self.metricas['dt']

        # Print do peso com calibração padrão
        peso_ /= self.amostra
        print('\n\nPeso com calibração padrão: {}\n\n'.format(peso_))

        # Cálculo do IMC
        peso = peso / self.amostra
        altura = float(self.pacient['Altura']) / 100.
        imc = peso / altura ** 2

        self.points_entry.set_text(str(self.amostra))

        # Preenchimento da janela principal com os dados do paciente
        self.pacient['Peso'] = round(peso, 2)
        self.pacient['IMC'] = round(imc, 1)

        self.weight.set_text(str(peso))
        self.weight.set_max_length(6)
        self.imc.set_text(str(imc))
        self.imc.set_max_length(5)
        self.save_exam_button.set_sensitive(True)

        self.calcula_metricas()
        self.apresenta_exame()

    def calcula_metricas(self):

        # Definição do intervalo entre capturas
        self.metricas['dt'] = 0.040
        self.metricas['tTotal'] = len(self.APs) * self.metricas['dt']
        self.metricas['tempo'] = np.arange(0, self.metricas['tTotal'], self.metricas['dt'])

        # Processamento do sinal
        self.metricas['APs_Processado'], self.metricas['MLs_Processado'], \
        self.metricas['AP_'], self.metricas['ML_'] = calc.geraAP_ML(self.APs, self.MLs)
        print("AP_ = ", self.metricas['AP_'])
        print("ML_ = ", self.metricas['ML_'])

        # RD
        self.metricas['dis_resultante_total'] = calc.distanciaResultante(self.metricas['APs_Processado'],
                                                                         self.metricas['MLs_Processado'])
        # MDIST
        self.metricas['dis_media'] = calc.distanciaMedia(self.metricas['dis_resultante_total'])
        # MDIST_AP
        self.metricas['dis_mediaAP'] = calc.distanciaMedia_(self.metricas['APs_Processado'])
        # MDIST_ML
        self.metricas['dis_mediaML'] = calc.distanciaMedia_(self.metricas['MLs_Processado'])

        print("MDIST = ", self.metricas['dis_media'])
        print("MDIST_AP = ", self.metricas['dis_mediaAP'])
        print("MDIST_ML = ", self.metricas['dis_mediaML'])

        # RDIST
        self.metricas['dis_rms_total'] = calc.distRMS(self.metricas['dis_resultante_total'])
        # RDIST_AP
        self.metricas['dis_rms_AP'] = calc.distRMS(self.metricas['APs_Processado'])
        # RDIST_AP
        self.metricas['dis_rms_ML'] = calc.distRMS(self.metricas['MLs_Processado'])

        print("RDIST = ", self.metricas['dis_rms_total'])
        print("RDIST_AP = ", self.metricas['dis_rms_AP'])
        print("RDIST_ML = ", self.metricas['dis_rms_ML'])

        # TOTEX
        self.metricas['totex_total'] = calc.totex(self.metricas['APs_Processado'], self.metricas['MLs_Processado'])
        # TOTEX_AP
        self.metricas['totex_AP'] = calc.totexParcial(self.metricas['APs_Processado'])
        # TOTEX_ML
        self.metricas['totex_ML'] = calc.totexParcial(self.metricas['MLs_Processado'])

        print("TOTEX = ", self.metricas['totex_total'])
        print("TOTEX_AP = ", self.metricas['totex_AP'])
        print("TOTEX_ML = ", self.metricas['totex_ML'])

        # MVELO
        self.metricas['mvelo_total'] = calc.mVelo(self.metricas['totex_total'], self.metricas['tTotal'])
        # MVELO_AP
        self.metricas['mvelo_AP'] = calc.mVelo(self.metricas['totex_AP'], self.metricas['tTotal'])
        # MVELO_ML
        self.metricas['mvelo_ML'] = calc.mVelo(self.metricas['totex_ML'], self.metricas['tTotal'])

        print("MVELO = ", self.metricas['mvelo_total'])
        print("MVELO_AP = ", self.metricas['mvelo_AP'])
        print("MVELO_ML = ", self.metricas['mvelo_ML'])

        # Cálculo dos máximos (sinal processado)
        self.metricas['max_absoluto_AP'] = np.absolute(self.metricas['APs_Processado']).max()
        self.metricas['max_absoluto_ML'] = np.absolute(self.metricas['MLs_Processado']).max()

        self.metricas['max_absoluto_AP'] *= 1.05
        self.metricas['max_absoluto_ML'] *= 1.05

        print('max_absoluto_AP:', self.metricas['max_absoluto_AP'], 'max_absoluto_ML:',
              self.metricas['max_absoluto_ML'])

        self.metricas['max_absoluto'] = max(self.metricas['max_absoluto_AP'], self.metricas['max_absoluto_ML'])

    def apresenta_exame(self):

        # Preenchimento da janela principal com as métricas
        metricas = [self.metricas['dis_mediaAP'], self.metricas['dis_mediaML'], self.metricas['dis_media'],
                    self.metricas['dis_rms_AP'], self.metricas['dis_rms_ML'], self.metricas['dis_rms_total'],
                    self.metricas['totex_AP'], self.metricas['totex_ML'], self.metricas['totex_total'],
                    self.metricas['mvelo_AP'], self.metricas['mvelo_ML'], self.metricas['mvelo_total']]

        for x in range(1, 2):
            for y in range(1, 13):
                self.grid1.get_child_at(x, y).set_text(str(round(metricas[y - 1], 6)))

        self.axis_0.set_xlim(-self.metricas['max_absoluto'], self.metricas['max_absoluto'])
        self.axis_0.set_ylim(-self.metricas['max_absoluto'], self.metricas['max_absoluto'])
        self.axis_0.plot(self.metricas['MLs_Processado'], self.metricas['APs_Processado'], '.-', color='b')
        self.canvas_0.draw()

        self.metricas['maximo'] = max([self.metricas['max_absoluto_AP'], self.metricas['max_absoluto_ML'],
                                       max(self.metricas['dis_resultante_total'])])

        self.axis_2.set_ylim(-self.metricas['maximo'], self.metricas['maximo'])
        self.axis_2.plot(self.metricas['tempo'], self.metricas['APs_Processado'], '-', color='k', label='APs')
        self.axis_2.plot(self.metricas['tempo'], self.metricas['MLs_Processado'], '--', color='b', label='MLs')
        self.axis_2.plot(self.metricas['tempo'], self.metricas['dis_resultante_total'], ':', color='g', label='DRT')
        self.axis_2.legend()
        self.canvas_2.draw()

        self.save_exam_button.set_sensitive(True)

    # ARMAZENAMENTO DOS RESULTADOS NO BANCO DE DADOS #

    # Evento de clique do botão "SALVAR EXAME"
    def on_save_exam_button_clicked(self, widget):
        # Teste se há exame
        # if self.flags['is_exam']:
        # Inserção do exame no BD
        self.cur.execute("INSERT INTO exams (APs, MLs, pac_id, usr_id) VALUES (%s, %s, %s, %s)",
                         (list(self.APs), list(self.MLs), self.pacient['ID'], self.user_ID))
        # self.cur.execute("UPDATE pacients SET weight = %f, imc = %f WHERE id = %d;" % (float(self.pacient['Peso']), float(self.pacient['IMC']), int(self.pacient['ID'])))
        self.conn.commit()

        # Limpeza do combobox de seleção
        self.combo_box_set_exam.remove_all()
        # Preenchimento do combobox de seleção
        # Fills the exams_combobox with the dates of current pacient exams
        self.cur.execute("SELECT * FROM exams WHERE pac_id = (%s)", (str(self.pacient['ID'])))
        rows = self.cur.fetchall()
        i = 1
        for row in rows:
            self.combo_box_set_exam.append(str(row[0]), str(i) + ' - ' + str(row[3]))
            i += 1

        # Mudanças nos elementos gráficos
        self.combo_box_set_exam.set_active_id("0")
        self.combo_box_set_exam.set_sensitive(True)
        self.load_exam_button.set_sensitive(True)
        self.save_exam_button.set_sensitive(False)

    def on_cancel_button_in_login_clicked(self, widget):
        print("Quit in login with cancel_button")
        self.cur.close()
        self.conn.close()
        Gtk.main_quit()

    def on_login_button_clicked(self, widget):
        self.message_dialog_window.set_transient_for(self.login_window)
        username = self.username_entry_in_login.get_text()
        password = self.password_entry_in_login.get_text()

        self.cur.execute("SELECT username FROM users;")
        rows = self.cur.fetchall()
        user_exists = False
        i = 0
        while (not user_exists) and (i < len(rows)):
            if rows[i][0] == username:
                user_exists = True
            i += 1

        self.cur.execute("SELECT crypt(%s, password) = password FROM users WHERE username = %s;", (password, username))
        row = self.cur.fetchall()

        if username == "" or not user_exists:
            self.message_dialog_window.format_secondary_text("Nome de usuário inválido, tente novamente.")
            self.message_dialog_window.show()
            self.username_entry_in_login.grab_focus()
        elif password == "" or len(password) < 8 or not (row[0][0]):
            self.message_dialog_window.format_secondary_text("Senha inválida, tente novamente.")
            self.message_dialog_window.show()
            self.password_entry_in_login.grab_focus()
        else:
            self.user_ID = str(i)
            print("Login as " + username)
            self.login_window.hide()
            self.main_window.set_title("IEM_WBB" + " - " + username)
            self.main_window.show_all()
            self.username_entry_in_login.set_text("")
            self.password_entry_in_login.set_text("")

    def on_register_new_user_button_clicked(self, widget):
        print("Register Window")

        self.full_name_entry_in_register.set_text("")
        self.username_entry_in_register.set_text("")
        self.password_entry_in_register.set_text("")
        self.password_check_entry_in_register.set_text("")
        self.email_entry_in_register.set_text("")
        self.adm_password_entry_in_register.set_text("")
        self.is_adm_button_in_register.set_active(False)

        self.full_name_entry_in_register.grab_focus()
        self.register_window.show()

    def isAdmPass(self, admPass):
        if admPass == "":
            return False

        self.cur.execute("SELECT crypt('{0}', password) = password FROM users WHERE is_adm = TRUE;".format(admPass))
        rows = self.cur.fetchall()
        i = 0
        q = len(rows)
        while i < q:
            if rows[i][0]:
                return True
            i += 1

        return False

    def on_register_user_button_clicked(self, widget):

        self.message_dialog_window.set_transient_for(self.register_window)
        name = self.full_name_entry_in_register.get_text()
        username = self.username_entry_in_register.get_text()
        password = self.password_entry_in_register.get_text()
        password_check = self.password_check_entry_in_register.get_text()
        email = self.email_entry_in_register.get_text()
        adm_password = self.adm_password_entry_in_register.get_text()
        is_adm = self.is_adm_button_in_register.get_active()

        invalid_email = validate_email(email, verify=True)

        self.cur.execute("SELECT username FROM users;")
        rows = self.cur.fetchall()
        user_exists = False
        i = 0
        q = len(rows)
        while not user_exists and (i < q):
            if rows[i][0] == username:
                user_exists = True
            i += 1

        if name == "":
            self.message_dialog_window.format_secondary_text("Nome inválido, tente novamente.")
            self.message_dialog_window.show()
            self.full_name_entry_in_register.grab_focus()
        elif username == "" or user_exists:
            self.message_dialog_window.format_secondary_text("Nome de usuário inválido, tente novamente.")
            self.message_dialog_window.show()
            self.username_entry_in_register.grab_focus()
        elif email == "" or not invalid_email:
            self.message_dialog_window.format_secondary_text("E-mail inválido, tente novamente.")
            self.message_dialog_window.show()
            self.email_entry_in_register.grab_focus()
        elif password == "" or len(password) < 8:
            self.message_dialog_window.format_secondary_text("Senha inválida, tente novamente.")
            self.message_dialog_window.show()
            self.password_entry_in_register.grab_focus()
        elif password != password_check:
            self.message_dialog_window.format_secondary_text("Senhas não correspondem, tente novamente.")
            self.message_dialog_window.show()
            self.password_check_entry_in_register.grab_focus()
        elif not self.isAdmPass(adm_password):
            self.message_dialog_window.format_secondary_text("Senha do administrador inválida, tente novamente.")
            self.message_dialog_window.show()
            self.email_entry_in_register.grab_focus()
        else:
            self.cur.execute(
                "INSERT INTO users (name, username, password, email, is_adm) VALUES ('{0}', '{1}', crypt('{2}', gen_salt('md5')), '{3}', '{4}');".format(
                    name, username, password, email, is_adm))
            self.conn.commit()
            self.register_window.hide()
            self.username_entry_in_login.grab_focus()

    def close_register_window(self, arg1, arg2):
        self.register_window.hide()
        self.username_entry_in_login.grab_focus()

        return True

    def on_cancel_in_register_button_clicked(self, widget):
        self.register_window.hide()
        self.username_entry_in_login.grab_focus()

    def onFullNameEntryInRegisterChanged(self, widget):
        fullName = widget.get_text().split(' ')
        username = ""
        for i in range(len(fullName) - 1):
            username += fullName[i][0]
        username += fullName[len(fullName) - 1]
        self.username_entry_in_register.set_text(username.lower())

    def on_save_as_activate(self, menuitem, data=None):

        # Teste se há exame e paciente selecionados
        if self.flags['is_pacient'] and self.flags['is_exam']:
            # Definição da janela
            dialog = Gtk.FileChooserDialog("Salvar como", self.main_window,
                                           Gtk.FileChooserAction.SAVE,
                                           (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                            Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

            # Definição da confirmação de sobrescrição
            dialog.set_do_overwrite_confirmation(True)

            # Adicionando filtros de tipo
            self.add_filters(dialog)

            # Definição da pasta a ser exibida
            path = str('./pacients/' + self.pacient['ID'] + ' - ' + self.pacient['Nome'])
            dialog.set_current_folder(path)

            # Definição do nome do arquivo
            dialog.set_current_name(self.pacient['Nome'] + '.xls')

            # Execução da janela
            response = dialog.run()
            # dialog.set_filename('.xls')
            if response == Gtk.ResponseType.OK:
                print(dialog.get_filename())
                manArq.importXlS(self.pacient, self.APs, self.MLs, self.exam_date, dialog.get_filename())
                print("Salvo")
                self.main_window.get_focus()
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancelado")
                self.main_window.get_focus()

            dialog.destroy()
        else:
            self.message_dialog_window.set_transient_for(self.main_window)
            self.message_dialog_window.format_secondary_text("Não há usuário ou exame carregado.")
            self.message_dialog_window.show()

        self.main_window.get_focus()

    @staticmethod
    def add_filters(dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name(".xls")
        filter_text.add_mime_type("application/x-msexcel")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Todos os arquivos")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def clear_all_main_window(self):
        self.pacient = {}
        self.flags['is_pacient'] = False
        self.flags['is_exam'] = False

        self.name_entry.set_text('')
        self.sex_combobox.set_active_id()
        self.age_entry.set_text('')
        self.height_entry.set_text('')
        self.weight.set_text('')
        self.imc.set_text('')
        self.name_entry.set_sensitive(True)
        self.age_entry.set_sensitive(True)
        self.height_entry.set_sensitive(True)
        self.sex_combobox.set_sensitive(True)

        self.combo_box_set_exam.remove_all()
        self.load_exam_button.set_sensitive(False)

        self.savepacient_button.set_sensitive(True)
        self.changepacientbutton.set_sensitive(False)

        self.clear_charts()

        self.progressbar.set_fraction(0)

        for x in range(1, 2):
            for y in range(1, 13):
                self.grid1.get_child_at(x, y).set_text("0.000000")

    def on_main_window_destroy(self, object, data=None):
        print("Quit with cancel")
        self.cur.close()
        self.conn.close()
        Gtk.main_quit()

    def on_quit_activate(self, menuitem, data=None):
        print("Quit from menu")
        self.main_window.hide()
        # self.calibration_by_points_window.hide()
        self.clear_all_main_window()
        self.username_entry_in_login.grab_focus()
        self.login_window.show()

    def on_new_activate(self, menuitem, data=None):
        self.clear_all_main_window()

    # Gets the signal of changing at exams_combobox
    def on_combo_box_set_exam_changed(self, widget):
        self.load_exam_button.set_sensitive(False)
        # Gets the active row ID at exams_combobox
        self.exam['ID'] = str(widget.get_active_id())
        if self.exam['ID'] != "None":
            self.load_exam_button.set_sensitive(True)

    # Evento de clique no botão de carregar exame
    def on_load_exam_button_clicked(self, widget):
        # Selects the active row from table exams
        select = "SELECT aps, mls, date, type FROM exams WHERE id = %s" % self.exam['ID']
        self.cur.execute(select)
        row = self.cur.fetchall()

        self.APs = np.zeros_like(row[0][0])
        self.MLs = np.zeros_like(row[0][1])

        for i in range(len(row[0][0])):
            self.APs[i] = row[0][0][i]
            self.MLs[i] = row[0][1][i]

        self.clear_charts()
        self.calcula_metricas()
        self.apresenta_exame()

    # Show new_device_window
    def on_new_device_activate(self, menuitem, data=None):
        self.device_name_in_new.set_text("")
        self.device_mac_in_new.set_text("")
        self.add_as_default_button_in_add_device.set_active(False)
        self.new_device_window.show()

    def device_exists(self, mac):
        mac = mac.upper()
        MAC = '\'' + mac + '\''
        self.cur.execute("SELECT mac FROM devices WHERE mac = %s" % MAC)
        rows = self.cur.fetchall()
        exists = False
        i = 0
        while (not exists) and (i < len(rows)):
            exists = (rows[i][0].upper() == mac)
            i += 1

        return exists

    def on_add_button_in_add_device_clicked(self, widget):

        self.message_dialog_window.set_transient_for(self.new_device_window)
        name = self.device_name_in_new.get_text()
        mac = self.device_mac_in_new.get_text()
        is_default = self.add_as_default_button_in_add_device.get_active()

        if name == "":
            self.message_dialog_window.format_secondary_text("Nome inválido, tente novamente.")
            self.message_dialog_window.show()
            self.device_name_in_new.grab_focus()
        elif (mac == "") or not (iva(mac)):
            self.message_dialog_window.format_secondary_text("MAC inválido, tente novamente.")
            self.message_dialog_window.show()
            self.device_mac_in_new.grab_focus()
        elif self.device_exists(mac):
            self.message_dialog_window.format_secondary_text("Este dispositivo já está cadastrado.")
            self.message_dialog_window.show()
            self.device_mac_in_new.grab_focus()
        else:
            self.message_dialog_window.format_secondary_text(
                "Um novo dispositivo não está calibrado, o que pode gerar dados equivocados.")
            self.message_dialog_window.show()            
            self.WBB = {'Nome': name, 'MAC': mac, 'Padrao': is_default}
            if is_default:
                self.cur.execute("UPDATE devices SET is_default = FALSE;")
            self.cur.execute("INSERT INTO devices (name, mac, is_default) VALUES (%s, %s, %s);",
                             (name, mac, is_default))
            self.conn.commit()
            self.new_device_window.hide()

    # Disconnet self.wiimote
    def on_disconnect_activate(self, menuitem, data=None):
        if self.wiimote:
            self.wiimote.close()
            self.wiimote = None
            self.flags['is_connected'] = False
            self.battery_label.set_text("Bateria:")
            self.status_image.set_from_file("./media/bt_red.png")
            self.status_label.set_text("Não conectado")

    def main_window_delete_event(self, widget, arg2):
        widget.hide()
        self.main_window.get_focus()
        return True

    def close_advanced_graphs_window(self, arg1, arg2):
        self.nt.home()
        self.boxAdvanced.remove(self.child)
        self.boxAdvanced.remove(self.nt)
        self.parent.pack_start(self.child, expand=True, fill=True, padding=0)
        self.advanced_graphs_window.hide()
        return True

    def on_cancel_in_saved_button_clicked(self, widget):
        print("Seleção de dispositivo cancelada")
        self.saved_devices_window.hide()

    def on_search_device_activate(self, menuitem, data=None):
        self.combo_box_in_search.remove_all()
        self.spinner_in_search.start()
        self.search_device_window.show()

    def on_start_search_button_clicked(self, widget):
        self.battery_label.set_text("Bateria:")
        self.flags['is_connected'] = False

        self.status_image.set_from_file("./media/bt_red.png")
        self.status_label.set_text("Não conectado")

        print("Buscando novo dispositivo")

        self.devices = connect.searchWBB()

        self.combo_box_in_search.remove_all()
        device_ID = 0
        for addr, name in self.devices:
            self.combo_box_in_search.append(str(device_ID), 'Nome: ' + name + '\nMAC: ' + addr)
            device_ID += 1

        self.connect_button_in_search.set_sensitive(True)
        self.save_device_in_search.set_sensitive(True)
        self.spinner_in_search.stop()

    def on_connect_button_in_search_clicked(self, widget):
        device_ID = int(self.combo_box_in_search.get_active_id())

        self.wiimote, self.battery = connect.connectToWBB(self.devices[device_ID][0])

        if self.wiimote:
            cal = self.wiimote.get_balance_cal()
            calibrations = {'right_top': cal[0],
                        'right_bottom': cal[1],
                        'left_top': cal[2],
                        'left_bottom': cal[3]}
            self.WBB = {'Calibração': calibrations}
            self.flags['is_connected'] = True
            self.battery_label.set_text("Bateria: " + str(int(100 * self.battery)) + "%")
            self.battery_label.set_visible(True)
            self.status_image.set_from_file("./media/bt_green.png")
            self.status_label.set_text("Conectado")
            self.capture_button.set_sensitive(True)
            self.search_device_window.hide()

            # Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 1, self.verify_bt)
            GLib.timeout_add_seconds(1, self.verify_bt)

        else:
            self.message_dialog_window.set_transient_for(self.search_device_window)
            self.message_dialog_window.format_secondary_text(
                "Não foi possível conectar-se à plataforma, tente novamente.")
            self.message_dialog_window.show()

    def on_save_device_in_search_clicked(self, widget):
        device_ID = int(self.combo_box_in_search.get_active_id())

        self.device_name_in_new.set_text(self.devices[device_ID][1])
        self.device_mac_in_new.set_text(self.devices[device_ID][0])
        self.device_mac_in_new.set_sensitive(False)
        self.new_device_window.show()

    def on_cancel_in_search_clicked(self, widget):
        self.connect_button_in_search.set_sensitive(False)
        self.save_device_in_search.set_sensitive(False)
        self.spinner_in_search.stop()
        self.search_device_window.hide()
        self.main_window.get_focus()

    # Show saved devices window
    def on_connect_to_saved_device_activate(self, menuitem, data=None):

        self.flags['is_connected'] = False

        # Fills the combobox with devices names
        self.combo_box_in_saved.remove_all()
        self.cur.execute("SELECT id, name, is_default FROM devices;")
        rows = self.cur.fetchall()
        for row in rows:
            self.combo_box_in_saved.append(str(row[0]), row[1])
            if row[2]:
                self.combo_box_in_saved.set_active_id(str(row[0]))
        self.saved_devices_window.show()

    # Saved devices selection
    def on_combo_box_in_saved_changed(self, widget):

        # Gets the active row ID at pacients_combobox
        ID = self.combo_box_in_saved.get_active_id()
        ID = str(ID)

        if ID != "None":
            # Selects the active row from table devices
            self.cur.execute("SELECT mac FROM devices WHERE id = (%s);", ID)
            row = self.cur.fetchall()

            self.mac_entry_in_saved.set_text(row[0][0])
            self.connect_in_saved_button.set_sensitive(True)

    def on_connect_in_saved_button_clicked(self, widget):
        self.battery_label.set_text("Bateria:")
        self.status_image.set_from_file("./media/bt_red.png")
        self.status_label.set_text("Não conectado")

        MAC = self.mac_entry_in_saved.get_text()

        self.wiimote, self.battery = wbb.conecta(MAC)

        if self.wiimote:
            
            self.cur.execute("SELECT name, is_default FROM devices WHERE mac = \'%s\';" % (str(MAC)))
            rows = self.cur.fetchall()
            if TESTING:
                cal = self.wiimote.get_balance_cal()
                calibration = {'right_top': cal[0],
                                'right_bottom': cal[1],
                                'left_top': cal[2],
                                'left_bottom': cal[3]}
            else:
                self.cur.execute("SELECT calibrations FROM devices WHERE mac = \'%s\';" % (str(MAC)))
                cals = self.cur.fetchall()
                row_calibration = cals[0][0]

                calibration = {'right_top': row_calibration[0],
                            'right_bottom': row_calibration[1],
                            'left_top': row_calibration[2],
                            'left_bottom': row_calibration[3]}

            self.WBB = {'Nome': rows[0][0], 'MAC': MAC, 'Calibração': calibration, 'Padrão': rows[0][1]}
            self.flags['is_connected'] = True
            self.battery_label.set_text("Bateria: " + str(int(100 * self.battery)) + "%")
            self.battery_label.set_visible(True)
            self.status_image.set_from_file("./media/bt_green.png")
            self.status_label.set_text("Conectado")
            self.connect_in_saved_button.set_sensitive(False)
            self.saved_devices_window.hide()
            self.main_window.get_focus()
            self.capture_button.set_sensitive(True)

            GLib.timeout_add_seconds(1, self.verify_bt)
            # Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 1, self.verify_bt)

        else:
            self.message_dialog_window.set_transient_for(self.saved_devices_window)
            self.message_dialog_window.format_secondary_text(
                "Não foi possível conectar-se à plataforma, tente novamente.")
            self.message_dialog_window.show()

    def on_cancel_button_in_add_device_clicked(self, widget):
        print("Adição de dispositivo cancelada")
        self.new_device_window.hide()

    def on_device_mac_activate(self, widget):
        print("Dispositivo adicionado")
        self.new_device_window.hide()

    def on_button_press_event(self, widget, event):

        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            self.child = Gtk.get_event_widget(event)
            self.parent = self.child.get_parent()
            self.parent.remove(self.child)
            self.boxAdvanced.pack_start(self.child, expand=True, fill=True, padding=0)
            self.nt = NavigationToolbar(self.child, self.advanced_graphs_window)
            self.boxAdvanced.pack_start(self.nt, expand=False, fill=True, padding=0)
            self.advanced_graphs_window.set_resizable(True)
            self.advanced_graphs_window.maximize()
            self.advanced_graphs_window.show()

        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            pass

    def on_cancel_in_standup_clicked(self, widget):
        self.stand_up_window.hide()

    def on_messagedialog_button_cancel_clicked(self, widget):
        self.message_dialog_window.hide()

    def on_capture_button_clicked(self, widget):
        self.message_dialog_window.set_transient_for(self.main_window)
        if not self.flags['is_pacient']:
            self.message_dialog_window.format_secondary_text(
                "É preciso cadastrar ou carregar um paciente para realizar o processo de captura.")
            self.message_dialog_window.show()
        elif not self.flags['is_connected']:
            self.message_dialog_window.format_secondary_text(
                "É preciso conectar a um dispositivo para realizar o processo de captura.")
            self.message_dialog_window.show()
        else:
            self.progressbar.set_fraction(0)
            self.stand_up_window.show()

    def clear_charts(self, chart=None):
        self.metricas['dt'] = 0.040
        self.metricas['tTotal'] = self.amostra * self.metricas['dt']
        charts_estatocinesigrama = [self.axis_0, self.axis_1]
        charts_estabilograma = [self.axis_2, self.axis_3]

        if not chart:
            for a in charts_estatocinesigrama:
                a.clear()
                a.set_ylabel('Anteroposterior (AP) mm')
                a.set_xlabel('Mediolateral (ML) mm')
                # a.set_xlim(-433/2, 433/2)
                # a.set_ylim(-238/2, 238/2)
                a.set_xlim(-1, 1)
                a.set_ylim(-1, 1)
                a.axhline(0, color='grey')
                a.axvline(0, color='grey')

            for a in charts_estabilograma:
                a.clear()
                a.set_xlim(0, self.metricas['tTotal'])
                a.set_ylabel('Amplitude')
                a.set_xlabel('Tempo (s)')
        else:
            chart.clear()
            if chart in charts_estatocinesigrama:
                chart.set_ylabel('Anteroposterior (AP) mm')
                chart.set_xlabel('Mediolateral (ML) mm')
                chart.set_xlim(-1, 1)
                chart.set_ylim(-1, 1)
                chart.axhline(0, color='grey')
                chart.axvline(0, color='grey')
            else:
                chart.set_xlim(0, self.metricas['tTotal'])
                chart.set_ylabel('Amplitude')
                chart.set_xlabel('Tempo (s)')

    def verify_bt(self):
        if self.wiimote:
            try:
                self.wiimote.request_status()
                self.battery = self.wiimote.state['battery'] / BATTERY_MAX
                self.battery_label.set_text("Bateria: " + str(int(100 * self.battery)) + "%")
            except RuntimeError:
                self.flags['is_connected'] = False
                self.battery_label.set_text("Bateria:")
                self.status_image.set_from_file("./media/bt_red.png")
                self.status_label.set_text("Não conectado")
                self.message_dialog_window.set_transient_for(self.main_window)
                self.message_dialog_window.format_secondary_text("Perda de conexão, tente novamente.")
                self.message_dialog_window.show()
                return False
        else:
            return False

        return True

    def resize(self, widget):
        w, h = self.main_window.get_size()
        size = 0.76 * h
        charts = [self.box_0, self.box_1, self.box_2, self.box_3]
        for c in charts:
            c.set_size_request(size, size)

    @staticmethod
    def isTime(time):
        time = time.split(':')
        if len(time) == 3:
            return True
        return False

    def on_view_changed(self, widget):
        (model, iter) = widget.get_selected()
        tv = widget.get_tree_view()

        b = tv.get_parent().get_children()[1]

        b.set_sensitive(False)

        time = model[iter][0].split(' - ')
        if self.isTime(time[0]):
            b.set_sensitive(True)
            d = '\'' + str(time[0]) + '\''
            self.exam['data'] = d


    def on_load_chart(self, widget):

        self.cur.execute("SELECT aps, mls, type FROM exams WHERE date::time = %s" % self.exam['data'])
        for row in self.cur.fetchall():
            print(row)

        return
        self.calcula_metricas()

        parent = widget.get_parent()
        child_list = parent.get_children()

        parent_ = parent.get_parent()
        child_list_ = parent_.get_children()

        canv = child_list_[1].get_children()[0]
        fig = canv.figure
        ax = fig.get_axes()[0]

        #
        #     self.calcula_metricas()
        #
        #     if self.t == 'OA':
        #         f.suptitle("Olhos Abertos")
        #     elif self.t == 'OF':
        #         f.suptitle("Olhos Fechados")
        #
        #     if tipo == 0:
        #         a.set_xlim(-self.metricas['max_absoluto'], self.metricas['max_absoluto'])
        #         a.set_ylim(-self.metricas['max_absoluto'], self.metricas['max_absoluto'])
        #         a.plot(self.metricas['MLs_Processado'], self.metricas['APs_Processado'], '.-', color='b')
        #     elif tipo == 1:
        #         a.set_ylim(-self.metricas['max_absoluto'], self.metricas['max_absoluto'])
        #         a.plot(self.metricas['tempo'], self.metricas['APs_Processado'], '-', color='k', label='APs')
        #         a.plot(self.metricas['tempo'], self.metricas['MLs_Processado'], '--', color='b', label='MLs')
        #         a.plot(self.metricas['tempo'], self.metricas['dis_resultante_total'], ':', color='g', label='DRT')
        #         a.legend()
        #
        #     c.draw()
        #
        #     self.toastLabel.set_text("Exame Carregado")
        #     self.toast.set_reveal_child(True)

    def onToastButtonClicked(self, widget):
        self.toast.set_reveal_child(False)

    def show_revealer(self):
        pass

    def on_state_changed_event(self, widget, state):
        print(state == Gtk.StateFlags(2))

    def __init__(self):
        self.conn, self.cur = bd.open_BD("iem_wbb", "localhost", "postgres", "postgres")

        '''
        #Connecting to DB
        self.conn = psycopg2.connect("dbname=iem_wbb host=localhost user=postgres password=postgres")
        #Opening DB cursor
        self.cur = self.conn.cursor()
        '''

        self.amostra = 768
        self.balance_CoP_x = np.zeros(self.amostra)
        self.balance_CoP_y = np.zeros(self.amostra)
        self.APs = np.zeros(self.amostra)
        self.MLs = np.zeros(self.amostra)

        # Dicts
        self.pacient = {}
        self.exam = {}
        self.metricas = {}
        self.WBB = {}
        self.flags = {'is_pacient': False,
                      'is_exam': False,
                      'is_connected': False,
                      'modifying': False}

        self.user_ID = None
        self.battery = None
        self.child = None
        self.parent = None
        self.nt = None
        self.wiimote = None

        # Builders
        self.iemGladeFile = "./src/iem-wbb.glade"
        self.iemBuilder = Gtk.Builder()
        self.iemBuilder.add_from_file(self.iemGladeFile)
        self.iemBuilder.connect_signals(self)

        self.commonGladeFile = "./src/common.glade"
        self.commonBuilder = Gtk.Builder()
        self.commonBuilder.add_from_file(self.commonGladeFile)
        self.commonBuilder.connect_signals(self)

        # Windows
        self.login_window = self.iemBuilder.get_object("login_window")
        self.login_window.set_icon_from_file('./media/balance.ico')
        self.register_window = self.iemBuilder.get_object("register_window")
        self.main_window = self.iemBuilder.get_object("main_window")
        self.stand_up_window = self.iemBuilder.get_object("stand_up_window")
        self.load_pacient_window = self.iemBuilder.get_object("load_pacient_window")
        self.advanced_graphs_window = self.iemBuilder.get_object("advanced_graphs_window")
        self.save_as_dialog = self.iemBuilder.get_object("save_as_dialog")

        self.message_dialog_window = self.commonBuilder.get_object("message_dialog_window")
        self.new_device_window = self.commonBuilder.get_object("new_device_window")
        self.search_device_window = self.commonBuilder.get_object("search_device_window")
        self.saved_devices_window = self.commonBuilder.get_object("saved_devices_window")
        self.register_window = self.iemBuilder.get_object("register_window")

        # Boxes
        self.boxOriginal = self.iemBuilder.get_object("boxOriginal")
        self.boxProcessado = self.iemBuilder.get_object("boxProcessado")
        self.boxFourier = self.iemBuilder.get_object("boxFourier")
        self.boxAdvanced = self.iemBuilder.get_object("boxAdvanced")
        self.box0 = self.iemBuilder.get_object("box0")
        self.box1 = self.iemBuilder.get_object("box1")
        self.box2 = self.iemBuilder.get_object("box2")
        self.box3 = self.iemBuilder.get_object("box3")

        # Images
        self.login_image = self.iemBuilder.get_object("login_image")
        self.login_image.set_from_file('./media/cadeado.png')
        self.image_in_saved = self.commonBuilder.get_object("image_in_saved")
        self.image_in_saved.set_from_file('./media/syncButton.png')
        self.search_image = self.commonBuilder.get_object("search_image")
        self.search_image.set_from_file('./media/syncButton.png')
        self.pacient_image = self.iemBuilder.get_object("pacient_image")
        self.pacient_image.set_from_file('./media/paciente.png')

        # Buttons
        self.save_device_in_search = self.commonBuilder.get_object("save_device_in_search")
        self.connect_button_in_search = self.commonBuilder.get_object("connect_button_in_search")
        self.connect_in_saved_button = self.commonBuilder.get_object("connect_in_saved_button")
        self.add_as_default_button_in_add_device = self.commonBuilder.get_object("add_as_default_button_in_add_device")
        self.savepacient_button = self.iemBuilder.get_object("savepacient_button")
        self.changepacientbutton = self.iemBuilder.get_object("changepacientbutton")
        self.load_exam_button = self.iemBuilder.get_object("load_exam_button")
        self.button_load_chart_0 = self.iemBuilder.get_object("button_load_chart_0")
        self.button_load_chart_1 = self.iemBuilder.get_object("button_load_chart_1")
        self.button_load_chart_2 = self.iemBuilder.get_object("button_load_chart_2")
        self.button_load_chart_3 = self.iemBuilder.get_object("button_load_chart_3")
        self.capture_button = self.iemBuilder.get_object("capture_button")
        self.save_exam_button = self.iemBuilder.get_object("save_exam_button")
        self.is_adm_button_in_register = self.iemBuilder.get_object("is_adm_button_in_register")

        # Entrys
        self.name_entry = self.iemBuilder.get_object("name_entry")
        self.age_entry = self.iemBuilder.get_object("age_entry")
        self.height_entry = self.iemBuilder.get_object("height_entry")
        self.weight = self.iemBuilder.get_object("weight")
        self.imc = self.iemBuilder.get_object("imc")
        self.points_entry = self.iemBuilder.get_object("points_entry")

        self.username_entry_in_login = self.iemBuilder.get_object("username_entry_in_login")
        self.password_entry_in_login = self.iemBuilder.get_object("password_entry_in_login")
        self.password_entry_in_login.set_activates_default(True)
        self.device_name_in_new = self.commonBuilder.get_object("device_name_in_new")
        self.device_mac_in_new = self.commonBuilder.get_object("device_mac_in_new")
        self.mac_entry_in_saved = self.commonBuilder.get_object("mac_entry_in_saved")

        self.full_name_entry_in_register = self.iemBuilder.get_object("full_name_entry_in_register")
        self.username_entry_in_register = self.iemBuilder.get_object("username_entry_in_register")
        self.password_entry_in_register = self.iemBuilder.get_object("password_entry_in_register")
        self.password_check_entry_in_register = self.iemBuilder.get_object("password_check_entry_in_register")
        self.email_entry_in_register = self.iemBuilder.get_object("email_entry_in_register")
        self.adm_password_entry_in_register = self.iemBuilder.get_object("adm_password_entry_in_register")

        # Combo-Boxes
        self.sex_combobox = self.iemBuilder.get_object("sex_combobox")
        self.combo_box_set_exam = self.iemBuilder.get_object("combo_box_set_exam")
        self.combo_box_in_saved = self.commonBuilder.get_object("combo_box_in_saved")
        self.combo_box_in_search = self.commonBuilder.get_object("combo_box_in_search")
        self.combobox_in_load_pacient = self.iemBuilder.get_object("combobox_in_load_pacient")

        # Events
        self.login_window.connect('destroy', Gtk.main_quit)
        self.register_window.connect("delete-event", self.close_register_window)
        self.search_device_window.connect("delete-event", self.main_window_delete_event)
        self.new_device_window.connect("delete-event", self.main_window_delete_event)
        self.stand_up_window.connect("delete-event", self.main_window_delete_event)
        self.saved_devices_window.connect("delete-event", self.main_window_delete_event)
        self.load_pacient_window.connect("delete-event", self.main_window_delete_event)
        self.advanced_graphs_window.connect("delete-event", self.close_advanced_graphs_window)

        # Spinners
        self.spinner_in_search = self.commonBuilder.get_object("spinner_in_search")

        # Labels
        self.pacient_label_in_load = self.iemBuilder.get_object("pacient_label_in_load")

        # Charts
        self.fig = plt.figure()
        self.axis_0 = self.fig.add_subplot(111)

        self.fig_1 = plt.figure()
        self.axis_1 = self.fig_1.add_subplot(111)

        self.fig_2 = plt.figure()
        self.axis_2 = self.fig_2.add_subplot(111)

        self.fig_3 = plt.figure()
        self.axis_3 = self.fig_3.add_subplot(111)

        self.canvas_0 = FigureCanvas(self.fig)
        self.box_0 = Gtk.Box()
        self.box_0.pack_start(self.canvas_0, expand=True, fill=True, padding=0)

        self.canvas_1 = FigureCanvas(self.fig_1)
        self.box_1 = Gtk.Box()
        self.box_1.pack_start(self.canvas_1, expand=True, fill=True, padding=0)

        self.canvas_2 = FigureCanvas(self.fig_2)
        self.box_2 = Gtk.Box()
        self.box_2.pack_start(self.canvas_2, expand=True, fill=True, padding=0)

        self.canvas_3 = FigureCanvas(self.fig_3)
        self.box_3 = Gtk.Box()
        self.box_3.pack_start(self.canvas_3, expand=True, fill=True, padding=0)

        self.clear_charts()

        boxes = [self.box_0, self.box_1, self.box_2, self.box_3]
        for b in boxes:
            b.connect('button-press-event', self.on_button_press_event)
            b.connect('state-flags-changed', self.on_state_changed_event)

        # Grid
        self.grid1 = self.iemBuilder.get_object("grid1")
        for m in range(1, 13):
            self.grid1.attach(Gtk.Entry.new(), 2, m, 1, 1)
            self.grid1.get_child_at(2, m).set_text('0.000000')
            self.grid1.get_child_at(2, m).set_editable(False)
            self.grid1.get_child_at(2, m).set_width_chars(8)

        self.clear_charts()

        # TreeViews
        self.view_0 = Gtk.TreeView()
        self.view_1 = Gtk.TreeView()
        self.view_2 = Gtk.TreeView()
        self.view_3 = Gtk.TreeView()
        views = [self.view_0, self.view_1, self.view_2, self.view_3]

        for v in views:
            store = Gtk.TreeStore(str)
            self.cur.execute("SELECT * FROM pacients ORDER BY name;")
            p = self.cur.fetchall()
            for pac in p:
                nome = store.append(None, [pac[1]])
                self.cur.execute("SELECT date::date FROM exams WHERE pac_id = %s;" % (pac[0]))
                d = self.cur.fetchall()
                for dat in list(set(d)):
                    data = store.append(nome, [str(dat[0])])
                    self.cur.execute("SELECT date::time, type FROM exams WHERE date::date = %s and pac_id = %s;" %
                                     ('\'' + str(dat[0]) + '\'', pac[0]))
                    h = self.cur.fetchall()
                    for hr in h:
                        store.append(data, [str(hr[0]) + ' - ' + str(hr[1])])

            # the treeview shows the model
            # create a treeview on the model store
            v.set_model(store)
            v.get_selection().connect("changed", self.on_view_changed)
            # the cellrenderer for the column - text
            renderer_exams = Gtk.CellRendererText()
            # the column is created
            column_exams = Gtk.TreeViewColumn(
                "Exames por Paciente", renderer_exams, text=0)
            # and it is appended to the treeview
            v.append_column(column_exams)

            # the exams are sortable by pacient
            column_exams.set_sort_column_id(0)
            v.set_sensitive(False)

        # add the treeview to the window
        self.chart_button_0 = Gtk.Button("Carregar")
        self.chart_button_1 = Gtk.Button("Carregar")
        self.chart_button_2 = Gtk.Button("Carregar")
        self.chart_button_3 = Gtk.Button("Carregar")

        buttons = [self.chart_button_0, self.chart_button_1, self.chart_button_2, self.chart_button_3]
        chart_boxes = [self.box_0, self.box_1, self.box_2, self.box_3]
        boxes = [self.box0, self.box1, self.box2, self.box3]

        for i in range(len(buttons)):
            box = Gtk.VBox()
            label = Gtk.Label("Exame " + str(i % 2 + 1))
            boxH = Gtk.HBox()
            box.set_homogeneous(False)
            box.add(views[i])
            buttons[i].set_sensitive(False)
            buttons[i].set_valign(Gtk.Align.CENTER)
            buttons[i].set_halign(Gtk.Align.BASELINE)
            buttons[i].connect('clicked', self.on_load_chart)
            box.add(buttons[i])
            boxH.set_spacing(10)
            boxH.add(box)
            boxH.add(chart_boxes[i])
            boxes[i].add(label)
            boxes[i].add(boxH)

        # StatusBar
        self.status_image = self.iemBuilder.get_object("status_image")
        self.status_image.set_from_file('./media/bt_red.png')
        self.status_label = self.iemBuilder.get_object("status_label")
        self.battery_label = self.iemBuilder.get_object("battery_label")
        self.progressbar = self.iemBuilder.get_object("progressbar")

        # Toasts
        self.toast = self.iemBuilder.get_object("toast")
        self.toastLabel = self.iemBuilder.get_object("toastLabel")
        self.toastButton = self.iemBuilder.get_object("toastButton")

        ''' Login '''
        # self.login_window.show_all()
        self.main_window.maximize()
        self.resize(self.main_window)
        self.main_window.show_all()


if __name__ == "__main__":
    main = iemWbb()
    Gtk.main()
