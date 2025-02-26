import geopandas as gpd
import pandas as pd
import numpy as np


# load data from BDOT_analiza_zabudowa.gdb
# /home/ard/prg/topo/venv/lib64/python3.11/site-packages/pyogrio/geopandas.py:265: UserWarning: More than one layer found in 'BDOT_analiza_zabudowa.gdb': 'L4_1_BDOT10k__OT_SWRS_L' (default), 'L4_1_BDOT10k__OT_SWRM_L', 'L4_1_BDOT10k__OT_SUPR_L', 'L4_1_BDOT10k__OT_SULN_L', 'L4_1_BDOT10k__OT_SKTR_L', 'L4_1_BDOT10k__OT_SKRW_P', 'L4_1_BDOT10k__OT_SKDR_L', 'L4_1_BDOT10k__OT_PTZB_A', 'L4_1_BDOT10k__OT_PTWP_A', 'L4_1_BDOT10k__OT_PTUT_A', 'L4_1_BDOT10k__OT_PTTR_A', 'L4_1_BDOT10k__OT_PTRK_A', 'L4_1_BDOT10k__OT_PTPL_A', 'L4_1_BDOT10k__OT_PTNZ_A', 'L4_1_BDOT10k__OT_PTLZ_A', 'L4_1_BDOT10k__OT_PTKM_A', 'L4_1_BDOT10k__OT_PTGN_A', 'L4_1_BDOT10k__OT_ADMS_A', 'L4_1_BDOT10k__OT_BUWT_P'. Specify layer parameter to avoid this warning.
# select adms_a layer
layer = "L4_1_BDOT10k__OT_ADMS_A"
file_name = "BDOT_analiza_zabudowa.gdb"
district_data = gpd.read_file(file_name, layer=layer)

district_name = 'Koniuchy'

# select row with nazwa = 'Koniuchy'
district = district_data[district_data['nazwa'] == district_name]

# 1) area
area = district['Shape_Area']
print(f"Powierzchnia zabudowy mieszkaniowej w {district_name} to {area.sum():.2f} m²")

# 2) 
# skdr
roads_name = 'L4_1_BDOT10k__OT_SKDR_L'

road_data = gpd.read_file(file_name, layer=roads_name)


# clip roads to district
roads = gpd.clip(road_data, district)
roads = roads[roads['katZarzadz'].isin(['P', 'G'])]
length_sum = roads['Shape_Length'].sum()
district_area = district['Shape_Area'].sum()
road_density = length_sum / district_area * 1000
print(f'Gęstość dróg gminnych i powiatowych: {road_density:.3f} m/km²')

# 3)
teren_upraw_trwalych_name = 'L4_1_BDOT10k__OT_PTUT_A'
ptut_layer = gpd.read_file(file_name, layer=teren_upraw_trwalych_name)
wody_powierzchniowe_name = 'L4_1_BDOT10k__OT_PTWP_A'
ptwp_layer = gpd.read_file(file_name, layer=wody_powierzchniowe_name)
obszary_trawiaste_name = 'L4_1_BDOT10k__OT_PTTR_A'
pttr_layer = gpd.read_file(file_name, layer=wody_powierzchniowe_name)

objects = [ptut_layer, ptwp_layer, pttr_layer]

wysokie_budowle_techniczne_name = 'L4_1_BDOT10k__OT_BUWT_P'
buwt_layer = gpd.read_file(file_name, layer=wysokie_budowle_techniczne_name)
# select all with idIIP_BT_I = 'PL.PZGIK.BDOT10k.BUWTP.04.6312'
buwt_layer = buwt_layer[buwt_layer['idIIP_BT_I'] == 'PL.PZGIK.BDOT10k.BUWTP.04.6312']

# create 2 buffers
small_buffer = buwt_layer.buffer(800)
large_buffer = buwt_layer.buffer(1800)
diff_geoms = large_buffer.difference(small_buffer)
# create a geodataframe with the differences
diff_df = gpd.GeoDataFrame(geometry=diff_geoms)
# save to diffs.gpkg
diff_df.to_file('diffs.gpkg')
area_sum = 0
for layer in objects:
    layer = gpd.clip(layer, diff_df)
    area_sum += layer.geometry.area.sum()

print(f'Powierzchnia terenów upraw trwałych, wód powierzchniowych oraz obszarów trawiastych w promieniu 0,8 oraz 1,8 km od wybranej wysokiej budowli technicznej: {area_sum:.2f} m²')

# cli


# BDT_PROJEKT_1 Poznanie struktury BDOT i analiza danych.␍
# ␍
# Baza ród³owa: BDOT_analiza_zabudowa.gdb␍
# Dokumentacja BDOT10k w pliku pdf - struktura bazy i klasyfikacja str. 197.␍
# ␍
# Termin oddania sprawozdania: Zaj.nr 2␍
# ␍
# Wynikiem zadania ma byæ odpowied na 3 pytania sformu³owane poni¿ej, zawarta w sprawozdzaniu krótko opisuj¹cym tak¿e sposób uzyskania wyników [kolejne kroki wykonywane w analizach]␍
# Æwiczenie realizujemy w aplikacji ArcGIS.␍
# Wybieramy dowoln¹ dzielnicê, ale tak¹, która zawiera zabudowê [PTZB] i drogi gminne [z klasy SKDR]␍
# ␍
# +) zapytanie A: jaka jest powierzchnia zabudowy mieszkaniowej w wybranej dzielnicy Torunia? ␍
# +) zapytanie B: jaka jest gêstoc dróg gminnych i powiatowych w tej dzielnicy Torunia?␍
# +) zapytanie C: jaka jest powierzchnia terenów upraw trwa³ych, wód powierzchnowych oraz obszarów trawiastych w promieniu 0,8 oraz 1,8 km od wybranej wysokiej budowli technicznej?␍
# ␍
# + HELP: http://desktop.arcgis.com/en/arcmap/10.3/map/working-with-layers/using-select-by-location.htm␍
# ␍
# UWAGI:␍
# - w zapyt.A chodzi wy³¹cznie o zabudowê mieszkaniow¹ [trzeba wybraæ dane z klasy PTZB_A zapytaniem opartym na s³owniku OT_RodzajZabudowy]␍
# - w zapyt. A i B chodzi o jedn¹ dzielnicê, wiêc jej obszar tak¿e nale¿y wybraæ do zapytania przestrzennego [i dzia³aæ na wybranych obiektach zbioru dzielnic miasta]␍
# zwróæmy uwagê, ¿e dzielnice wzajemnie siê nak³adaj¹, wiêc aby zobaczyæ je wszystkie na mapie nale¿y zmieniæ znak wywietlania na kontur bez wype³nienia [widoczna jest wtedy geometria odpowiadaj¹ca wszystkim 14 rekordom z tabeli]␍
# - finiszujemy zapytaniem przestrzennym [korzystaj¹c z helpa dostêpnego pod ww adresem URL] i liczymy sumaryczn¹ powierzchniê wybranych obiektów klasy PTZB_A stanowi¹c¹ odpowied na pytanie [obliczenia statystyczne prowadzimy na zakoñczenie - w tabeli wyniku poprzez PKM > Statistics]␍
# - w zapyt. C klasy terenów upraw trwa³ych, wód powierzchniowych oraz obszarów trawiastych analizujemy oddzielnie,␍
# tereny upraw trwa³ych s¹ modelowane w klasie PTUT_A, wody powierzchniowe - w klasie PTWP_A, roslinnoæ trawiasta - w klasie PTTR_A, natomiast wysokie budowle techiczne - w BUWT_P.␍
# ␍
# Kryteria oceny projektu:␍
# * wyniki analiz i opis przebiegu 3x30p=90pkt␍
# * forma sprawozdania 10pkt␍
# suma 100 pkt␍
