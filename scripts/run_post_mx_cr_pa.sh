#!/bin/bash
# Pasos posteriores a regional_bo_py_ideologia_pobreza.py (ver LEEME). Correr desde la carpeta raíz.
set -e
for s in ampliacion_mx_cr_pa percepcion_economica_panel aprobacion_completa us_completar us_completar_parche inflacion_parche mandato_parche cuenta_corriente_wb_panel panel_modelo_completo regional_cr mx_parse_estados regional_mx; do python3 -I scripts/$s.py >/tmp/log_$s.txt 2>&1 || { echo FALLO $s; tail -5 /tmp/log_$s.txt; exit 1; }; done
