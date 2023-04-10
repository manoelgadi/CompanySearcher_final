# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 13:26:05 2020

@author: Prof. Manoel Gadi
"""



from urllib.request import urlopen
sourceCode = urlopen("http://tobesure.pythonanywhere.com/buscador?nif=A28015865&JSON=yes&modelo=yes").read()

import json
empresas = json.loads(sourceCode)

print(empresas[0]['Nombre'])
print(empresas[0]['probabilidad_default'])