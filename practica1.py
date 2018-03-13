#!/usr/bin/python3
'''
APLICACION WEB GENERADORA DE URLS CORTAS
GUARDA EN DISCO LAS URLS LARGAS Y CORTAS
NECESITA UN FICHERO CREADO "my_urls.txt"
By: FLAVIO ALONSO ARRUNATEGUI REQUEJO
'''

import webapp
from urllib.parse import unquote
import csv

formulario = """
	<form action="" method="POST">
	INTRODUCE UNA URL:<br>
	<input type="text" name="url" value=""><br>
	<input type="submit" value="Listo">
</form>
"""
OK = "200 OK"
Not_Found = "404 ERROR"


def buscar(recurso):
	recurso = recurso.split('/')[1]  # quitamos prefijo "/"
	existe = False
	url_real = None
	for rec in urls_acortadas:
		if rec == recurso:
			existe = True
	if existe:
		for url in urls_reales:
			if urls_reales[url] == recurso:
				url_real = url
	return (existe, url_real)


def acortar(url):
	if url.find("http://") != 0 and url.find("https://") != 0:
        # la url NO empieza por http:// o https://
		url = ("http://" + url)  # añadimos http:// al inicio

	url_ac = "NoAcortada"
	add = "NO"
	for my_url in urls_reales:
		if my_url == url:  # ya se ha acortado antes la url
			numero = urls_reales[my_url]
			url_ac = urls_acortadas[numero]

	if url_ac == "NoAcortada":
		add = "SI"  # habra que añadir al diccionario
		numero = len(urls_acortadas)
		url_ac = "http://" + host_name + ":" + str(port) + "/" + str(numero)
		numero = str(numero)  # 'numero'
	return (add, url_ac, url, numero)


def cargar_urls():
    with open('my_urls.txt', 'r') as fd:
        try:
            reales_acortadas = fd.readlines()
            reales = reales_acortadas[0].split(',')[:-1]  # no tomar /n
            acortadas = reales_acortadas[1].split(',')[:-1]  # no tomar eof
            i = 0
            for k in reales:
                urls_reales[k] = str(i)
                i = i + 1
            i = 0
            for v in acortadas:
                numero = v.split('/')[-1]
                urls_acortadas[numero] = v
                i = i + 1
        except IndexError:
            print("Fichero vacio - NO URLs en disco")

    fd.close()
    return None


def guardar_urls():
    fd = open('my_urls.txt', 'w')
    for k, v in urls_reales.items():
        fd.write(k)
        fd.write(',')
    fd.write('\n')  # segunda linea -> acortados
    for k, v in urls_acortadas.items():
        fd.write(v)
        fd.write(',')
    fd.close()
    return None


class practica1(webapp.webApp):
    def __init__(self, hostname, port):
        cargar_urls()
        super().__init__(hostname, port)

    def parse(self, request):
        try:
            metodo = request.split()[0]
            recurso = request.split()[1]  # /recurso
            peticion = request.split()
            return (metodo, recurso, peticion)
        except IndexError:  # para favicon.ico
            return ("None", "None", "None")  # process se encarga

    def process(self, parsedRequest):
        (metodo, recurso, peticion) = parsedRequest
        if metodo == 'GET':
            if(recurso != '/'):  # cuando hay un recurso
                (existe, url_real) = buscar(recurso)  # el recurso existe?
                if existe:
                	http_redirect = ("<meta http-equiv='" + "refresh'" +
                					'content="' + '0;URL='+ url_real + '"/>')
                	return(OK, "<html><body> REDIRIGIENDO..." + http_redirect +
                                "</body></html>")
                else:
                	htmlAnswer = ("<html><body><h1>RECURSO NO DISPONIBLE\
                	                </h1></body></html>")
                	return (Not_Found, htmlAnswer)
            else:
                titulo = "<h1>PRACTICA 1 - SARO - Web Acortadora de Urls</h1>"
                lista = ("<br> URLS REALES: " + str(urls_reales)
                + "<br> URLS ACORTADAS: " + str(urls_acortadas))

                return(OK, "<html><body>" + titulo + formulario + lista +
                                "</body></html>")

        elif metodo == 'POST':
            # unquote corrige errores %3A%2F%2F
            url = unquote(peticion[-1].split('=')[1])
            if url != '':  # han escrito una url (qs valido)
                (add, url_ac, url_real, numero) = acortar(url)
                if add == 'SI':
                    urls_reales[url_real] = numero   # añadimos al diccionario
                    urls_acortadas[numero] = url_ac
                    guardar_urls()   # añadimos el diccionario al fichero

                enlace = ("<a href='" + url_real + "'>URL ORIGINAL</a>\
                            <a href='" + url_ac + "'>URL ACORTADA</a>")
                htmlAnswer = "<html><body>" + enlace + "</body></html>"
                return(OK, htmlAnswer)
            else:
                htmlAnswer = "<html><body><h1>Introduce una URL en el\
                                formulario</h1></body></html>"
                return (Not_Found, htmlAnswer)
        else:  # favicon.ico o para otros METODOS
            htmlAnswer = "<html><body><h1>ERROR 404 NOT FOUND\
                            </h1></body></html>"
            return (Not_Found, htmlAnswer)

if __name__ == "__main__":
    urls_reales = {}  # {'url_real': 'numero'}
    urls_acortadas = {}  # {'numero': 'url_ac'}
    host_name = 'localhost'
    port = 1234
    WebApp_Urls = practica1(host_name, port)
