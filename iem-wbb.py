#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('src')
sys.path.append('media')

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango

import calculos as calc
import conexao as connect
import ManipularArquivo as manArq
import bancoDeDados as bd
import psycopg2

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

class Iem_wbb:
    
    def on_save_as_activate(self, menuitem, data=None):
        path = str('./pacients/' + self.pacient['ID'] + ' - ' + self.pacient['Nome'])

        if(self.is_pacient and self.is_exam):
            dialog = Gtk.FileChooserDialog("Salvar como", self.main_window,
                Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

            dialog.set_do_overwrite_confirmation(True)

            self.add_filters(dialog)
            dialog.set_current_folder(path)
            dialog.set_current_name(self.pacient['Nome']+'.xls')

            response = dialog.run()
            dialog.set_filename('.xls')
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

    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name(".xls")
        filter_text.add_mime_type("application/x-msexcel")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Todos os arquivos")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def on_cancel_button_in_login_clicked(self, widget):
        print("Quit in login with cancel_button")
        self.cur.close()
        self.conn.close()
        Gtk.main_quit()

    def clear_all_main_window(self):
        self.pacient = {}
        self.is_pacient = False

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

    def on_login_button_clicked(self, widget):
        self.message_dialog_window.set_transient_for(self.login_window)
        username = self.username_entry_in_login.get_text()
        password = self.password_entry_in_login.get_text()

        self.cur.execute("SELECT username FROM users;")
        rows = self.cur.fetchall()
        user_exists = False
        i = 0
        while (not (user_exists)) and (i<len(rows)):
            if(rows[i][0] == username):
                user_exists = True
            i+=1

        self.cur.execute("SELECT crypt(%s, password) = password FROM users WHERE username = %s;", (password, username))
        row = self.cur.fetchall()

        if(username == "" or not (user_exists)):
            self.message_dialog_window.format_secondary_text("Nome de usuário inválido, tente novamente.")
            self.message_dialog_window.show()
            self.username_entry_in_login.grab_focus()
        elif(password == "" or len(password) < 8 or not (row[0][0])):
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

        #Window
        self.register_window = self.iemBuilder.get_object("register_window")

        #Entrys
        self.full_name_entry_in_register = self.iemBuilder.get_object("full_name_entry_in_register")
        self.username_entry_in_register = self.iemBuilder.get_object("username_entry_in_register")
        self.password_entry_in_register = self.iemBuilder.get_object("password_entry_in_register")
        self.password_check_entry_in_register = self.iemBuilder.get_object("password_check_entry_in_register")
        self.email_entry_in_register = self.iemBuilder.get_object("email_entry_in_register")
        self.adm_password_entry_in_register = self.iemBuilder.get_object("adm_password_entry_in_register")

        #Button
        self.is_adm_button_in_register = self.iemBuilder.get_object("is_adm_button_in_register")

        self.full_name_entry_in_register.set_text("")
        self.username_entry_in_register.set_text("")
        self.password_entry_in_register.set_text("")
        self.password_check_entry_in_register.set_text("")
        self.email_entry_in_register.set_text("")
        self.adm_password_entry_in_register.set_text("")
        self.is_adm_button_in_register.set_active(False)

        self.full_name_entry_in_register.grab_focus()
        self.register_window.show()

    def isAdmPass(self,admPass):
        if (admPass == ""):
            return False

        self.cur.execute("SELECT crypt('{0}', password) = password FROM users WHERE is_adm = TRUE;".format(admPass))
        rows = self.cur.fetchall()
        i = 0
        q = len(rows)
        while(i<q):
            print (rows[i][0])
            if(rows[i][0]):
                return True
            i+=1

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

        is_valid_email = validate_email(email, verify=True)

        self.cur.execute("SELECT username FROM users;")
        rows = self.cur.fetchall()
        user_exists = False
        i = 0
        q = len(rows)
        while (not (user_exists) and (i<q)):
            if(rows[i][0] == username):
                user_exists = True
            i+=1

        if(name == ""):
            self.message_dialog_window.format_secondary_text("Nome inválido, tente novamente.")
            self.message_dialog_window.show()
            self.full_name_entry_in_register.grab_focus()
        elif(username == "" or user_exists):
            self.message_dialog_window.format_secondary_text("Nome de usuário inválido, tente novamente.")
            self.message_dialog_window.show()
            self.username_entry_in_register.grab_focus()
        elif(email == "" or not is_valid_email):
            self.message_dialog_window.format_secondary_text("E-mail inválido, tente novamente.")
            self.message_dialog_window.show()
            self.email_entry_in_register.grab_focus()
        elif(password == "" or len(password) < 8):
            self.message_dialog_window.format_secondary_text("Senha inválida, tente novamente.")
            self.message_dialog_window.show()
            self.password_entry_in_register.grab_focus()
        elif(password != password_check):
            self.message_dialog_window.format_secondary_text("Senhas não correspondem, tente novamente.")
            self.message_dialog_window.show()
            self.password_check_entry_in_register.grab_focus()
        elif(not self.isAdmPass(adm_password)):
            self.message_dialog_window.format_secondary_text("Senha do administrador inválida, tente novamente.")
            self.message_dialog_window.show()
            self.email_entry_in_register.grab_focus()
        else:
            self.cur.execute("INSERT INTO users (name, username, password, email, is_adm) VALUES ('{0}', '{1}', crypt('{2}', gen_salt('md5')), '{3}', '{4}');".format(name, username, password, email, is_adm))
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

    def on_main_window_destroy(self, object, data=None):
        print("Quit with cancel")
        self.cur.close()
        self.conn.close()
        Gtk.main_quit()

    def on_quit_activate(self, menuitem, data=None):
        print("Quit from menu")
        self.main_window.hide()
        #self.calibration_by_points_window.hide()
        self.clear_all_main_window()
        self.username_entry_in_login.grab_focus()
        self.login_window.show()

    def on_new_activate(self, menuitem, data=None):
        self.clear_all_main_window()

    def on_open_activate(self, menuitem, data=None):

        self.is_pacient = False

        self.pacient_label_in_load.set_text("")

        #Fills the combobox with pacients names
        self.combobox_in_load_pacient.remove_all()
        self.cur.execute("SELECT id, name FROM pacients ORDER BY id;")
        rows = self.cur.fetchall()
        for row in rows:
            self.combobox_in_load_pacient.append(str(row[0]),str(row[0]) + ' - ' + row[1])

        #Shows the window to load a pacient
        self.load_pacient_window.show()

    #Gets the signal of changing at pacients_combobox
    def on_combobox_in_load_pacient_changed(self, widget):

        self.pacient_label_in_load.set_text("")

        #Gets the active row ID at pacients_combobox
        ID = self.combobox_in_load_pacient.get_active_id()
        ID = str(ID)

        if(ID != "None"):
            #Selects the active row from table pacients
            select = "SELECT * FROM pacients WHERE id = %s;" % (ID)
            self.cur.execute(select)
            row = self.cur.fetchall()

            #Fills the pacient with row content
            name = str(row[0][1])
            sex = str(row[0][2])
            sex = sex[0]
            age = str(row[0][3])
            height = str(row[0][4])
            weight = str(row[0][5])
            imc = str(row[0][6])

            self.pacient_label_in_load.set_text('Nome: ' + name +
                '\n' + 'Sexo: ' + sex +
                '\n' + 'Idade: ' + age +
                '\n' + 'Altura: ' + height +
                '\n' + 'Peso: ' + weight +
                '\n' + 'IMC: ' + imc)

            self.pacient = {'Nome': name, 'ID': ID, 'Sexo': sex, 'Idade': age, 'Altura': height, 'Peso' : weight, 'IMC': imc}

    def on_load_pacient_button_clicked(self, widget):

        self.is_pacient = True

        #Clears charts and label contents
        self.pacient_label_in_load.set_text("")
        self.combo_box_set_exam.remove_all()

        self.clear_charts()

        #Fill the main window with pacient data
        self.name_entry.set_text(self.pacient['Nome'])
        self.age_entry.set_text(self.pacient['Idade'])
        self.height_entry.set_text(self.pacient['Altura'])
        if(self.pacient['Sexo'] == 'M'):
            self.sex_combobox.set_active_id('0')
        elif(self.pacient['Sexo'] == 'F'):
            self.sex_combobox.set_active_id('1')
        else:
            self.sex_combobox.set_active_id('2')

        self.weight.set_text(self.pacient['Peso'])
        self.imc.set_text(self.pacient['IMC'])
        self.sex_combobox.set_sensitive(False)
        self.name_entry.set_sensitive(False)
        self.age_entry.set_sensitive(False)
        self.height_entry.set_sensitive(False)
        self.savepacient_button.set_sensitive(False)
        self.changepacientbutton.set_sensitive(True)
        self.load_pacient_window.hide()
        self.capture_button.set_sensitive(True)

        #Fills the exams_combobox with the dates of current pacient exams
        self.cur.execute("SELECT * FROM exams WHERE pac_id = (%s)", (self.pacient['ID']))
        rows = self.cur.fetchall()
        i=1
        for row in rows:
            self.combo_box_set_exam.append(str(row[0]), str(i) + ' - ' + str(row[3]))
            i+=1

        if(len(rows)):
            self.combo_box_set_exam.set_sensitive(True)
            self.load_exam_button.set_sensitive(True)
        else:
            self.combo_box_set_exam.set_sensitive(False)
            self.load_exam_button.set_sensitive(False)

    def on_cancel_in_load_button_clicked(self, widget):
        self.pacient_label_in_load.set_text("")
        self.load_pacient_window.hide()

    #Gets the signal of changing at exams_combobox
    def on_combo_box_set_exam_changed(self, widget):
        #Gets the active row ID at exams_combobox
        ID = self.combo_box_set_exam.get_active_id()
        ID = str(ID)

        if(ID != "None"):
            #Selects the active row from table exams
            select = "SELECT aps, mls, date, type FROM exams WHERE id = %s" % (ID)
            self.cur.execute(select)
            row = self.cur.fetchall()

            self.APs = np.zeros_like(row[0][0])
            self.MLs = np.zeros_like(row[0][1])

            for i in range(len(row[0][0])):
                self.APs[i] = row[0][0][i]
                self.MLs[i] = row[0][1][i]

            print(row)

            self.exam_date = row[0][2]
            self.exam_type = row[0][3]
            print(type(self.exam_date), self.exam_type)

    def on_load_exam_button_clicked(self, widget):
        dt = 0.040
        tTotal = len(self.APs) * dt
        tempo = np.arange(0, tTotal, 0.040)

        max_absoluto_AP = calc.valorAbsoluto(min(self.APs), max(self.APs))
        max_absoluto_ML = calc.valorAbsoluto(min(self.MLs), max(self.MLs))

        max_absoluto_AP *= 1.25
        max_absoluto_ML *= 1.25

        print('max_absoluto_AP:',max_absoluto_AP,'max_absoluto_ML:',max_absoluto_ML)

        self.clear_charts()

        APs_Processado, MLs_Processado, AP_, ML_ = calc.geraAP_ML(self.APs, self.MLs)
        print("AP_ = ", AP_)
        print("ML_ = ", ML_)
        #RD
        dis_resultante_total = calc.distanciaResultante(APs_Processado, MLs_Processado)

        #? Isto não faz sentido
        #dis_resultante_AP = calc.distanciaResultanteParcial(APs_Processado)
        #dis_resultante_ML = calc.distanciaResultanteParcial(MLs_Processado)

        #MDIST
        dis_media = calc.distanciaMedia(dis_resultante_total)

        #MDIST_AP
        dis_mediaAP = calc.distanciaMedia_(APs_Processado)
        #MDIST_ML
        dis_mediaML = calc.distanciaMedia_(MLs_Processado)

        print("MDIST = ", dis_media)
        print("MDIST_AP = ", dis_mediaAP)
        print("MDIST_ML = ", dis_mediaML)

        #RDIST
        dis_rms_total = calc.distRMS(dis_resultante_total)
        #dis_rms_AP = calc.distRMS(dis_resultante_AP)
        #dis_rms_ML = calc.distRMS(dis_resultante_ML)
        #RDIST_AP
        dis_rms_AP = calc.distRMS(APs_Processado)
        #RDIST_AP
        dis_rms_ML = calc.distRMS(MLs_Processado)

        print("RDIST = ", dis_rms_total)
        print("RDIST_AP = ", dis_rms_AP)
        print("RDIST_ML = ", dis_rms_ML)

        #totex_total = calc.totex(APs_Processado, MLs_Processado)
        #TOTEX
        totex_total = calc.totex(APs_Processado, MLs_Processado)
        #TOTEX_AP
        totex_AP = calc.totexParcial(APs_Processado)
        #TOTEX_ML
        totex_ML = calc.totexParcial(MLs_Processado)

        print("TOTEX = ", totex_total)
        print("TOTEX_AP = ", totex_AP)
        print("TOTEX_ML = ", totex_ML)

        #MVELO
        mvelo_total = calc.mVelo(totex_total, tTotal)
        #MVELO_AP
        mvelo_AP = calc.mVelo(totex_AP, tTotal)
        #MVELO_ML
        mvelo_ML =  calc.mVelo(totex_ML, tTotal)

        print("MVELO = ", mvelo_total)
        print("MVELO_AP = ", mvelo_AP)
        print("MVELO_ML = ", mvelo_ML)

        metricas = [dis_mediaAP, dis_mediaML, dis_media, dis_rms_AP, dis_rms_ML, dis_rms_total, totex_AP, totex_ML, totex_total, mvelo_AP, mvelo_ML, mvelo_total]

        for x in range(1, 2):
            for y in range(1, 13):
                self.grid1.get_child_at(x, y).set_text(str(round(metricas[y-1], 6)))
        
        '''
        self.entry_Mdist_TOTAL_OA.set_text(str(dis_media))
        self.entry_Mdist_AP_OA.set_text(str(dis_mediaAP))
        self.entry_Mdist_ML_OA.set_text(str(dis_mediaML))

        self.entry_Rdist_TOTAL_OA.set_text(str(dis_rms_total))
        self.entry_Rdist_AP_OA.set_text(str(dis_rms_AP))
        self.entry_Rdist_ML_OA.set_text(str(dis_rms_ML))

        self.entry_TOTEX_TOTAL_OA.set_text(str(totex_total))
        self.entry_TOTEX_AP_OA.set_text(str(totex_AP))
        self.entry_TOTEX_ML_OA.set_text(str(totex_ML))

        self.entry_MVELO_TOTAL_OA.set_text(str(mvelo_total))
        self.entry_MVELO_AP_OA.set_text(str(mvelo_AP))
        self.entry_MVELO_ML_OA.set_text(str(mvelo_ML))
        '''

        #max_absoluto_AP = calc.valorAbsoluto(min(APs_Processado), max(APs_Processado))
        #max_absoluto_ML = calc.valorAbsoluto(min(MLs_Processado), max(MLs_Processado))

        max_absoluto_AP = np.absolute(APs_Processado).max()
        max_absoluto_ML = np.absolute(MLs_Processado).max()

        max_absoluto_AP *=1.05
        max_absoluto_ML *=1.05

        print('max_absoluto_AP:', max_absoluto_AP, 'max_absoluto_ML:', max_absoluto_ML)

        self.axis_0_OA.set_xlim(-max_absoluto_ML, max_absoluto_ML)
        self.axis_0_OA.set_ylim(-max_absoluto_AP, max_absoluto_AP)
        self.axis_0_OA.plot(MLs_Processado, APs_Processado,'.-',color='r')
        self.canvas_0_OA.draw()

        #w1 = self.box_0_OA.get_allocation().width

        #h1 = max_absoluto_AP*w1//max_absoluto_ML
        
        #self.box_0_OA.set_size_request(w1, h1)

        '''self.axis_0_OF.set_xlim(-max_absoluto_ML, max_absoluto_ML)
        self.axis_0_OF.set_ylim(-max_absoluto_AP, max_absoluto_AP)
        self.axis_0_OF.plot(MLs_Processado, APs_Processado,'.-',color='g')
        self.canvas_0_OF.draw()'''

        self.maximo = max([max_absoluto_AP, max_absoluto_ML, max(dis_resultante_total)])

        self.axis_1_OA.set_ylim(-self.maximo, self.maximo)
        self.axis_1_OA.plot(tempo, APs_Processado, color='k', label='APs')
        self.axis_1_OA.plot(tempo, MLs_Processado, color='m', label='MLs')
        self.axis_1_OA.plot(tempo, dis_resultante_total, color='g', label='DRT')
        self.axis_1_OA.legend()
        self.canvas_1_OA.draw()

        self.points_entry.set_text(str(len(self.APs)))

    #Show new_device_window
    def on_new_device_activate(self, menuitem, data=None):
        self.device_name_in_new.set_text("")
        self.device_mac_in_new.set_text("")
        self.add_as_default_button_in_add_device.set_active(False)
        self.new_device_window.show()

    def device_exists(self, mac):
        mac = mac.upper()
        MAC = '\''+mac+'\''
        self.cur.execute("SELECT mac FROM devices WHERE mac = %s" % MAC)
        rows = self.cur.fetchall()
        exists = False
        i = 0
        while (not (exists)) and (i<len(rows)):
            exists = (rows[i][0].upper() == mac)
            i+=1

        return exists

    def on_add_button_in_add_device_clicked(self, widget):

        self.message_dialog_window.set_transient_for(self.new_device_window)
        name = self.device_name_in_new.get_text()
        mac = self.device_mac_in_new.get_text()
        is_default = self.add_as_default_button_in_add_device.get_active()

        if (name == ""):
            self.message_dialog_window.format_secondary_text("Nome inválido, tente novamente.")
            self.message_dialog_window.show()
            self.device_name_in_new.grab_focus()
        elif((mac == "") or not (iva(mac))):
            self.message_dialog_window.format_secondary_text("MAC inválido, tente novamente.")
            self.message_dialog_window.show()
            self.device_mac_in_new.grab_focus()
        elif(self.device_exists(mac)):
            self.message_dialog_window.format_secondary_text("Este dispositivo já está cadastrado.")
            self.message_dialog_window.show()
            self.device_mac_in_new.grab_focus()
        else:
            self.message_dialog_window.format_secondary_text("Um novo dispositivo não está calibrado, o que pode gerar dados equivocados.")
            self.message_dialog_window.show()
            self.WBB = {'Nome':name, 'MAC':mac, 'Padrao' : is_default}
            if(is_default):
                self.cur.execute("UPDATE devices SET is_default = FALSE;")
            self.cur.execute("INSERT INTO devices (name, mac, is_default) VALUES (%s, %s, %s);", (name, mac, is_default))
            self.conn.commit()
            self.new_device_window.hide()

    #Disconnet self.wiimote
    def on_disconnect_activate(self, menuitem, data=None):
        if(self.wiimote):
            self.wiimote.close()
            self.wiimote = None
            self.is_connected = False
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
        self.is_connected = False

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

        if(self.wiimote):
            self.is_connected = True
            self.battery_label.set_text("Bateria: " + str(int(100*self.battery))+"%")
            self.battery_label.set_visible(True)
            self.status_image.set_from_file("./media/bt_green.png")
            self.status_label.set_text("Conectado")
            self.capture_button.set_sensitive(True)
            self.search_device_window.hide()

            #Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 1, self.verify_bt)
            GLib.timeout_add_seconds(1, self.verify_bt)

        else:
            self.message_dialog_window.set_transient_for(self.search_device_window)
            self.message_dialog_window.format_secondary_text("Não foi possível conectar-se à plataforma, tente novamente.")
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

    #Show saved devices window
    def on_connect_to_saved_device_activate(self, menuitem, data=None):

        self.is_connected = False

        #Fills the combobox with devices names
        self.combo_box_in_saved.remove_all()
        self.cur.execute("SELECT id, name, is_default FROM devices;")
        rows = self.cur.fetchall()
        for row in rows:
            self.combo_box_in_saved.append(str(row[0]), row[1])
            if(row[2]):
                self.combo_box_in_saved.set_active_id(str(row[0]))
        self.saved_devices_window.show()

    #Saved devices selection
    def on_combo_box_in_saved_changed(self, widget):

        #Gets the active row ID at pacients_combobox
        ID = self.combo_box_in_saved.get_active_id()
        ID = str(ID)

        if(ID != "None"):
            #Selects the active row from table devices
            self.cur.execute("SELECT mac FROM devices WHERE id = (%s);", (ID))
            row = self.cur.fetchall()

            self.mac_entry_in_saved.set_text(row[0][0])
            self.connect_in_saved_button.set_sensitive(True)

    def on_connect_in_saved_button_clicked(self, widget):
        self.battery_label.set_text("Bateria:")
        self.status_image.set_from_file("./media/bt_red.png")
        self.status_label.set_text("Não conectado")

        MAC = self.mac_entry_in_saved.get_text()

        self.wiimote, self.battery = wbb.conecta(MAC)

        if(self.wiimote):

            self.cur.execute("SELECT name, calibrations, is_default FROM devices WHERE mac = \'%s\';" % (str(MAC)))
            rows = self.cur.fetchall()
            row_calibration = rows[0][1]

            calibration = { 'right_top':    row_calibration[0],
                            'right_bottom': row_calibration[1],
                            'left_top':     row_calibration[2],
                            'left_bottom':  row_calibration[3] }

            self.WBB = {'Nome': rows[0][0], 'MAC': MAC, 'Calibração': calibration, 'Padrão': rows[0][2]}

            self.is_connected = True
            self.battery_label.set_text("Bateria: " + str(int(100*self.battery))+"%")
            self.battery_label.set_visible(True)
            self.status_image.set_from_file("./media/bt_green.png")
            self.status_label.set_text("Conectado")
            self.connect_in_saved_button.set_sensitive(False)
            self.saved_devices_window.hide()
            self.main_window.get_focus()
            self.capture_button.set_sensitive(True)

            GLib.timeout_add_seconds(1, self.verify_bt)
            #Gdk.threads_add_timeout(GLib.PRIORITY_HIGH_IDLE, 1, self.verify_bt)

        else:
            self.message_dialog_window.set_transient_for(self.saved_devices_window)
            self.message_dialog_window.format_secondary_text("Não foi possível conectar-se à plataforma, tente novamente.")
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

    def on_savepacient_button_clicked(self, widget):

        self.is_pacient = False

        name = self.name_entry.get_text()
        sex = self.sex_combobox.get_active_text()
        age = self.age_entry.get_text()
        height = self.height_entry.get_text()

        if (name == ""):
            self.message_dialog_window.format_secondary_text("Nome inválido, tente novamente.")
            self.message_dialog_window.show()
            self.name_entry.grab_focus()
        elif(sex == ""):
            self.message_dialog_window.format_secondary_text("Sexo inválido, tente novamente.")
            self.message_dialog_window.show()
            self.sex_combobox.grab_focus()
        elif(age == ""):
            self.message_dialog_window.format_secondary_text("Idade inválida, tente novamente.")
            self.message_dialog_window.show()
            self.age_entry.grab_focus()
        elif(height == ""):
            self.message_dialog_window.format_secondary_text("Altura inválida, tente novamente.")
            self.message_dialog_window.show()
            self.height_entry.grab_focus()
        else:
            height = height.replace(',', '.', 1)
            self.savepacient_button.set_sensitive(False)
            self.height_entry.set_text(height)
            self.name_entry.set_sensitive(False)
            self.sex_combobox.set_sensitive(False)
            self.age_entry.set_sensitive(False)
            self.height_entry.set_sensitive(False)
            self.capture_button.set_sensitive(True)
            if not self.modifying:
                self.cur.execute("INSERT INTO pacients (name, sex, age, height) VALUES (%s, %s, %s, %s);",(name, sex, age, height))
                self.conn.commit()
                self.cur.execute("SELECT * FROM pacients_id_seq;")
                row = self.cur.fetchall()
                ID = row[0][0]
                self.pacient = {'Nome': name, 'ID': ID, 'Sexo': sex, 'Idade': age, 'Altura': height}
            else:
                self.cur.execute("UPDATE pacients SET sex = (%s), age = (%s), height = (%s), name = (%s) WHERE id = (%s);", (sex, age, height, name, self.pacient['ID']))
                self.conn.commit()
                self.pacient['Nome'] = name
                self.pacient['Sexo'] = sex
                self.pacient['Idade'] = age
                self.pacient['Altura'] = height
            print("Paciente salvo")
            self.changepacientbutton.set_sensitive(True)
            self.is_pacient = True

    def on_changepacientbutton_clicked(self, widget):
        self.modifying = True
        self.savepacient_button.set_sensitive(True)
        self.name_entry.set_sensitive(True)
        self.sex_combobox.set_sensitive(True)
        self.age_entry.set_sensitive(True)
        self.height_entry.set_sensitive(True)
        self.changepacientbutton.set_sensitive(False)

    def on_capture_button_clicked(self, widget):
        if(not self.is_pacient):
            self.message_dialog_window.format_secondary_text("É preciso cadastrar ou carregar um paciente para realizar o processo de captura.")
            self.message_dialog_window.show()
        elif(not self.is_connected):
            self.message_dialog_window.format_secondary_text("É preciso conectar a um dispositivo para realizar o processo de captura.")
            self.message_dialog_window.show()
        else:
            self.progressbar.set_fraction(0)
            self.stand_up_window.show()

    def on_start_capture_button_clicked(self, widget):
        self.stand_up_window.hide()

        self.clear_charts()

        self.amostra = 768
        self.MLs = np.zeros(self.amostra)
        self.APs = np.zeros(self.amostra)
        peso = 0.0

        dt = 0.040
        tTotal = self.amostra * dt
        tempo = np.arange(0, tTotal, dt)
        t1 = ptime.time() + dt
        #print(self.amostra)
        #print(type(self.amostra))

        for i in range(self.amostra):

            while(Gtk.events_pending()):
                Gtk.main_iteration()
                self.progressbar.set_fraction(i/self.amostra)

            readings = wbb.captura1(self.wiimote)

            peso += wbb.calcWeight(readings, self.WBB['Calibração'], wbb.escala_eu)

            CoP_x, CoP_y =  wbb.calCoP(readings, self.WBB['Calibração'], wbb.escala_eu)

            self.MLs[i] = CoP_x
            self.APs[i] = CoP_y

            while (ptime.time() < t1):
                pass

            t1 += dt

        peso = peso / self.amostra
        altura = float(self.pacient['Altura'])/100.
        imc = peso / altura**2

        self.points_entry.set_text(str(self.amostra))

        self.pacient['Peso'] = round(peso, 2)
        self.pacient['IMC'] = round(imc ,1)

        self.weight.set_text(str(peso))
        self.weight.set_max_length(6)
        self.imc.set_text(str(imc))
        self.imc.set_max_length(5)
        self.save_exam_button.set_sensitive(True)

        metricas = [dis_mediaAP, dis_mediaML, dis_media, dis_rms_AP, dis_rms_ML, dis_rms_total, totex_AP, totex_ML, totex_total, mvelo_AP, mvelo_ML, mvelo_total]

        for x in range(1, 2):
            for y in range(1, 13):
                self.grid1.get_child_at(x, y).set_text(str(round(metricas[y-1], 6)))

        '''
        self.entry_Mdist_TOTAL_OA.set_text(str(dis_media))
        self.entry_Mdist_AP_OA.set_text(str(dis_mediaAP))
        self.entry_Mdist_ML_OA.set_text(str(dis_mediaML))

        self.entry_Rdist_TOTAL_OA.set_text(str(dis_rms_total))
        self.entry_Rdist_AP_OA.set_text(str(dis_rms_AP))
        self.entry_Rdist_ML_OA.set_text(str(dis_rms_ML))

        self.entry_TOTEX_TOTAL_OA.set_text(str(totex_total))
        self.entry_TOTEX_AP_OA.set_text(str(totex_AP))
        self.entry_TOTEX_ML_OA.set_text(str(totex_ML))

        self.entry_MVELO_TOTAL_OA.set_text(str(mvelo_total))
        self.entry_MVELO_AP_OA.set_text(str(mvelo_AP))
        self.entry_MVELO_ML_OA.set_text(str(mvelo_ML))
        '''

        #max_absoluto_AP = calc.valorAbsoluto(min(APs_Processado), max(APs_Processado))
        #max_absoluto_ML = calc.valorAbsoluto(min(MLs_Processado), max(MLs_Processado))

        self.axis_0_OA.set_xlim(-max_absoluto_ML, max_absoluto_ML)
        self.axis_0_OA.set_ylim(-max_absoluto_AP, max_absoluto_AP)
        self.axis_0_OA.plot(MLs_Processado, APs_Processado,'.-',color='r')
        self.canvas_0_OA.draw()

        #h1 = max_absoluto_AP*800 // max_absoluto_ML

        #self.box_0_OA.set_size_request(800, h1)

        '''
        charts = [self.box_0_OA, self.box_0_OF, self.box_1_OA, self.box_1_OF]
        for c in charts:
            #w1 = c.get_allocation().width
        '''

        self.maximo = max([max_absoluto_AP, max_absoluto_ML, max(dis_resultante_total)])

        self.axis_1_OA.set_ylim(-self.maximo, self.maximo)
        self.axis_1_OA.plot(tempo, APs_Processado, color='k', label='APs')
        self.axis_1_OA.plot(tempo, MLs_Processado, color='m', label='MLs')
        self.axis_1_OA.plot(tempo, dis_resultante_total, color='g', label='DRT')
        self.axis_1_OA.legend()
        self.canvas_1_OA.draw()

        self.save_exam_button.set_sensitive(True)

    def on_save_exam_button_clicked(self, widget):
        self.cur.execute("INSERT INTO exams (APs, MLs, pac_id, usr_id) VALUES (%s, %s, %s, %s)", (list(self.APs), list(self.MLs), self.pacient['ID'], self.user_ID))
        #self.cur.execute("UPDATE pacients SET weight = %f, imc = %f WHERE id = %d;" % (float(self.pacient['Peso']), float(self.pacient['IMC']), int(self.pacient['ID'])))
        self.conn.commit()

        self.combo_box_set_exam.remove_all()
        #Fills the exams_combobox with the dates of current pacient exams
        self.cur.execute("SELECT * FROM exams WHERE pac_id = (%s)", (self.pacient['ID']))
        rows = self.cur.fetchall()
        i=1
        for row in rows:
            self.combo_box_set_exam.append(str(row[0]), str(i) + ' - ' + str(row[3]))
            i+=1

        self.combo_box_set_exam.set_active_id("0")
        self.combo_box_set_exam.set_sensitive(True)
        self.load_exam_button.set_sensitive(True)
        self.save_exam_button.set_sensitive(False)

    def clear_charts(self):
        dt = 0.040
        tTotal = len(self.APs) * dt

        charts_estatocinesigrama = [self.axis_0_OA, self.axis_0_OF]
        charts_estabilograma = [self.axis_1_OA, self.axis_1_OF]

        for a in charts_estatocinesigrama:
            a.clear()
            a.set_ylabel('Anteroposterior (AP) mm')
            a.set_xlabel('Mediolateral (ML) mm')
            #a.set_xlim(-433/2, 433/2)
            #a.set_ylim(-238/2, 238/2)
            a.set_xlim(-1, 1)
            a.set_ylim(-1, 1)
            a.axhline(0, color='grey')
            a.axvline(0, color='grey')

        for a in charts_estabilograma:
            a.clear()
            a.set_xlim(0, tTotal)
            a.set_ylabel('Amplitude')
            a.set_xlabel('Tempo (s)')

    def verify_bt(self):
        if(self.wiimote):
            try:
                self.wiimote.request_status()
                self.battery = self.wiimote.state['battery']/BATTERY_MAX
                self.battery_label.set_text("Bateria: "+ str(int(100*self.battery))+"%")
            except RuntimeError:
                self.is_connected = False
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
        w1 = 600
        charts = [self.box_0_OA, self.box_0_OF, self.box_1_OA, self.box_1_OF]
        for c in charts:
            c.set_size_request(w1, w1)

    def on_view_changed(self, widget):
        (model, iter) = widget.get_selected()
        tv = widget.get_tree_view()

        if(tv == self.view_0):
            b = self.chart_button_0

        b.set_sensitive(False)
        self.exam = None
        if(model[iter][0][0].isdigit()):
            b.set_sensitive(True)
            d = '\'' + str(model[iter][0]) + '\''
            self.cur.execute("SELECT aps, mls, type FROM exams WHERE date::time = %s" % (d))
            self.exam = self.cur.fetchall()

    def on_load_chart(self, widget):
        if(widget == self.chart_button_0):
            a, c, x = self.axis_0_OA, self.canvas_0_OA, 1
        if(self.exam):
            self.APs = np.zeros_like(self.exam[0][0])
            self.MLs = np.zeros_like(self.exam[0][1])

            for i in range(len(self.APs)):
                self.APs[i] = self.exam[0][0][i]
                self.MLs[i] = self.exam[0][1][i]

            self.t = self.exam[0][2]

            dt = 0.040
            tTotal = len(self.APs) * dt
            tempo = np.arange(0, tTotal, dt)

            APs_Processado, MLs_Processado, AP_, ML_ = calc.geraAP_ML(self.APs, self.MLs)
            #print("AP_ = ", AP_)
            #print("ML_ = ", ML_)
            #RD
            dis_resultante_total = calc.distanciaResultante(APs_Processado, MLs_Processado)

            #? Isto não faz sentido
            dis_resultante_AP = calc.distanciaResultanteParcial(APs_Processado)
            dis_resultante_ML = calc.distanciaResultanteParcial(MLs_Processado)

            #MDIST
            dis_media = calc.distanciaMedia(dis_resultante_total)

            #MDIST_AP
            dis_mediaAP = calc.distanciaMedia_(APs_Processado)
            #MDIST_ML
            dis_mediaML = calc.distanciaMedia_(MLs_Processado)

            #print("MDIST = ", dis_media)
            #print("MDIST_AP = ", dis_mediaAP)
            #print("MDIST_ML = ", dis_mediaML)

            #RDIST
            dis_rms_total = calc.distRMS(dis_resultante_total)
            #dis_rms_AP = calc.distRMS(dis_resultante_AP)
            #dis_rms_ML = calc.distRMS(dis_resultante_ML)
            #RDIST_AP
            dis_rms_AP = calc.distRMS(APs_Processado)
            #RDIST_AP
            dis_rms_ML = calc.distRMS(MLs_Processado)

            #print("RDIST = ", dis_rms_total)
            #print("RDIST_AP = ", dis_rms_AP)
            #print("RDIST_ML = ", dis_rms_ML)

            #totex_total = calc.totex(APs_Processado, MLs_Processado)
            #TOTEX
            totex_total = calc.totex(APs_Processado, MLs_Processado)
            #TOTEX_AP
            totex_AP = calc.totexParcial(APs_Processado)
            #TOTEX_ML
            totex_ML = calc.totexParcial(MLs_Processado)

            #print("TOTEX = ", totex_total)
            #print("TOTEX_AP = ", totex_AP)
            #print("TOTEX_ML = ", totex_ML)

            #MVELO
            mvelo_total = calc.mVelo(totex_total, tTotal)
            #MVELO_AP
            mvelo_AP = calc.mVelo(totex_AP, tTotal)
            #MVELO_ML
            mvelo_ML =  calc.mVelo(totex_ML, tTotal)

            #print("MVELO = ", mvelo_total)
            #print("MVELO_AP = ", mvelo_AP)
            #print("MVELO_ML = ", mvelo_ML)

            max_absoluto_AP = np.absolute(APs_Processado).max()
            max_absoluto_ML = np.absolute(MLs_Processado).max()


            max_absoluto_AP *=1.05
            max_absoluto_ML *=1.05

            max_absoluto = max(max_absoluto_AP, max_absoluto_ML)

            metricas = [dis_mediaAP, dis_mediaML, dis_media, dis_rms_AP, dis_rms_ML, dis_rms_total, totex_AP, totex_ML, totex_total, mvelo_AP, mvelo_ML, mvelo_total]

            for y in range(1, 13):
                self.grid1.get_child_at(x, y).set_text(str(round(metricas[y-1], 6)))

            a.set_xlim(-max_absoluto, max_absoluto)
            a.set_ylim(-max_absoluto, max_absoluto)
            a.plot(MLs_Processado, APs_Processado,'.-',color='r')
            c.draw()

    def __init__(self):
        self.conn, self.cur = bd.open_BD("iem_wbb", "localhost", "postgres", "postgres")

        '''
        #Connecting to DB
        self.conn = psycopg2.connect("dbname=iem_wbb host=localhost user=postgres password=postgres")
        #Opening DB cursor
        self.cur = self.conn.cursor()
        '''

        self.date_0 = ""

        self.exam_type = ['OA', 'OF']
        self.amostra = 768
        self.balance_CoP_x = np.zeros(self.amostra)
        self.balance_CoP_y = np.zeros(self.amostra)
        self.APs = np.zeros(self.amostra)
        self.MLs = np.zeros(self.amostra)
        self.WBB = {}

        self.user_ID = None
        self.exam_date = None
        self.battery = None
        self.child = None
        self.parent = None
        self.nt = None
        self.wiimote = None
        self.is_pacient = False
        self.is_exam = False
        self.is_connected = False
        self.modifying = False

        self.pacient = {}

        #Builders
        self.iemGladeFile = "./src/iem-wbb.glade"
        self.iemBuilder = Gtk.Builder()
        self.iemBuilder.add_from_file(self.iemGladeFile)
        self.iemBuilder.connect_signals(self)

        self.commonGladeFile = "./src/common.glade"
        self.commonBuilder = Gtk.Builder()
        self.commonBuilder.add_from_file(self.commonGladeFile)
        self.commonBuilder.connect_signals(self)

        #Windows
        self.login_window = self.iemBuilder.get_object("login_window")
        self.login_window.set_icon_from_file('./media/balance.ico')
        self.register_window = self.iemBuilder.get_object("register_window")
        self.main_window = self.iemBuilder.get_object("main_window")
        self.stand_up_window = self.iemBuilder.get_object("stand_up_window")
        self.load_pacient_window = self.iemBuilder.get_object("load_pacient_window")
        self.advanced_graphs_window = self.iemBuilder.get_object("advanced_graphs_window")

        self.message_dialog_window = self.commonBuilder.get_object("message_dialog_window")
        self.new_device_window = self.commonBuilder.get_object("new_device_window")
        self.search_device_window = self.commonBuilder.get_object("search_device_window")
        self.saved_devices_window = self.commonBuilder.get_object("saved_devices_window")

        #Boxes
        self.boxOriginal = self.iemBuilder.get_object("boxOriginal")
        self.boxProcessado = self.iemBuilder.get_object("boxProcessado")
        self.boxFourier = self.iemBuilder.get_object("boxFourier")
        self.boxAdvanced = self.iemBuilder.get_object("boxAdvanced")
        self.box0 = self.iemBuilder.get_object("box0")
        self.box1 = self.iemBuilder.get_object("box1")
        self.box2 = self.iemBuilder.get_object("box2")
        self.box3 = self.iemBuilder.get_object("box3")
        

        #Images
        self.login_image = self.iemBuilder.get_object("login_image")
        self.login_image.set_from_file('./media/cadeado.png')
        self.image_in_saved = self.commonBuilder.get_object("image_in_saved")
        self.image_in_saved.set_from_file('./media/syncButton.png')
        self.search_image = self.commonBuilder.get_object("search_image")
        self.search_image.set_from_file('./media/syncButton.png')
        self.pacient_image = self.iemBuilder.get_object("pacient_image")
        self.pacient_image.set_from_file('./media/paciente.png')

        #Buttons
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
        self.chart_button_0 = Gtk.Button("Carregar")
        self.chart_button_0.set_sensitive(False)

        #Entrys
        self.name_entry = self.iemBuilder.get_object("name_entry")
        self.age_entry = self.iemBuilder.get_object("age_entry")
        self.height_entry = self.iemBuilder.get_object("height_entry")
        self.weight = self.iemBuilder.get_object("weight")
        self.imc = self.iemBuilder.get_object("imc")
        self.entry_Mdist_TOTAL_OA = self.iemBuilder.get_object("mdist_t_oa")
        self.entry_Mdist_AP_OA = self.iemBuilder.get_object("mdist_ap_oa")
        self.entry_Mdist_ML_OA = self.iemBuilder.get_object("mdist_ml_oa")
        self.entry_Rdist_AP_OA = self.iemBuilder.get_object("rdist_ap_oa")
        self.entry_Rdist_ML_OA = self.iemBuilder.get_object("rdist_ml_oa")
        self.entry_Rdist_TOTAL_OA = self.iemBuilder.get_object("rdist_t_oa")
        self.entry_TOTEX_AP_OA = self.iemBuilder.get_object("totex_ap_oa")
        self.entry_TOTEX_ML_OA = self.iemBuilder.get_object("totex_ml_oa")
        self.entry_TOTEX_TOTAL_OA = self.iemBuilder.get_object("totex_t_oa")
        self.entry_MVELO_AP_OA = self.iemBuilder.get_object("mvelo_ap_oa")
        self.entry_MVELO_ML_OA = self.iemBuilder.get_object("mvelo_ml_oa")
        self.entry_MVELO_TOTAL_OA = self.iemBuilder.get_object("mvelo_t_oa")
        self.points_entry = self.iemBuilder.get_object("points_entry")

        self.username_entry_in_login = self.iemBuilder.get_object("username_entry_in_login")
        self.password_entry_in_login = self.iemBuilder.get_object("password_entry_in_login")
        self.password_entry_in_login.set_activates_default(True)
        self.device_name_in_new = self.commonBuilder.get_object("device_name_in_new")
        self.device_mac_in_new = self.commonBuilder.get_object("device_mac_in_new")
        self.mac_entry_in_saved = self.commonBuilder.get_object("mac_entry_in_saved")

        #Combo-Boxes
        self.sex_combobox = self.iemBuilder.get_object("sex_combobox")
        self.combo_box_set_exam = self.iemBuilder.get_object("combo_box_set_exam")
        self.combo_box_in_saved = self.commonBuilder.get_object("combo_box_in_saved")
        self.combo_box_in_search = self.commonBuilder.get_object("combo_box_in_search")
        self.combobox_in_load_pacient = self.iemBuilder.get_object("combobox_in_load_pacient")

        #Events
        self.login_window.connect('destroy', Gtk.main_quit)
        self.register_window.connect("delete-event", self.close_register_window)
        self.search_device_window.connect("delete-event", self.main_window_delete_event)
        self.new_device_window.connect("delete-event", self.main_window_delete_event)
        self.stand_up_window.connect("delete-event", self.main_window_delete_event)
        self.saved_devices_window.connect("delete-event", self.main_window_delete_event)
        self.load_pacient_window.connect("delete-event", self.main_window_delete_event)
        self.advanced_graphs_window.connect("delete-event", self.close_advanced_graphs_window)

        #Spinners
        self.spinner_in_search = self.commonBuilder.get_object("spinner_in_search")

        #Labels
        self.pacient_label_in_load = self.iemBuilder.get_object("pacient_label_in_load")

        #Charts
        #self.fig = plt.figure(dpi=50)
        self.fig = plt.figure()
        #self.fig.suptitle("Olhos Abertos", fontsize=20)
        #self.fig.suptitle("Olhos Abertos")
        self.axis_0_OA = self.fig.add_subplot(111)
        #self.fig2 = plt.figure(dpi=50)
        self.fig2 = plt.figure()
        #self.fig2.suptitle("Olhos Fechados", fontsize=20)
        #self.fig2.suptitle("Olhos Fechados")
        self.axis_0_OF = self.fig2.add_subplot(111)

        #self.fig3 = plt.figure(dpi=50)
        #self.fig3.suptitle("Amplitude - Olhos Abertos", fontsize=20)
        self.fig3 = plt.figure()
        #self.fig3.suptitle("Amplitude - Olhos Abertos")
        self.axis_1_OA = self.fig3.add_subplot(111)
        #self.fig5 = plt.figure(dpi=50)
        #self.fig5.suptitle("Amplitude - Olhos Fechados", fontsize=20)
        self.fig5 = plt.figure()
        #self.fig5.suptitle("Amplitude - Olhos Fechados")
        self.axis_1_OF = self.fig5.add_subplot(111)

        self.clear_charts()

        self.canvas_0_OA = FigureCanvas(self.fig)
        self.box_0_OA = Gtk.Box()
        #self.box_0_OA = self.iemBuilder.get_object('box_0_OA')
        self.box_0_OA.pack_start(self.canvas_0_OA, expand=True, fill=True, padding=0)
        self.canvas_0_OF = FigureCanvas(self.fig2)
        self.box_0_OF = Gtk.Box()
        #self.box_0_OF = self.iemBuilder.get_object('box_0_OF')
        self.box_0_OF.pack_start(self.canvas_0_OF, expand=True, fill=True, padding=0)
        self.canvas_1_OA = FigureCanvas(self.fig3)
        self.box_1_OA = Gtk.Box()
        #self.box_1_OA = self.iemBuilder.get_object('box_1_OA')
        self.box_1_OA.pack_start(self.canvas_1_OA, expand=True, fill=True, padding=0)
        self.canvas_1_OF = FigureCanvas(self.fig5)
        self.box_1_OF = Gtk.Box()
        #self.box_1_OF = self.iemBuilder.get_object('box_1_OF')
        self.box_1_OF.pack_start(self.canvas_1_OF, expand=True, fill=True, padding=0)

        boxes = [self.box_0_OA, self.box_0_OF, self.box_1_OA, self.box_1_OF]
        for b in boxes:
            b.connect('button-press-event', self.on_button_press_event)

        #Grid 
        self.grid1 = self.iemBuilder.get_object("grid1")
        #for x in ["mdist_", "rdist_", "totex_", "mvelo_"]:
            #for y in ["ap_", "ml_", "total_"]:
        for m in range(1, 13):
            self.grid1.attach(Gtk.Entry.new(), 2, m, 1, 1)
            self.grid1.get_child_at(2, m).set_text('0.000000')
            self.grid1.get_child_at(2, m).set_editable(False)
            self.grid1.get_child_at(2, m).set_width_chars(8)

        self.clear_charts()

        #TreeViews
        store = Gtk.TreeStore(str)
        self.cur.execute("SELECT * FROM pacients;")
        p = self.cur.fetchall()
        for pac in p:
            nome = store.append(None, [pac[1]])
            self.cur.execute("SELECT date::date FROM exams WHERE pac_id = %s;" % (pac[0]))
            d = self.cur.fetchall()
            for dat in list(set(d)):
                data = store.append(nome, [str(dat[0])])
                self.cur.execute("SELECT date::time FROM exams WHERE date::date = %s and pac_id = %s;" % ('\''+str(dat[0])+'\'', pac[0]))
                h = self.cur.fetchall()
                for hr in h:
                    store.append(data, [str(hr[0])])


        # the treeview shows the model
        # create a treeview on the model store
        self.view_0 = Gtk.TreeView()
        self.view_0.set_model(store)
        self.view_0.get_selection().connect("changed", self.on_view_changed)
        # the cellrenderer for the column - text
        renderer_exams = Gtk.CellRendererText()
        # the column is created
        column_exams = Gtk.TreeViewColumn(
            "Exames por Paciente", renderer_exams, text=0)
        # and it is appended to the treeview
        self.view_0.append_column(column_exams)

        # the exams are sortable by author
        column_exams.set_sort_column_id(0)

        # add the treeview to the window
        box = Gtk.VBox()
        box.set_homogeneous(False)
        box.add(self.view_0)
        self.chart_button_0.set_valign(Gtk.Align.CENTER)
        self.chart_button_0.set_halign(Gtk.Align.BASELINE)
        self.chart_button_0.connect('clicked', self.on_load_chart)
        box.add(self.chart_button_0)
        self.box0.set_spacing(10)
        self.box0.add(box)
        self.box0.add(self.box_0_OA)

        #StatusBar
        self.status_image = self.iemBuilder.get_object("status_image")
        self.status_image.set_from_file('./media/bt_red.png')
        self.status_label = self.iemBuilder.get_object("status_label")
        self.battery_label = self.iemBuilder.get_object("battery_label")
        self.progressbar = self.iemBuilder.get_object("progressbar")

        ''' Login '''
        #self.login_window.show_all()
        self.main_window.maximize()
        self.resize(self.main_window)
        self.main_window.show_all()


if __name__ == "__main__":

    main = Iem_wbb()
    Gtk.main()