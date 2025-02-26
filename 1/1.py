import geopandas as gpd

layer = "L4_1_BDOT10k__OT_ADMS_A"
file_name = "BDOT_analiza_zabudowa.gdb"
district_data = gpd.read_file(file_name, layer=layer)

district_name = 'Koniuchy'

# select row with nazwa = 'Koniuchy'
district = district_data[district_data['nazwa'] == district_name]

# 1) area
zabudowa_name = 'L4_1_BDOT10k__OT_PTZB_A'
zabudowa = gpd.read_file(file_name, layer=zabudowa_name)
zabudowa = zabudowa.clip(district)
area = zabudowa['Shape_Area'].sum()
print(f"Powierzchnia zabudowy mieszkaniowej w {district_name} to {area.sum():.2f} m²")
# save to file
zabudowa.to_file("zabudowa.gpkg")

# 2) 
# skdr
roads_name = 'L4_1_BDOT10k__OT_SKDR_L'
road_data = gpd.read_file(file_name, layer=roads_name)


# clip roads to district
roads = gpd.clip(road_data, district)
roads = roads[roads['katZarzadz'].isin(['P', 'G'])]
length_sum = roads['Shape_Length'].sum()
district_area = district['Shape_Area'].sum()
print(district_area)
print(length_sum)
road_density = length_sum / district_area * 1000 * 1000
print(f'Gęstość dróg gminnych i powiatowych: {road_density:.3f} m/km²')
roads.to_file("drogi.gpkg")

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
for i, layer in enumerate(objects):
    layer = gpd.clip(layer, diff_df)
    # change layer epsg to 2180
    layer.to_crs(epsg=2180, inplace=True)
    area_sum += layer.geometry.area.sum()
    objects[i] = layer

print(f'Powierzchnia terenów upraw trwałych, wód powierzchniowych oraz obszarów trawiastych w promieniu 0,8 oraz 1,8 km od wybranej wysokiej budowli technicznej: {area_sum:.2f} m²')
# save to diffs.gpkg
diff_df.to_file('diffs.gpkg')
objects[0].to_file('ptut.gpkg')
objects[1].to_file('ptwp.gpkg')
objects[2].to_file('pttr.gpkg')

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
