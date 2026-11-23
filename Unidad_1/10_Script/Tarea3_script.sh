# SECCIÓN 1 --------------------
# Cantidad de lineas
wc -l oecd_bli_2015.csv

wc -l gdp_per_capita.csv

# Encabezados de ambos archivos y delimitadores
head -n 2 oecd_bli_2015.csv 

head -n 2 gdp_per_capita.csv 

# SECCIÓN 2 --------------------

awk -F',' '$3 == "\"SW_LIFS\"" && $7 == "\"TOT\"" {
	gsub(/"/, "", $2); 
    	gsub(/"/, "", $15);
	print $2 "," $15
}' oecd_bli_2015.csv > oecd_limpio.csv


# SECCIÓN 3 --------------------

awk -F'\t' 'NR>1 && $1 != "" {
	gsub(/,/, "", $6); 
	print $1 "," $6
}' gdp_per_capita.csv > gdp_limpio.csv

# SECCIÓN 4 --------------------
# Ordenar alfabeticamente

sort -t',' -k1,1 oecd_limpio.csv > oecd_sorted.csv

sort -t',' -k1,1 gdp_limpio.csv > gdp_sorted.csv

echo "Pais,Satisfaccion_Vida,PIB_Capita" > merge_data.csv

join -t',' -1 1 -2 1 oecd_sorted.csv gdp_sorted.csv >> merge_data.csv

# SECCIÓN 5 --------------------

tail -n +2 merge_data.csv | cut -d',' -f3 > X.csv

tail -n +2 merge_data.csv | cut -d',' -f2 > y.csv

