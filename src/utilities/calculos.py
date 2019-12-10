# -*- coding: utf-8 -*-

from math import sqrt
import numpy as np
from src.utilities.calculos_los import distance_points

def distanciaMedia(RD):
    # return sum(list(lista_valores)) / len(lista_valores)
    return RD.mean()


def distanciaMedia_(APouML):
    # return sum(list(lista_valores)) / len(lista_valores)
    return np.absolute(APouML).mean()


def distanciaResultante(AP, ML):
    distancia_result = np.zeros_like(AP)

    # for i in range(len(AP)):
    #    DR = sqrt((AP[i]**2)+(ML[i]**2))
    #    distancia_result.append(DR)

    distancia_result = np.sqrt(AP ** 2 + ML ** 2)
    return distancia_result


def distanciaResultanteParcial(APouML):
    distancia_resultparcial = np.zeros_like(APouML)

    # for i in range(len(APouML)):
    #    DR = sqrt(APouML[i]**2)
    #    distancia_resultparcial.append(DR)

    distancia_resultparcial = np.sqrt(APouML ** 2)
    return distancia_resultparcial


def distRMS(dist_resultante):
    # d_R_quadrada =np.zeros_like(dist_resultante)

    # for _ in range(len(dist_resultante)):
    #    dist_result_quadrada = (dist_resultante[_]**2)
    #    d_R_quadrada.append(dist_result_quadrada)

    # soma = sum(list(d_R_quadrada))
    # disRMS =sqrt(soma/len(dist_resultante))

    RMS = np.sqrt((dist_resultante ** 2).sum()) / dist_resultante.size

    return RMS


def geraAP_ML(valy, valx):
    # soma_AP0 = soma_ML0 = 0.0   #variáveis referentes ao somatorio
    valores_AP = np.zeros_like(valy)  # ndarray que receberá os valores de AP
    valores_ML = np.zeros_like(valx)  # ndarray que receberá os valores de ML

    # for ele in range(len(valy)):
    #    soma_AP0 = soma_AP0 + valx[ele]
    #    soma_ML0 = soma_ML0 + valy[ele]

    # AP_barra = soma_AP0 / len(valx)
    # ML_barra = soma_ML0 / len(valy
    # AP_barra = sum(valy) / len(valy)
    # ML_barra = sum(valx) / len(valx)
    AP_barra = valy.mean()
    ML_barra = valx.mean()
    print(f'AP_: {AP_barra}')
    print(f'ML_: {ML_barra}')
    
    valores_AP = valy - AP_barra
    valores_ML = valx - ML_barra
    # for i in range(len(valy)):
    #    ap = valx[i] - AP_barra
    #    ml = valy[i] - ML_barra
    #    valores_AP.append(ap)
    #    valores_ML.append(ml)

    return valores_AP, valores_ML, AP_barra, ML_barra


def mVelo(totex, tempo):
    velocidademedia = totex / tempo
    return velocidademedia


def totex(AP, ML):
    # dist = []
    # for i in range(len(AP)-1):
    #    distancia = sqrt((AP[i+1] - AP[i])**2 + (ML[i+1] - ML[i])**2)
    #    dist.append(distancia)
    # Totex = sum(list(dist))
    Totex_ = np.sqrt(((AP[1:] - AP[:-1]) ** 2) + ((ML[1:] - ML[:-1]) ** 2))
    Totex = Totex_.sum()
    return Totex


def totexParcial(APouML):
    # dist = []
    # for i in range(len(APouML)-1):
    #    distancia = sqrt((APouML[i+1] - APouML[i])**2)
    #    dist.append(distancia)
    # Totexparcial = sum(list(dist))
    Totexparcial = np.absolute(APouML[1:] - APouML[:-1]).sum()
    return Totexparcial


# retorna o maior valor absoluto de dois elementos
def valorAbsoluto(minimo, maximo):
    if abs(minimo) > abs(maximo):
        return abs(minimo)
    else:
        return abs(maximo)

def amplitude(aps, mls):
	a = 0.
	l = len(aps)
	for i in range(l-1):
		d = distance_points((mls[i], aps[i]), (mls[i+1], aps[i+1]))
		if d > a:
			a = d
	return a

def amplitude_parcial(ap_ou_ml):
	return ap_ou_ml.max() - ap_ou_ml.min()

def get_amplitude(aps, mls):
    APs_Processado, MLs_Processado, _, _ = geraAP_ML(aps, mls)

    # AMPLITUDE_AP
    amplitude_AP = amplitude_parcial(APs_Processado)
    # AMPLITUDE_ML
    amplitude_ML = amplitude_parcial(MLs_Processado)

    return amplitude_AP, amplitude_ML

def computes_metrics(aps, mls):
    metrics = dict()

    aps *= .1
    mls *= .1

    # Definição do intervalo entre capturas
    metrics['dt'] = 0.040
    metrics['tTotal'] = len(aps) * metrics['dt']
    metrics['tempo'] = np.arange(0, metrics['tTotal'], metrics['dt'])
    
    # Processamento do sinal
    metrics['APs_Processado'], metrics['MLs_Processado'], metrics['AP_'], metrics['ML_'] = geraAP_ML(
        aps, mls)

    # RD
    metrics['dis_resultante_total'] = distanciaResultante(metrics['APs_Processado'],
                                                          metrics['MLs_Processado'])
    # MDIST
    metrics['dis_media'] = distanciaMedia(metrics['dis_resultante_total'])
    # MDIST_AP
    metrics['dis_mediaAP'] = distanciaMedia_(metrics['APs_Processado'])
    # MDIST_ML
    metrics['dis_mediaML'] = distanciaMedia_(metrics['MLs_Processado'])

    # RDIST
    metrics['dis_rms_total'] = distRMS(metrics['dis_resultante_total'])
    # RDIST_AP
    metrics['dis_rms_AP'] = distRMS(metrics['APs_Processado'])
    # RDIST_AP
    metrics['dis_rms_ML'] = distRMS(metrics['MLs_Processado'])

    # TOTEX
    metrics['totex_total'] = totex(
        metrics['APs_Processado'], metrics['MLs_Processado'])
    # TOTEX_AP
    metrics['totex_AP'] = totexParcial(metrics['APs_Processado'])
    # TOTEX_ML
    metrics['totex_ML'] = totexParcial(metrics['MLs_Processado'])

    # MVELO
    metrics['mvelo_total'] = mVelo(metrics['totex_total'], metrics['tTotal'])
    # MVELO_AP
    metrics['mvelo_AP'] = mVelo(metrics['totex_AP'], metrics['tTotal'])
    # MVELO_ML
    metrics['mvelo_ML'] = mVelo(metrics['totex_ML'], metrics['tTotal'])

    # AMPLITUDE
    metrics['amplitude_total'] = amplitude(
        metrics['APs_Processado'], metrics['MLs_Processado'])
    # AMPLITUDE_AP
    metrics['amplitude_AP'] = amplitude_parcial(metrics['APs_Processado'])
    # AMPLITUDE_ML
    metrics['amplitude_ML'] = amplitude_parcial(metrics['MLs_Processado'])

    # Cálculo dos máximos (sinal processado)
    metrics['max_absoluto_AP'] = np.absolute(metrics['APs_Processado']).max()
    metrics['max_absoluto_ML'] = np.absolute(metrics['MLs_Processado']).max()
    metrics['max_absoluto_AP'] *= 1.05
    metrics['max_absoluto_ML'] *= 1.05
    metrics['max_absoluto'] = max(
        metrics['max_absoluto_AP'], metrics['max_absoluto_ML'])
    metrics['maximo'] = max([metrics['max_absoluto_AP'], metrics['max_absoluto_ML'], max(
        metrics['dis_resultante_total'])])

    # print(metrics)

    return metrics
