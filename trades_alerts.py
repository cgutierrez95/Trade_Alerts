"""
@author: Carlos Andrés Gutiérrez González
"""
# Se impoartan todas la librerias a utilizar
# Librerias para GUI
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui
from PyQt5.uic import loadUiType

# Librerias para el manejo de datos
import pandas as pd
import numpy as np
import sqlite3

# Libreria para el manejo de fechas
import datetime as dt

# Libreria para el manejo de API's
import requests

#Librerias para el manejo de rutas.
import os
from os import path
import sys 

#Librerias para la automatización de funciones.
import time
#import threading

#libreria para Whatsapp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#Libreria para screenshot
import pyautogui

#Libreria para saber el usuario activo
import getpass

update=0
# Función para el manejo de rutas al momento de ejecución del programa.
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for Py Installer"""
    base_path= getattr(sys,'MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

#Se define y se carga el form que se utilizará.
FORM_CLASS,_=loadUiType(resource_path("360trades.ui"))

#class TimerThread(QThread):
    #def run(self):
    #    i=0
   #     while i<=900:
  #          i+=1
 #           time.sleep(1)

#class Init_TimerThread(QThread):
    #def run(self):
        #i=0
       # while i<15:
       #     i+=1
      #      time.sleep(1)

#class TimeoutThread(QThread):
 #   def run(self):
  #      i=0
   #     while i<5:
    #        i+=1
     #       time.sleep(1)             

#Se define la clase Main
class Main(QMainWindow, FORM_CLASS):    
    
    #Se indican todos los métodos a correrse con el inicio de la aplicación.
    def __init__(self,parent=None):
        super(Main,self).__init__(parent)
        QMainWindow.__init__(self)        
        self.setupUi(self)
        self.Get_Data_Active_Trades()
        self.Handel_Buttons()
        self.load_add_trade()
        self.position()
        #self.Init_Timer()
                     
    #Se definen los métodos enlazados a un botón.    
    def Handel_Buttons(self):
        self.btn_update.clicked.connect(self.update_price)
        self.btn_end_trade.clicked.connect(self.end_trade)
        self.btn_add_trade.clicked.connect(self.add_trade)
        self.btn_salir.clicked.connect(self.exit)        
 
    #Función para el manejo de las bases de datos.    
    def sql(self,db,query,data):
        
        #Se establece la conexión con la base de datos.
        con=sqlite3.connect(resource_path(db))
        
        #Se crea el cursor para la consulta.
        c=con.cursor()
        
        #Se procede a intentar ejecutar la consulta
        try:
            c.execute(query,data)
        except:
            #La consulta fracasó y se termina la conexion con la base de datos
            con.commit()
            c.close()
            QMessageBox.question(self, 'Advertecia', "Hubo un error al acceder a la base de datos", QMessageBox.Ok)
            return
            
        finally:
            #La consulta fue exitosa y se termina la conexion con la base de datos.
            con.commit()
            c.close()
            return 
           
    #Función para agregar trades.
    def add_trade(self):
        
        #Se guardan todas las variables a utilizar.
        date=self.date_date.date().toPyDate()
        date=date.strftime("%d/%m/%Y")
        symbol=self.txt_symbol.text()
        
        try:
            entry_price=float(self.txt_entry_price.text())
        except:       
            QMessageBox.question(self, 'Advertecia', "El campo Entry Price no puede estar vacio", QMessageBox.Ok)
            return            
        
        try:
            exit1=float(self.txt_exit_1.text())
        except:
            QMessageBox.question(self, 'Advertecia', "El campo Exit #1 no puede estar vacio", QMessageBox.Ok)
            return
        
        try:
            exit2=float(self.txt_exit_2.text())
        except:
            exit2=0
            
        try:
            exit3=float(self.txt_exit_3.text())
        except:
            exit3=0 
        
        try:
            exit4=float(self.txt_exit_4.text())
        except:
            exit4=0         
                              
        try:
            stop_loss=float(self.txt_stop_loss.text())
        except:
            QMessageBox.question(self, 'Advertecia', "El campo Stop Loss no puede estar vacio", QMessageBox.Ok)
            return
                    
        current_price=0 
        active_id=1
        
        direction=self.cmb_direction.currentText()
        
        #Se realizan la validación del símbolo.
        if symbol.find("/")==-1:
            QMessageBox.question(self, 'Advertecia', "Falta agregar / en el símbolo", QMessageBox.Ok)
            return
        symbol=symbol.upper()
        
        #Se establecen los parametros para ejecutar la consulta SQL.
        query='''INSERT INTO active_trades(date, symbol, direction, entry_price, current_price, exit1, exit2, exit3, exit4, stop_loss, active_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)'''
        data=(date, symbol, direction, entry_price, current_price, exit1, exit2, exit3, exit4, stop_loss, active_id)
        self.sql("360trades.db",query,data)
               
        #Se reestablecen los textboxes para que esten vacios despues de la carga.
        self.txt_entry_price.setText("")
        self.txt_symbol.setText("")
        self.txt_exit_1.setText("")
        self.txt_exit_2.setText("")
        self.txt_exit_3.setText("")
        self.txt_exit_4.setText("")
        self.txt_stop_loss.setText("")
        
        #Se informa que el trade se ha agregado con éxito y se carga en los active trades.
        self.Get_Data_Active_Trades()
        
        
        #Se manda mensaje de que la carga concluyó correctamente
        QMessageBox.question(self, 'Advertecia', "El trade se ha agregado con éxito", QMessageBox.Ok)
    
    # Se establecen los parametros iniciales de add trades
    def load_add_trade(self):
        
        # Se establece la fecha del dia de hoy.
        today=dt.date.today()
        self.date_date.setDate(today)
        
        #Se precargan valores en el combobox.
        self.cmb_direction.addItems(["Long","Short"])
        self.cmb_direction.setFixedWidth(167)
        
        #Modifica los textboxes para que solo admiten caracteres numericos.
        self.txt_entry_price.setValidator(QtGui.QDoubleValidator())
        self.txt_exit_1.setValidator(QtGui.QDoubleValidator())
        self.txt_exit_2.setValidator(QtGui.QDoubleValidator())
        self.txt_exit_3.setValidator(QtGui.QDoubleValidator())
        self.txt_exit_4.setValidator(QtGui.QDoubleValidator())
        self.txt_stop_loss.setValidator(QtGui.QDoubleValidator())
       
    #Función para hacer los requests del precio actual a Binance    
    def API_Binance_Update_Price(self,symbol):

        #Se establece la conexion con la API de Binance
        current_price=requests.get("http://binance.com/api/v3/ticker/price",params=symbol)
        
        #Se evaluan todos los posibles resultados de la consulta a Binance.
        if current_price.status_code==400:
            return 0
        
        if current_price.status_code==403:
            self.close()
            return "Se ha violado el Firewall"
        
        if current_price.status_code==429:
            self.close()
            return "Se ha excedido el numero de consultas"
            
        if current_price.status_code==418:
            self.close()
            return "Se ha bloqueado la dirección IP"
        
        if current_price.status_code>=500:
            return "Binance esta teniendo problemas"
        
        if current_price.status_code==200:
            try:              
                return float(current_price.json()["price"])
            except:
                return"Ha ocurrido un error al momento de regresar el precio"    
            
    #Función para la carga inicial de active trades y se le da formato.
    def Get_Data_Active_Trades(self):

        #Se establece la conexión con la base de datos.
        con=sqlite3.connect(resource_path("360trades.db"))
        result=pd.read_sql('select * from active_trades where active_id=1',con)
        con.close()
        
        # A partir de la consulta, se crean las columnas necesarias.
        #Se calculan todos los % de ganancia de los exits
        
        p0=pd.DataFrame({'p0':(((result['current_price']/result['entry_price']))*100).round(2)})
        result=pd.concat([result,p0],axis=1)
        
        p1=pd.DataFrame({'p1':(((result['exit1']/result['entry_price'])-1)*100).round(2)})
        result=pd.concat([result,p1],axis=1)
        
        p2=pd.DataFrame({'p2':(((result['exit2']/result['entry_price'])-1)*100).round(2)})
        result=pd.concat([result,p2],axis=1)
        
        p3=pd.DataFrame({'p3':(((result['exit3']/result['entry_price'])-1)*100).round(2)})
        result=pd.concat([result,p3],axis=1)
        
        p4=pd.DataFrame({'p4':(((result['exit4']/result['entry_price'])-1)*100).round(2)}) 
        result=pd.concat([result,p4],axis=1)

        pl=pd.DataFrame({'pl':(-(1-(result['stop_loss']/result['entry_price']))*100).round(2)})
        result=pd.concat([result,pl],axis=1)  
    
        #Acomoda el dataframe en el orden necesario.
        result=result.reindex(columns=["trade_id", "date", "symbol", "direction", "entry_price", "current_price", "p0", "exit1",
                                       "p1", "exit2", "p2", "exit3", "p3", "exit4", "p4", "stop_loss","pl"])
    
        #Establece el tamaño del DataFrame a cargar.
        shape=result.shape
        filas=shape[0]
        columnas=shape[1]
    
        #Carga en la tabla los datos obtenidos de la consulta
        self.tbl_360_trades.setRowCount(0)

        for a in range(filas):
            self.tbl_360_trades.insertRow(a)
            for b in range(columnas):
                item=(result.iloc[a,b])
                self.tbl_360_trades.setItem(a,b, QTableWidgetItem(str(item)))
        
        #Se le da formato a la tabla
        self.table_format(filas,columnas)
        
        #Establece el modo solo lectura a la tabla
        self.tbl_360_trades.setEditTriggers(QAbstractItemView.NoEditTriggers)
                        
    #Función para dar formato a la tabla de active_trades
    def table_format(self,filas,columnas):
        # Se llama a la función de asignacion de colores dinámicos
        self.colores(filas)
   
        #Fuente Y Alineación De Columnas
        for a in range(filas):
            for b in range(columnas):
                self.tbl_360_trades.item(a,b).setFont(QtGui.QFont('Arial', 9, QtGui.QFont.Bold))
                self.tbl_360_trades.item(a,b).setTextAlignment(Qt.AlignCenter)
                
        #Header Borders
        self.tbl_360_trades.setStyleSheet( "QHeaderView::section{"
            "border-top:0px solid #D8D8D8;"
            "border-left:0px solid #D8D8D8;"
            "border-right:1px solid #D8D8D8;"
            "border-bottom: 1px solid #D8D8D8;"
            "background-color:white;"
            "padding-top:4px;"
        "}"
        "QTableCornerButton::section{"
            "border-top:0px solid #D8D8D8;"
            "border-left:0px solid #D8D8D8;"
            "border-right:1px solid #D8D8D8;"
            "border-bottom: 1px solid #D8D8D8;"
            "background-color:white;"
        "}"
        );
        
        #Column Resize
        self.tbl_360_trades.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tbl_360_trades.resizeColumnsToContents()
              
    #Función para terminar los trades y pasarlos a históricos.    
    def end_trade(self):
        
        #Se recupera la fila del trade que se va a terminar.
        fila=self.tbl_360_trades.currentRow()
        
        #Verifica que se seleccione una fila valida
        if fila<0:
            QMessageBox.question(self, 'Advertecia', "Por favor seleccione una fila", QMessageBox.Ok)
            return
                
        #Se almacenan las variables a grabar en la tabla.
        trade_id= int(self.tbl_360_trades.item(fila,0).text())  
            
        #Se agrega el trade a historic trades
        query='''Update active_trades set active_id = ? where trade_id=?'''
        
        data=(0,trade_id)
        self.sql("360trades.db", query, data)
        
        # Se elimina el renglon de la tabla
        self.tbl_360_trades.removeRow(self.tbl_360_trades.currentRow())
            
        #Se actualizan las tablas para mostrar la información.
        self.Get_Data_Active_Trades()

    #Función para cerrar la aplicación con la tecla escape.
    def keyPressEvent(self,event):
                
        if event.key()==Qt.Key_Escape:
            buttonReply=QMessageBox.question(self, 'Salir', "Esta seguro que desea salir de la aplicación", QMessageBox.Yes | QMessageBox.No )
            if buttonReply == QMessageBox.Yes:
                self.close()
            if buttonReply == QMessageBox.No:
                return
            
    #Función para actualizar el preio con Binance    
    def update_price(self):
          
        symbols=[]
        updated_prices=[]
        
        #Se cuentan cuantos simbolos se actualizar
        filas= self.tbl_360_trades.rowCount()
        
        #Se extraen los simbolos a actualizar y se guardan en una lista.
        for a in range(filas):
             symbol=self.tbl_360_trades.item(a,2).text()
             symbol=symbol.replace("/","")
             symbol="symbol="+symbol
             
             symbols.append(symbol)
        
        #Se pide el precio actualizado a Binance.
        for symbol in symbols:
            updated_prices.append(self.API_Binance_Update_Price(symbol))
             
        #Se actualiza la tabla tbl_active_trades y la base de datos active_trades     
        for a, updated_price in enumerate(updated_prices):
            self.tbl_360_trades.setItem(a,5, QTableWidgetItem(str(updated_price)))

            query="""Update active_trades set current_price= ? where trade_id = ?"""
            trade_id=int(self.tbl_360_trades.item(a,0).text())
            try:
                data=(float(updated_price), trade_id)
            except:
                data= (0, trade_id)
                
            self.sql("360trades.db", query, data)
        
        filas=self.tbl_360_trades.rowCount()
        columnas=self.tbl_360_trades.columnCount()
        self.recalc()
        self.table_format(filas,columnas)
        #self.timeout_screen()
            
    #Funcion para establecer los colores dinamicos de cada trade    
    def colores(self, filas):
        
        #Se establecen los colores a utilizar       
        fondo_verde=QtGui.QColor(0,176,80)
        texto_verde=QtGui.QColor(0,97,0)
        
        fondo_rojo=QtGui.QColor(255,199,206)
        texto_rojo=QtGui.QColor(156,0,6)
        
        fondo_amarillo=QtGui.QColor(255,235,156)
        texto_amarillo=QtGui.QColor(156,101,0)
        
        fondo_gris=QtGui.QColor(165,165,165)

        texto_negro=QtGui.QColor(0,0,0)        
        
        for a in range(filas):

            #Formato para el current price
            if float(self.tbl_360_trades.item(a,6).text())>=90 and float(self.tbl_360_trades.item(a,6).text())<98 :
                self.tbl_360_trades.item(a,6).setBackground(fondo_amarillo)
                self.tbl_360_trades.item(a,6).setForeground(texto_amarillo)               
            elif float(self.tbl_360_trades.item(a,6).text())>=98:
                self.tbl_360_trades.item(a,6).setBackground(fondo_verde)
                self.tbl_360_trades.item(a,6).setForeground(texto_verde)
            
            #Formato para exit #1
            check=(float(self.tbl_360_trades.item(a,5).text())/float(self.tbl_360_trades.item(a,7).text()))
            if check>=.90 and check<.98:
                self.tbl_360_trades.item(a,8).setBackground(fondo_amarillo)
                self.tbl_360_trades.item(a,8).setForeground(texto_amarillo)
            elif check>=.98:
                self.tbl_360_trades.item(a,8).setBackground(fondo_verde)
                self.tbl_360_trades.item(a,8).setForeground(texto_verde)
            else:
                self.tbl_360_trades.item(a,8).setBackground(fondo_gris)
                self.tbl_360_trades.item(a,8).setForeground(texto_negro)
               
            #Formato para exit #2
            try:
                check=(float(self.tbl_360_trades.item(a,5).text())/float(self.tbl_360_trades.item(a,9).text()))
                if check>=.90 and check<.98:
                    self.tbl_360_trades.item(a,10).setBackground(fondo_amarillo)
                    self.tbl_360_trades.item(a,10).setForeground(texto_amarillo)
                elif check>=.98:
                    self.tbl_360_trades.item(a,10).setBackground(fondo_verde)
                    self.tbl_360_trades.item(a,10).setForeground(texto_verde)
                else:
                    self.tbl_360_trades.item(a,10).setBackground(fondo_gris)
                    self.tbl_360_trades.item(a,10).setForeground(texto_negro)
            except:
                self.tbl_360_trades.setItem(a,10, QTableWidgetItem(str(0)))
                
            #Formato para exit #3
            try:
                check=(float(self.tbl_360_trades.item(a,5).text())/float(self.tbl_360_trades.item(a,11).text()))
                if check>=.90 and check<.98:
                    self.tbl_360_trades.item(a,12).setBackground(fondo_amarillo)
                    self.tbl_360_trades.item(a,12).setForeground(texto_amarillo)
                elif check>=.98:
                    self.tbl_360_trades.item(a,12).setBackground(fondo_verde)
                    self.tbl_360_trades.item(a,12).setForeground(texto_verde)
                else:
                    self.tbl_360_trades.item(a,12).setBackground(fondo_gris)
                    self.tbl_360_trades.item(a,12).setForeground(texto_negro)
            except:
               self.tbl_360_trades.setItem(a,12, QTableWidgetItem(str(0)))
                
            #Formato para exit #4
            try:
                check=(float(self.tbl_360_trades.item(a,5).text())/float(self.tbl_360_trades.item(a,13).text()))
                if check>=.90 and check<.98:
                    self.tbl_360_trades.item(a,14).setBackground(fondo_amarillo)
                    self.tbl_360_trades.item(a,14).setForeground(texto_amarillo)
                elif check>=.98:
                    self.tbl_360_trades.item(a,14).setBackground(fondo_verde)
                    self.tbl_360_trades.item(a,14).setForeground(texto_verde)
                else:
                    self.tbl_360_trades.item(a,14).setBackground(fondo_gris)
                    self.tbl_360_trades.item(a,14).setForeground(texto_negro)
            except:
                self.tbl_360_trades.setItem(a,14, QTableWidgetItem(str(0)))
                
            #Formato para stop loss
            self.tbl_360_trades.item(a,16).setBackground(fondo_rojo)
            self.tbl_360_trades.item(a,16).setForeground(texto_rojo)     

    #Función encargada del envo de mensajes automatizados a traves de whatsapp
    def Whatsapp(self):
        
        # se establece la ruta de la imagen
        filepath=resource_path("screenshot.png")
        
        #Se establece el prefijo de la ruta donde se almacenan las credenciales de Whatsapp.
        prefix="user-data-dir=C:\\Users\\"
        usuario=getpass.getuser()
        sufix="\\appdata\\local\\Google\\Chrome\\User Data\\Wtsp"
        chrome_profile_path= prefix + usuario + sufix
                
        #Se consulta la hora actual para el mensaje
        datetime=dt.datetime.now()
        datetime=datetime.strftime("%d/%m/%Y %H:%M:%S")    
        
        #Separadores de text que se utilizaran en el mensaje.
        separador="==========="
        skip_line="""
"""        
        #Se define el encabezado del mensaje.
        msg=""
        msg_header= "Trade Alert "  + datetime + skip_line
        msg+=msg_header

        #Se recorreran toda la tabla en busca de todas las combinaciones posibles.
        filas=self.tbl_360_trades.rowCount()
        n=5
        contador=0
        for i in range(5):
            section_body=""
            tokens={}
            #Se guardan todos los tokens que cumplan con la condición dada.
            for a in range(filas):
                if i==0:
                    if float(self.tbl_360_trades.item(a,6).text())>=95 and float(self.tbl_360_trades.item(a,6).text())<=105:
                        tokens[self.tbl_360_trades.item(a,2).text()]=self.tbl_360_trades.item(a,6).text()
                else:
                    m = n + (i*2)
                    try:
                        check=float(self.tbl_360_trades.item(a,n).text())/float(self.tbl_360_trades.item(a,m).text())
                    except:
                        check=0
                    if check>=.95 and check<=1.05:
                        tokens[self.tbl_360_trades.item(a,2).text()]=str(round(check,2)*100)   
                                     
            # Dependiendo de la iteracion se seleccionan los mensajes pertinentes.
            if len(tokens)>0:
                if i==0:
                    section_title="Entry"
                    section_body_description="% del precio de entrada"
                if i==1:
                    section_title="Exit #1"
                    section_body_description="% del precio de salida #1"
                if i==2:
                    section_title="Exit #2"
                    section_body_description="% del precio de salida #2"
                if i==3:
                    section_title="Exit #3"
                    section_body_description="% del precio de salida #3"
                if i==4:
                    section_title="Exit #4"
                    section_body_description="% del precio de salida #4"
                    
                section_header= separador + section_title + separador + skip_line
                                
                for clave in tokens:
                    section_body+= clave + " esta al " + tokens.get(clave) + section_body_description                  
                    section_body+= skip_line    
                    contador+=1
            else:
                section_title=""
                section_header=""
                section_body=""
            
            if contador<=0:
                #self.Timer()
                return
            
            msg += section_header + section_body
                         
        #Se establecen los parametros para google chrome
        options = Options()
        options.add_argument(chrome_profile_path)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        #Se realiza la conexion con el driver y la página de whatsapp
        driver = webdriver.Chrome(resource_path("chromedriver.exe"), options=options)
        driver.maximize_window()
        driver.get('https://web.whatsapp.com')  #Already authenticated
        
        #Tiempo de espera para continuar la ejecución
        time.sleep(10)
        
        #Se establece el contacto/grupo al cual mandar el mensaje
        driver.find_element_by_xpath("//*[@title='Criptoboys']").click()
        
        #Se envian tantos mensajes como tokens acumulados existan.
        driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]').send_keys(msg)
        #driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button/span').click()
        
        #Se procede a enviar la imagen de la tabla.
        attachment_box = driver.find_element_by_xpath('//div[@title = "Adjuntar"]')
        attachment_box.click()
        image_box = driver.find_element_by_xpath('//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
        image_box.send_keys(filepath)
          
        #Tiempo de espera para la creación del objeto
        time.sleep(10)
        
        #Se manda la imagen
        send_button = driver.find_element_by_xpath('//span[@data-testid="send"]')
        send_button.click()
                                        
        #Se cierra la conexion con whatsapp y el navegador.
        time.sleep(15)
        driver.close()
        #self.Timer()
    
    #Funcion para salir del programa.             
    def exit(self):
        buttonReply=QMessageBox.question(self, 'Salir', "Esta seguro que desea salir de la aplicación", QMessageBox.Yes | QMessageBox.No )
        if buttonReply == QMessageBox.Yes:
            self.close()
        if buttonReply == QMessageBox.No:
            return

    #Función para recalcular el porcentaje de entrada.
    def recalc(self):
        #Se cuentan cuantas filas se tienen.
        filas=self.tbl_360_trades.rowCount()

        #Se actualizan los campos necesarios en todas las filas.        
        for a in range(filas):
            
            # Se actualizan los campos PnL y PnLp dependiendo de la dirección.            
            p0=(float(self.tbl_360_trades.item(a,5).text())/float(self.tbl_360_trades.item(a,4).text()))*100
            
            #Se redondean a dos dígitos los valores obtenidos.                
            p0=round(p0,2)
            
            #Se introducen los campos calculados a la tabla.
            self.tbl_360_trades.setItem(a,6, QTableWidgetItem(str(p0)))

    #Funcion que activa el timer periodico de 15 minutos.
    #def Timer(self):
     #   self.timer=TimerThread()
      #  self.timer.start()
       # self.timer.finished.connect(self.window)
            
    #Función que activa el timer inicial    
    #def Init_Timer(self):
     #   self.timer=Init_TimerThread()
      #  self.timer.start()
       # self.timer.finished.connect(self.window)

    #Funcion que permite regresar el foco y la vista a la ventana principal.    
    #def window(self):
     #   self.setWindowFlags(Qt.WindowStaysOnTopHint)
      #  self.activateWindow()
       # self.show()
        #self.raise_()
        #self.timeout()
    
    #Función que toma un screenshot de la tabla.    
    def screenshot(self):
                
        global update
        if update%4==0:
            update+=1
            x=self.geometry().x()
            y=self.geometry().y()
            
            #Se ajusta la posicion de x, y
            x+=22
            y+=47
            
            #se determina el ancho y el alto del objeto para el screenshot
            height=self.tbl_360_trades.geometry().height()
            width=self.tbl_360_trades.geometry().width()
            
            #Se toman las coordenadas del main window.    
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save(resource_path("screenshot.png"))
        
        update+=1
        self.Whatsapp()
   


    #Función que permite establecer la posicion de la ventana de manera centrada.
    def position(self):

        #Se crean los objetos para medir la pantalla
        app = QtWidgets.QApplication(sys.argv)
        screen=app.primaryScreen()
        size=screen.size()
        rect=screen.availableGeometry()

        #Se coloca el QMainWindow en el centro de la pantalla
        width=rect.width()
        height=rect.height()
        self.move(int(width/4)-int(width*.033), int(height/4))
    
    #Funcion que permite cargar los graficos antes de tomar el screenshot.
    #def timeout(self):
       # self.timer=TimeoutThread()
        #self.timer.start()
        #self.timer.finished.connect(self.update_price)
    
    #def timeout_screen(self):
     #   self.timer=TimeoutThread()
      #  self.timer.start()  
       # self.timer.finished.connect(self.screenshot)  
    
def main():
    app=QApplication(sys.argv)
    window=Main()
    window.show()
    app.exec()
      
if __name__=='__main__':
    main()    