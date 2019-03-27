#! /usr/bin/env python
# -*- coding: utf-8 -*-

#Programador 1: Bernat Bosca Candel
#Programador 2: Albert Cañellas Solé

#Llibreries
from Tkinter import *
import Tkinter as tk
import os, sys, difflib
import tkMessageBox, tkFileDialog

#Funcions auxiliars a les funcions dels botons
##############################################
#Busca tots els path dels fitxers iguals al que rep i els afegeix a la llista 'listResult'
def find_all(file_name, path, listResult):
	for path_list, dir_list, files in os.walk(path):
		if file_name in files:
			listResult.append(os.path.join(path_list, file_name))

#Retorna 'True' si hi ha al menys un fitxer igual al arbre de directoris rebuts
def find_some1(file_name, path):
	for path_list, dir_list, files in os.walk(path):
		if file_name in files:
        	    return True
	return False

#Retorna el numero de linies iguals als fitxers, si es 0 vol dir que son iguals
def find_iguals(fileX, fileY):
	num_lines = 0
	file1 = open(fileX, 'r')
	file2 = open(fileY, 'r')
	while True:
		line1 = file1.readline()
		line2 = file2.readline()
		if not line1 == line2:
			num_lines += 1
		if not line1 and not line2:
			break
	file1.close()
	file2.close()
	return num_lines

#Funcions dels botons
##############################################

#variables globals
dirLOrigin = []		#Llista dels fitxers originals amb path absolut
dirLIguals = []		#Llista dels fitxers iguals amb path absolut
dirLSemb = []		#Llista dels fitxers semblants amb path absolut (sols nom igual)
numLinesDif = []	#Llista del numero de linies diferent per a cada fitxer semblant
nomfnou = "nom"		#Variable per a renombrar, nom nou
nomfvell = "nom"	#Varianle per a renombrar, nom antic

#Actualitzar path del directori
def opendirX (dirX, finestra, text):
	dirX.set(tkFileDialog.askdirectory(parent=finestra, initialdir=dirX.get(), title=text))
#Operacions per fer la cerca
def find_files (dirFont, dirDesti, listOrigin, listIguals, listSemb):
	global dirLOrigin
	global dirLIguals
	global dirLSemb
	global numLinesDif
	dirLOrigin = []
	dirLIguals = []
	dirLSemb = []
	numLinesDif = []
	dirLFont = os.listdir(dirFont.get())
	i = 0
	while (i<len(dirLFont)):
		file = dirLFont[i]		
		if not os.path.isfile(file):		#Si es un directori l'eliminem de la llista origin
			del dirLFont[i];
		elif not find_some1(file, dirDesti.get()):
			del dirLFont[i];		#Si no te cap fitxer amb el nom igua l'eliminem de la llista origin
		else:
			listOrigin.insert(END, dirLFont[i])		#Si entrem al else es que es tracta d'un fitxer que te alguna copia
			dirLOrigin.append(os.path.join(dirFont.get(), dirLFont[i]))
			i += 1
	#Obtenim la llista dels fitxers originals(tenen al menys 1 copia al path destí)
	dirLFont = dirLFont[:len(dirLOrigin)]	
	dirLFL = []
	i = 0
	for file in dirLFont:
		find_all(file, dirDesti.get(), dirLFL)
		while i < len(dirLFL):
			#Ara clasifiquem els fitxers en Iguals o Semblants segons la funció find_iguals
			num_lines = find_iguals(file, dirLFL[i])		
			if num_lines == 0:
				listIguals.insert(END, os.path.relpath(dirLFL[i], dirDesti.get()))
				dirLIguals.append(dirLFL[i])
			else:
				listSemb.insert(END, os.path.relpath(dirLFL[i], dirDesti.get()))
				dirLSemb.append(dirLFL[i])
				numLinesDif.append(num_lines)
			i += 1
#Funcio per a renombrar fitxers
def rename (listbox, finestra):
	global nomfnou
	global nomfvell
	selec = listbox.curselection()
	pos = len(selec)
	i = 0
	while (i<pos):
		idx = selec[i]		
		nomfvell = os.path.basename(dirLSemb[idx])
		inputNom=MyDialog(finestra)
		finestra.wait_window(inputNom.top)
		if not nomfnou == '':					#Sols ha clicat Acceptar, no ha escrit res
			path = dirLSemb[idx]
			nomNou = os.path.dirname(path)+'/'+nomfnou
			os.rename(path, nomNou)
		i += 1
#Depenen de l'opcio 'quina' serveix per elimanr fitxers iguals(quina=0) o semblants(quina=altre nombre)
def delete (listBox, quina):
	global dirLIguals
	global dirLSemb	
	selec = listBox.curselection()
	pos = len(selec)
	i = 0
	auxlist = []	
	if quina == 0:
		auxlist = dirLIguals
	else:
		auxlist = dirLSemb
	while (i<pos):
		idx = selec[i]
		path = auxlist[idx]
		os.remove(path)
		auxlist[idx] = 'x'
		listBox.delete(idx, None)
		i += 1
	i = 0
	while (i<len(auxlist)):
		if auxlist[i] == 'x':			#Eliminem de la llista global els fitxers marcats
			del auxlist[i]			#Ho fem així perque de l'altra forma sens descuadrava el ordre d'eliminació
		else:
			i += 1
	if quina == 0:
		dirLIguals = auxlist
	else:
		dirLSemb = auxlist
#Funcio que serveix per fer un hard linck(quin=0), soft linck(quin=1) o comparar(quin=2)
def links (listBox, dirDesti, quin, finestra):
	global dirLIguals
	global dirLOrigin
	global dirLSemb
	global numLinesDif
	selec = listBox.curselection()
	pos = len(selec)
	i = 0
	auxlist = []	
	if not quin == 2:
		auxlist = dirLIguals			#Per a soft o hard link necesitem els fitxers iguals
	else:						#Per a compara necesitem els fitxers semblants
		auxlist = dirLSemb
		inode = []				#Inodes dels fitxers seleccionats
		pathRDSemb = []				#Path relatiu a Destí dels fitxers semblants
		n_linies = []				#Número de línies diferents
		fitxersOri = []				#Nom dels fitxers originals que tenen fitxer semblant
	while (i<pos):
		idx = selec[i]
		path = auxlist[idx]						#Path: path absolut del fitxer destí(Igu o Semb)
		nomf = os.path.basename(auxlist[idx])				#Nom fitxer del Path
		y = 0
		while (y<len(dirLOrigin)):
			if (nomf == os.path.basename(dirLOrigin[y])):
				if quin < 2:				
					os.remove(path)
					if quin == 0:				#PathOri: path absolut del fitxer Original
						os.link(dirLOrigin[y], path)		#Creem el hard link
					else:				
						os.symlink(dirLOrigin[y], path)		#Creem el soft link
				else:
					statresult = os.stat(path)			#Calculem les dades comparades als diferents fitxers
					inode.append(statresult[1])
					pathRDSemb.append(os.path.relpath(path, dirDesti.get()))
					n_linies.append(numLinesDif[i])
					fitxersOri.append(os.path.basename(dirLOrigin[y]))		#Nom fitxer del PathOri
				break
			y += 1
		i += 1
	#cridar finestra compara
	if quin == 2:
		inputNom=MyDialog1(finestra, inode, pathRDSemb, n_linies, fitxersOri)			#Obrim el dialog de compara
		finestra.wait_window(inputNom.top)							#Esperem fins que ens cliquen Accepta

#Classes dialog per compara i renombra
##############################################

#Classe per compara
class MyDialog1:		#la class MyDialog que em serveix per mostrar les diferencies dels fitxers seleccionats
	def __init__(self, parent, inode, pathRDSemb, n_linies, fitxersOri):
		top = self.top = Toplevel(parent)
		i = 0
		label=tk.Label(top)
		label.pack(side=BOTTOM)
		self.mySubmitButton = tk.Button(top, text='Accepta', command=self.send)
		self.mySubmitButton.pack(side=BOTTOM)
		label=tk.Label(top)
		label.pack()
		fram=Frame(top)				#Primera columna, apilem un baix del altre dins de la columna
		label=tk.Label(fram, text='\tFitxer amb path relatiu a destí:\t')
		label.pack(anchor=W)
		label=tk.Label(fram, text='\tAmb inode:\t')
		label.pack(anchor=W)
		label=tk.Label(fram, text='\tComparat amb:\t')
		label.pack(anchor=W)
		label=tk.Label(fram, text='\tNumero de linies diferents:\t')
		label.pack(anchor=W)
		fram.pack(side=LEFT)
		while (i<len(pathRDSemb)):
			fram=Frame(top)			#Una columna per fitxer
			label=tk.Label(fram, text=pathRDSemb[i]+'\t')
			label.pack(anchor=W)
			label=tk.Label(fram, text=str(inode[i])+'\t')
			label.pack(anchor=W)
			label=tk.Label(fram, text=fitxersOri[i]+'\t')
			label.pack(anchor=W)
			label=tk.Label(fram, text=str(n_linies[i])+'\t')
			label.pack(anchor=W)
			fram.pack(side=LEFT)
			i += 1
	def send(self):  #el boto guarda el nou nom
		self.top.destroy()

#Classe per renombra
class MyDialog:		#la class MyDialog que ens serveix per preguntar el nou nom del fitxer
	def __init__(self, parent):
		global nomfvell		
		top=self.top = Toplevel(parent)
		label=tk.Label(top)			#Busquem que quede centrat el contingut amb marges
		label.pack()
		label=tk.Label(top, width=5)
		label.pack(side=LEFT)
		label=tk.Label(top, width=5)
		label.pack(side=RIGHT)
		label=tk.Label(top, text='*Si no vols canviar el nom, clica igualment (Accepta)')
		label.pack(side=BOTTOM, anchor=W)
		label=tk.Label(top)
		label.pack(side=BOTTOM)
		self.myLabel = tk.Label(top, text='Escriu el nou nom per a ('+nomfvell+')')
		self.myLabel.pack()
		self.myEntryBox = tk.Entry(top, width=65)
		self.myEntryBox.pack(expand=1, fill=X)
		self.mySubmitButton = tk.Button(top, text='Accepta', command=self.send)
		self.mySubmitButton.pack()
	def send(self):	 #el boto guarda el nou nom
		global nomfnou			
		nomfnou=self.myEntryBox.get()
		self.top.destroy()


	
