# !/usr/bin/env python3

import sys
import os
import time
import numpy as np
import bluetooth

try:
    import cwiid
except:
    print("Desculpe, não consigo importar o cwiid por algum motivo.")
    print("Por favor, verifique se ele e suas ligações python estão instaladas,")
    print("e também o patch da Wii Balance Board.")
    sys.exit(1)

escala_jp = 1700.  # Escala Japão 17 Kg * 2 = 34,0 Kg * 4 = 136 Kg
escala_eu = 1875.  # Escala EUA 18,5 Kg * 2 = 37,5 Kg * 4 = 150 Kg


def captura(wiimote, min=False, rep=100):
    duration = 1  # second
    freq = 440  # Hz
    freq_ = 220  # Hz
    # os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
    # print("Preparados!!!!!")
    # time.sleep(5)
    # print("Já!!!!!!!!!!")
    # os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq_))
    calibre = np.zeros((rep, 4))
    fat = rep / 10
    per = 0
    for i in range(rep):
        wiimote.request_status()
        readings = wiimote.state['balance']
        # weight = (calcweight(wiimote.state['balance'], named_calibration) / 100.0)
        # print(readings)
        # if (i%fat == 0):
        #    print(per, "%")
        #    per += 10
        j = 0
        for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
            calibre[i, j] = readings[sensor]
            j += 1

            time.sleep(0.05)

    # os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq_))
    # os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
    # os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq_))

    saida = np.zeros(4)
    j = 0
    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
        if min:
            saida[j] = calibre[:, j].min()
        else:
            saida[j] = calibre[:, j].mean()
        j += 1

    return saida


def saida_(calibre, min=False):
    saida = np.zeros(4)
    for j, sensor in enumerate(['right_top', 'right_bottom', 'left_top', 'left_bottom']):
        if min:
            saida[j] = calibre[:, j].min()
        else:
            saida[j] = calibre[:, j].mean()

    return saida


def captura1(wiimote):
    wiimote.request_status()
    readings = wiimote.state['balance']

    return readings


def search():
    print("Start discovering....")
    nearby_devices = bluetooth.discover_devices(duration=1, lookup_names=True)

    return nearby_devices


def conecta(mac=""):
    # mac = "00:26:59:DD:0A:6F" #WBB_ESBEL
    # mac = "00:22:4C:56:D3:F4" #WBB_DEV
    # mac = "00:27:09:AC:29:22" #WBB_MARCILIO

    wiimote = cwiid.Wiimote(mac)

    wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
    wiimote.request_status()

    while wiimote.state['ext_type'] != cwiid.EXT_BALANCE:
        print('Este programa suporta apenas o Wii Balance Board')
        print("Por favor, pressione o botão vermelho 'conectar' na Wii Balance Board (WBB), dentro do compartimento da bateria.")
        print("Não pise na WBB.")
        wiimote.close()
        wiimote = cwiid.Wiimote(mac)
        wiimote.rpt_mode = cwiid.RPT_BALANCE | cwiid.RPT_BTN
        wiimote.request_status()

    return wiimote


def gsc(readings, pos, calibrations, escala):
    reading = readings[pos]
    calibration = calibrations[pos]
    if reading < calibration[0]:
        reading = calibration[0]
    if reading < calibration[1]:
        return escala * (reading - calibration[0]) / (calibration[1] - calibration[0])
    else:
        return escala * (reading - calibration[1]) / (calibration[2] - calibration[1]) + escala


def calcWeight(readings, calibrations, escala):
    dx = np.zeros(4)
    j = 0
    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
        dx[j] = gsc(readings, sensor, calibrations, escala)
        j += 1
    peso = dx.sum()
    return peso / 100


def calPos(readings, calibrations, escala):
    rt = 0
    rb = 1
    lt = 2
    lb = 3
    dx = np.zeros(4)
    j = 0
    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
        dx[j] = gsc(readings, sensor, calibrations, escala)
        j += 1
    x_balance = (dx[rt] + dx[rb]) / (dx[lt] + dx[lb])
    if x_balance > 1:
        x_balance = -1 * ((dx[lt] + dx[lb]) / (dx[rt] + dx[rb])) + 1
    else:
        x_balance = x_balance - 1.

    y_balance = (dx[lb] + dx[rb]) / (dx[lt] + dx[rt])
    if y_balance > 1:
        y_balance = -1 * ((dx[lt] + dx[rt]) / (dx[lb] + dx[rb])) + 1
    else:
        y_balance = y_balance - 1.

    return x_balance, y_balance


def calCoP(readings, calibrations, escala):
    rt = 0
    rb = 1
    lt = 2
    lb = 3
    X = 433  # mm
    Y = 238  # mm

    F = np.zeros(4)
    j = 0
    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
        F[j] = gsc(readings, sensor, calibrations, escala)
        j += 1

    CoP_x = (X / 2) * ((F[rt] + F[rb]) - (F[lt] + F[lb])) / F.sum()
    CoP_y = (Y / 2) * ((F[rt] + F[lt]) - (F[rb] + F[lb])) / F.sum()

    return CoP_x, CoP_y


def calCoP_(readings, calibrations, escala):
    rt = 0
    rb = 1
    lt = 2
    lb = 3
    X = 433  # mm
    Y = 238  # mm

    F = np.zeros(4)
    for j, sensor in enumerate(calibrations.keys()):
        F[j] = gsc(readings, sensor, calibrations, escala)

    CoP_x = (X / 2) * ((F[rt] + F[rb]) - (F[lt] + F[lb])) / F.sum()
    CoP_y = (Y / 2) * ((F[rt] + F[lt]) - (F[rb] + F[lb])) / F.sum()

    return CoP_x, CoP_y


def calibra_medios(wiimote, calibrations, sensor, sinal_RB, sinal_LT, sinal_LB, escala):
    print("Calibrando o sinal medio")

    readings_RT = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_RB = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_LT = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_LB = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    for i, sensor in enumerate(['right_top', 'right_bottom', 'left_top', 'left_bottom']):
        readings_RT[sensor] = sinal_RT[i]
        readings_RB[sensor] = sinal_RB[i]
        readings_LT[sensor] = sinal_LT[i]
        readings_LB[sensor] = sinal_LB[i]

    for i in range(10):
        P_res = gsc(readings_RT, 'right_bottom', calibrations, escala)
        P_res += gsc(readings_RT, 'left_top', calibrations, escala)
        P_res += gsc(readings_RT, 'left_bottom', calibrations, escala)
        cal = (escala / (1070 - P_res)) * (readings_RT['right_top'] - calibrations['right_top'][0]) + \
            calibrations['right_top'][0]
        calibrations['right_top'][1] = cal

        P_res = gsc(readings_RB, 'right_top', calibrations, escala)
        P_res += gsc(readings_RB, 'left_top', calibrations, escala)
        P_res += gsc(readings_RB, 'left_bottom', calibrations, escala)
        cal = (escala / (1070 - P_res)) * (readings_RB['right_bottom'] - calibrations['right_bottom'][0]) + \
            calibrations['right_bottom'][0]
        calibrations['right_bottom'][1] = cal

        P_res = gsc(readings_LT, 'right_top', calibrations, escala)
        P_res += gsc(readings_LT, 'right_bottom', calibrations, escala)
        P_res += gsc(readings_LT, 'left_bottom', calibrations, escala)
        cal = (escala / (1070 - P_res)) * (readings_LT['left_top'] - calibrations['left_top'][0]) + \
            calibrations['left_top'][0]
        calibrations['left_top'][1] = cal

        P_res = gsc(readings_LB, 'right_top', calibrations, escala)
        P_res += gsc(readings_LB, 'right_bottom', calibrations, escala)
        P_res += gsc(readings_LB, 'left_top', calibrations, escala)
        cal = (escala / (1070 - P_res)) * (readings_LB['left_bottom'] - calibrations['left_bottom'][0]) + \
            calibrations['left_bottom'][0]
        calibrations['left_bottom'][1] = cal

    return calibrations


def calibra_maximos(wiimote, calibrations, sinal_RT, sinal_RB, sinal_LT, sinal_LB, escala):
    print("Calibrando o sinal máximo")

    j = 0
    readings_RT = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_RB = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_LT = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_LB = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
        readings_RT[sensor] = sinal_RT[j]
        readings_RB[sensor] = sinal_RB[j]
        readings_LT[sensor] = sinal_LT[j]
        readings_LB[sensor] = sinal_LB[j]
        j += 1

    P_res = gsc(readings_RT, 'right_bottom', calibrations, escala)
    P_res += gsc(readings_RT, 'left_top', calibrations, escala)
    P_res += gsc(readings_RT, 'left_bottom', calibrations, escala)
    P_res = 3070 - P_res - escala
    cal = (escala / P_res) * (readings_RT['right_top'] -
                              calibrations['right_top'][1]) + calibrations['right_top'][1]
    calibrations['right_top'][2] = cal

    P_res = gsc(readings_RB, 'right_top', calibrations, escala)
    P_res += gsc(readings_RB, 'left_top', calibrations, escala)
    P_res += gsc(readings_RB, 'left_bottom', calibrations, escala)
    P_res = 3070 - P_res - escala
    cal = (escala / P_res) * (readings_RB['right_bottom'] - calibrations['right_bottom'][1]) + \
        calibrations['right_bottom'][1]
    calibrations['right_bottom'][2] = cal

    P_res = gsc(readings_LT, 'right_top', calibrations, escala)
    P_res += gsc(readings_LT, 'right_bottom', calibrations, escala)
    P_res += gsc(readings_LT, 'left_bottom', calibrations, escala)
    P_res = 3070 - P_res - escala
    cal = (escala / P_res) * (readings_LT['left_top'] -
                              calibrations['left_top'][1]) + calibrations['left_top'][1]
    calibrations['left_top'][2] = cal

    P_res = gsc(readings_LB, 'right_top', calibrations, escala)
    P_res += gsc(readings_LB, 'right_bottom', calibrations, escala)
    P_res += gsc(readings_LB, 'left_top', calibrations, escala)
    P_res = 3070 - P_res - escala
    cal = (escala / P_res) * (readings_LB['left_bottom'] - calibrations['left_bottom'][1]) + \
        calibrations['left_bottom'][1]
    calibrations['left_bottom'][2] = cal

    return calibrations


def p_res(readings, sensor, calibrations, escala, peso, signal, max=False):
    res_weight = 0.
    sensors = ['right_top', 'right_bottom', 'left_top', 'left_bottom']
    sensors.remove(sensor)
    for s in sensors:
        res_weight += gsc(readings, s, calibrations, escala)
    if max:
        res_weight = peso - res_weight - escala
        cal = (escala / res_weight) * \
            (readings[sensor] - calibrations[sensor]
             [signal-1]) + calibrations[sensor][signal-1]
    else:
        cal = (escala / (peso - res_weight)) * \
            (readings[sensor] - calibrations[sensor]
             [signal-1]) + calibrations[sensor][signal-1]
    calibrations[sensor][signal] = cal


def main():
    rt = 0
    rb = 1
    lt = 2
    lb = 3

    wiimote = conecta()
    # Descobrir aqui uma forma de determinar qual a escala correta
    escala = escala_eu

    print("Calibrando o sinal mínimo")
    Minimos = captura(wiimote, True, 1000)
    # Minimos = np.array([2319., 3015., 4156., 4041.])
    # Minimos = np.array([2201., 2944., 4120.,  3914.])
    # Minimos = np.array([2302., 3003., 4161., 4023.])
    # Minimos = np.array([2201., 2944., 4120., 3914.])
    print("Minimos = ", Minimos)

    Medio = Minimos + escala
    Maximos = Medio + escala
    j = 0
    calibrations = {'right_top': 0, 'right_bottom': 0,
                    'left_top': 0, 'left_bottom': 0}
    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
        calibrations[sensor] = [Minimos[j], Medio[j], Maximos[j]]
        j += 1

    print("Calibrando o sinal medio")
    # Medio = np.array([3965., 4745., 5863., 5848.])

    print("RT")
    time.sleep(20)
    sinal_RT = captura(wiimote)
    # sinal_RT = np.array([3388.23, 3035.06, 4184.83, 4016.36])
    print("sinal_RT = ", sinal_RT)

    print("RB")
    time.sleep(20)
    sinal_RB = captura(wiimote)
    # sinal_RB = np.array([2362.15, 4060.83, 4145.24, 4056.61])
    print("sinal_RB = ", sinal_RB)

    print("LT")
    time.sleep(20)
    sinal_LT = captura(wiimote)
    # sinal_LT = np.array([2331.42, 2995.78, 5245.8,  4048.16])
    print("sinal_LT = ", sinal_LT)

    print("LB")
    time.sleep(20)
    sinal_LB = captura(wiimote)
    # sinal_LB = np.array([2293.68, 3059.89, 4183.14, 5133.24])
    print("sinal_LB = ", sinal_LB)

    j = 0
    readings_RT = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_RB = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_LT = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_LB = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
        readings_RT[sensor] = sinal_RT[j]
        readings_RB[sensor] = sinal_RB[j]
        readings_LT[sensor] = sinal_LT[j]
        readings_LB[sensor] = sinal_LB[j]
        j += 1

    for i in range(10):
        P_res = gsc(readings_RT, 'right_bottom', calibrations, escala)
        P_res += gsc(readings_RT, 'left_top', calibrations, escala)
        P_res += gsc(readings_RT, 'left_bottom', calibrations, escala)
        cal = (escala / (1070 - P_res)) * (readings_RT['right_top'] - calibrations['right_top'][0]) + \
            calibrations['right_top'][0]
        calibrations['right_top'][1] = cal

        P_res = gsc(readings_RB, 'right_top', calibrations, escala)
        P_res += gsc(readings_RB, 'left_top', calibrations, escala)
        P_res += gsc(readings_RB, 'left_bottom', calibrations, escala)
        cal = (escala / (1070 - P_res)) * (readings_RB['right_bottom'] - calibrations['right_bottom'][0]) + \
            calibrations['right_bottom'][0]
        calibrations['right_bottom'][1] = cal

        P_res = gsc(readings_LT, 'right_top', calibrations, escala)
        P_res += gsc(readings_LT, 'right_bottom', calibrations, escala)
        P_res += gsc(readings_LT, 'left_bottom', calibrations, escala)
        cal = (escala / (1070 - P_res)) * (readings_LT['left_top'] - calibrations['left_top'][0]) + \
            calibrations['left_top'][0]
        calibrations['left_top'][1] = cal

        P_res = gsc(readings_LB, 'right_top', calibrations, escala)
        P_res += gsc(readings_LB, 'right_bottom', calibrations, escala)
        P_res += gsc(readings_LB, 'left_top', calibrations, escala)
        cal = (escala / (1070 - P_res)) * (readings_LB['left_bottom'] - calibrations['left_bottom'][0]) + \
            calibrations['left_bottom'][0]
        calibrations['left_bottom'][1] = cal

        # print("Calibração :", calibrations)

    print("Calibração :", calibrations)

    print("Calibrando o sinal máximo")

    print("RT")
    time.sleep(20)
    sinal_RT = captura(wiimote)
    # sinal_RT = np.array([5370.93, 3033.08, 4220.24, 4027.63])
    # sinal_RT = np.array([5393.19, 3023.4,  4233.15, 3998.45])
    print("sinal_RT = ", sinal_RT)

    print("RB")
    time.sleep(20)
    sinal_RB = captura(wiimote)
    # sinal_RB = np.array([2381.56, 6109.33, 4141.01, 4060.05])
    # sinal_RB = np.array([2304.46, 6173.28, 4156.4,  4068.94])
    print("sinal_RB = ", sinal_RB)

    print("LT")
    time.sleep(20)
    sinal_LT = captura(wiimote)
    # sinal_LT = np.array([2348.89, 3005.74, 7301.5,  3993.06])
    print("sinal_LT = ", sinal_LT)

    print("LB")
    time.sleep(20)
    sinal_LB = captura(wiimote)
    # sinal_LB = np.array([2286.32, 3093.6,  4184.3,  7243.8 ])
    # sinal_LB = np.array([2275.19, 3081.05, 4229.82, 7234.94])
    print("sinal_LB = ", sinal_LB)

    j = 0
    readings_RT = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_RB = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_LT = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    readings_LB = {'right_top': 0, 'right_bottom': 0,
                   'left_top': 0, 'left_bottom': 0}
    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
        readings_RT[sensor] = sinal_RT[j]
        readings_RB[sensor] = sinal_RB[j]
        readings_LT[sensor] = sinal_LT[j]
        readings_LB[sensor] = sinal_LB[j]
        j += 1

    P_res = gsc(readings_RT, 'right_bottom', calibrations, escala)
    P_res += gsc(readings_RT, 'left_top', calibrations, escala)
    P_res += gsc(readings_RT, 'left_bottom', calibrations, escala)
    P_res = 3070 - P_res - escala
    cal = (escala / P_res) * (readings_RT['right_top'] -
                              calibrations['right_top'][1]) + calibrations['right_top'][1]
    calibrations['right_top'][2] = cal

    P_res = gsc(readings_RB, 'right_top', calibrations, escala)
    P_res += gsc(readings_RB, 'left_top', calibrations, escala)
    P_res += gsc(readings_RB, 'left_bottom', calibrations, escala)
    P_res = 3070 - P_res - escala
    cal = (escala / P_res) * (readings_RB['right_bottom'] - calibrations['right_bottom'][1]) + \
        calibrations['right_bottom'][1]
    calibrations['right_bottom'][2] = cal

    P_res = gsc(readings_LT, 'right_top', calibrations, escala)
    P_res += gsc(readings_LT, 'right_bottom', calibrations, escala)
    P_res += gsc(readings_LT, 'left_bottom', calibrations, escala)
    P_res = 3070 - P_res - escala
    cal = (escala / P_res) * (readings_LT['left_top'] -
                              calibrations['left_top'][1]) + calibrations['left_top'][1]
    calibrations['left_top'][2] = cal

    P_res = gsc(readings_LB, 'right_top', calibrations, escala)
    P_res += gsc(readings_LB, 'right_bottom', calibrations, escala)
    P_res += gsc(readings_LB, 'left_top', calibrations, escala)
    P_res = 3070 - P_res - escala
    cal = (escala / P_res) * (readings_LB['left_bottom'] - calibrations['left_bottom'][1]) + \
        calibrations['left_bottom'][1]
    calibrations['left_bottom'][2] = cal

    print("Calibração :", calibrations)

    print("Testando com alguem")
    time.sleep(10)
    sinal = captura(wiimote, False, 10)
    dx = np.zeros(4)
    j = 0
    readings = {'right_top': 0, 'right_bottom': 0,
                'left_top': 0, 'left_bottom': 0}
    for sensor in ('right_top', 'right_bottom', 'left_top', 'left_bottom'):
        readings[sensor] = sinal[j]
        dx[j] = gsc(readings, sensor, calibrations, escala)
        j += 1

    peso = dx.sum()
    print("Peso = ", peso / 100)

    wiimote.close()
    return


if __name__ == "__main__":
    main()
