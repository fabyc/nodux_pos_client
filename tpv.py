#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import psycopg2
import psycopg2.extras
import hashlib
import xmlrpclib
import sys
import hashlib
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import QtGui


import Tkinter
root = Tkinter.Tk()


import sys
try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass
try:
	import gtk
  	import gtk.glade
  	gtk.set_interactive(1)
except:
	sys.exit(1)

class tpv:

	def __init__(self):

		#Set the Glade file
		self.gladefile = "facturador.glade"
		self.wTree = gtk.glade.XML(self.gladefile, "login_facturador")

		#Create our dictionay and connect it
		dic = {"on_loginFacturador_destroy" : gtk.main_quit
				, "on_AddFactura" : self.OnAddFactura, "on_loginCancel_destroy" : gtk.main_quit,
				"on_Exit_destroy" : gtk.main_quit, "on_AddProduct" : self.OnAddProduct,
				"on_SearchClient" : self.OnSearchCliente}
		self.wTree.signal_autoconnect(dic)

		from proteus import config, Wizard, Model
		database = 'pymes'
		user = 'admin'
		password = 'pymes'


	def OnAddProduct(self, widget):
	    self.wTree = gtk.glade.XML(self.gladefile, "factura_detalle")
	    #Get the actual dialog widget
	    self.dlg = self.wTree.get_widget("factura_detalle")
	    dic = {"on_SearchProduct": self.OnSearchProduct}
	    self.wTree.signal_autoconnect(dic)

	    self.cCodigo = 0
	    self.cDescripcion = 1
	    self.cCantidad = 2
	    self.sCodigo = "Codigo"
	    self.sDescripcion = "Producto"
	    self.sCantidad = "Stock"

	    self.treeview_detalle_producto = self.wTree.get_widget("treeview_detalle_producto")
	    #Add all of the List Columns to the lineView
	    self.AddProductListColumn(self.sCodigo, self.cCodigo)
	    self.AddProductListColumn(self.sDescripcion, self.cDescripcion)
	    self.AddProductListColumn(self.sCantidad, self.cCantidad)
	    self.searchProductList = gtk.ListStore(str, str, str)
	    #Attache the model to the treeView
	    self.treeview_detalle_producto.set_model(self.searchProductList)
	    self.treeview_detalle_producto.get_selection().connect("changed", self.OnChanged)
	    #self.treeview_detalle_producto.get_selection().connect("select-cursor-row", self.OnChanged)
	    #self.treeview_detalle_producto.get_selection().connect("cursor-changed", self.OnChanged)
	    #self.treeview_detalle_producto.get_selection().connect("unselect-all", self.OnChanged)
	    #self.treeview_detalle_producto.get_selection().connect("toggle-cursor-row", self.OnChanged)
	    #self.treeview_detalle_producto.get_selection().connect("select-all", self.OnChanged)

	    self.cPrecio = 0
	    self.sPrecio = "Precio"

	    self.treeview_detalle_precios = self.wTree.get_widget("treeview_detalle_precios")
	    self.AddPriceListColumn(self.sPrecio, self.cPrecio)
	    self.PriceList = gtk.ListStore(str)
	    self.treeview_detalle_precios.set_model(self.PriceList)

	    self.cBodega = 0
	    self.cDCantidad = 1
	    self.sBodega = "Bodega"
	    self.sDCantidad = "Cantidad"

	    self.treeview_detalle_bodega = self.wTree.get_widget("treeview_detalle_bodega")
	    #Add all of the List Columns to the lineView
	    self.AddBodegasListColumn(self.sBodega, self.cBodega)
	    self.AddBodegasListColumn(self.sDCantidad, self.cDCantidad)
	    self.BodegaList = gtk.ListStore(str, str)
	    #Attache the model to the treeView
	    self.treeview_detalle_bodega.set_model(self.BodegaList)

	    self.dlg.show()

	def OnChanged(self, selection):
	    database = 'pymes' #base de datos
	    user = 'noduxdev' #usuario de la base de datos postgres
	    password = 'noduxdev' #password de la base de datos postgres
	    host = '192.168.1.45' #ip host
	    conn = psycopg2.connect(database=database,user= user, password=password, host=host)
	    cur = conn.cursor()
	    cur.execute("SELECT id FROM stock_location WHERE type ='warehouse'")
	    warehouse = cur.fetchall()
	    # get the model and the iterator that points at the data in the model
	    (model, iter) = selection.get_selected()
	    user_xmlrpc = 'admin' #usuario de la base de datos postgres
	    password_xmlrpc = 'pymes' #password de la base de datos postgres
	    s = xmlrpclib.ServerProxy ('http://%s:%s@192.168.1.45:8069/pymes' % (user_xmlrpc, password_xmlrpc))
	    nombre = ""
	    cantidad =""
	    precio = ""

	    if len(warehouse)>1:
	        self.BodegaList.clear()
	        for w in warehouse:
	            name, cantidad = s.model.einvoice.einvoice.search_warehouse(model[iter][1], warehouse[0] , {})
                self.bodega = Bodega(nombre, cantidad)
                self.bodega.bodega = name
                self.bodega.cantidad = cantidad
                elemento = self.BodegaList.pop()
                self.BodegaList.append([self.bodega.bodega, self.bodega.cantidad])

                price_list = s.model.einvoice.einvoice.search_price(model[iter][1], {})
                self.PriceList.clear()
                for p_l in price_list:
                    self.price_list = PriceList(precio)
                    self.price_list.precio = p_l
                    self.PriceList.append([self.price_list.precio])
	    else:
	        name, cantidad = s.model.einvoice.einvoice.search_warehouse(model[iter][1], warehouse[0], {})
	        self.bodega = Bodega(nombre, cantidad)
	        self.bodega.bodega = name
	        self.bodega.cantidad = cantidad
            self.BodegaList.clear()
            self.BodegaList.insert(0,[self.bodega.bodega, self.bodega.cantidad])

            price_list = s.model.einvoice.einvoice.search_price(model[iter][1], {})
            self.PriceList.clear()
            for p_l in price_list:
                self.price_list = PriceList(precio)
                self.price_list.precio =str(p_l["name"]) +": "+str(p_l["precio"])
                self.PriceList.insert(0,[self.price_list.precio])

	    self.entry_codigo_producto = self.wTree.get_widget("entry_codigo_producto")
	    self.entry_codigo_producto.set_text(model[iter][0])
	    self.entry_descripcion_producto = self.wTree.get_widget("entry_descripcion_producto")
	    self.entry_descripcion_producto.set_text(model[iter][1])
	    lotes = []
	    lotes = s.model.einvoice.einvoice.search_lote(model[iter][1], {})
	    self.listlotes = gtk.ListStore(int,str)
	    cont = 0


	    self.listlotes.clear()
	    for lote in lotes:
                cont = cont + 1
                self.listlotes.append([cont, lote['number']])
	    self.combobox_lotes_producto = self.wTree.get_widget("combobox_lotes_producto")
	    self.combobox_lotes_producto.set_model(self.listlotes)

	    self.cell = gtk.CellRendererText()
	    self.combobox_lotes_producto.pack_start(self.cell, True)
	    self.combobox_lotes_producto.add_attribute(self.cell, 'text', 1)
	    self.combobox_lotes_producto.set_active(0)
	    self.dlg.show()



    #para autocompletado
	def match_cb(self, completion, model, iter):
		print model[iter][0], 'was selected'
		return

	def activate_cb(self, entry):
		text = entry.get_text()
		print "El texto ", text
		if text:
		    if text not in [row[0] for row in self.liststore]:
		        self.liststore.append([text])
		        entry.set_text('')
		return

	def OnAddFactura(self, widget):
		#Create the dialog, show it, and store the results
		database = 'pymes' #base de datos
		user = 'noduxdev' #usuario de la base de datos postgres
		password = 'noduxdev' #password de la base de datos postgres
		host = '192.168.1.45' #ip host
		conn = psycopg2.connect(database=database,user= user, password=password, host=host)
		cur = conn.cursor()
		name_user = self.wTree.get_widget("entry_login").get_text()
		password_user = self.wTree.get_widget("entry_password").get_text()
		cur.execute("SELECT name, password_hash FROM res_user WHERE login =%s AND sale_device >0",[name_user])
		login = cur.fetchone()
		check = False
		if len(name_user) == 0 :
		    message = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
		    message.set_markup("Ingrese su nombre de usuario")
		    message.run()
		    message.destroy()
		elif len(password_user) == 0 :
		    message = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
		    message.set_markup("Ingrese su contraseña")
		    message.run()
		    message.destroy()

		else:
		    if login:
		        check = self.check_password(password_user, login[1])
		        if check == True:
		            self.cCodigo = 0
		            self.cDescripcion = 1
		            self.cCantidad = 2
		            self.cTotal = 3

		            self.sCodigo = "Codigo"
		            self.sDescripcion = "Producto"
		            self.sCantidad = "Cantidad"
		            self.sTotal = "Total"

		            dic = {"on_Exit_destroy" : gtk.main_quit, "on_AddProduct" : self.OnAddProduct,
				            "on_SearchClient" : self.OnSearchCliente, "on_SaveInvoice": self.OnSaveInvoice,
				            "on_AddClients": self.OnAddClients}

		            #Get the treeView from the widget Tree
		            self.wTree = gtk.glade.XML(self.gladefile, "facturageneral")
		            self.wTree.signal_autoconnect(dic)
		            self.dlg = self.wTree.get_widget("facturageneral")
		            self.treeview_detalle_de_factura = self.wTree.get_widget("treeview_detalle_de_factura")
		            #Add all of the List Columns to the lineView
		            self.AddInvoiceListColumn(self.sCodigo, self.cCodigo)
		            self.AddInvoiceListColumn(self.sDescripcion, self.cDescripcion)
		            self.AddInvoiceListColumn(self.sCantidad, self.cCantidad)
		            self.AddInvoiceListColumn(self.sTotal, self.cTotal)

		            #Create the listStore Model to use with the wineView
		            self.invoiceList = gtk.ListStore(str, str, str, str)
		            #Attache the model to the treeView
		            self.treeview_detalle_de_factura.set_model(self.invoiceList)

		            completion_name = gtk.EntryCompletion()
		            completion_vat_number = gtk.EntryCompletion()
		            self.liststore_id = gtk.ListStore(str)
		            self.liststore_names = gtk.ListStore(str)

		            cur.execute("SELECT vat_number FROM party_party")
		            parties_vat = cur.fetchall()
		            for p_v in parties_vat:
		                self.liststore_id.append([p_v[0]])
		            completion_vat_number.set_model(self.liststore_id)

		            cur.execute("SELECT name FROM party_party")
		            parties = cur.fetchall()
		            for p in parties:
		                self.liststore_names.append([p[0]])
		            completion_name.set_model(self.liststore_names)

		            self.entry_identificacion_cliente = self.wTree.get_widget("entry_identificacion_cliente")
		            self.entry_identificacion_cliente.set_completion(completion_vat_number)
		            completion_name.set_text_column(0)
		            self.entry_nombre_cliente = self.wTree.get_widget("entry_nombre_cliente")
		            self.entry_nombre_cliente.set_completion(completion_name)
		            completion_vat_number.set_text_column(0)

		            completion_vat_number.connect('match-selected', self.match_cb)
		            self.entry_identificacion_cliente.connect('activate', self.activate_cb)

		            self.entry_creada_por = self.wTree.get_widget("entry_creada_por")
		            self.entry_creada_por.set_text(login[0])

		            self.entry_status_factura = self.wTree.get_widget("entry_status_factura")
		            self.entry_status_factura.set_text("Borrador")

		            self.entry_status_factura = self.wTree.get_widget("entry_fecha_factura")
		            self.entry_status_factura.set_text("20/12/2016")

		            cur.execute("SELECT currency FROM company_company")
		            currency = cur.fetchone()
		            cur.execute("SELECT code FROM currency_currency WHERE id=%s", [currency[0]])
		            code_currency = cur.fetchone()

		            self.entry_moneda = self.wTree.get_widget("entry_moneda")
		            self.entry_moneda.set_text(code_currency[0])

		            self.liststore = gtk.ListStore(int,str)
		            cur.execute("SELECT name FROM product_price_list WHERE incluir_lista = True AND definir_precio_venta = True")
		            lista_venta = cur.fetchone()
		            self.liststore.append([0,lista_venta[0]])

		            cur.execute("SELECT name FROM product_price_list WHERE incluir_lista = True")
		            listas = cur.fetchall()
		            for lista in listas:
		                id_ = 1
		                self.liststore.append([id_,lista[0]])
		                id_ += 1
		            #the combobox
		            self.combobox = self.wTree.get_widget("combobox_listaprecios")
		            self.combobox.set_model(self.liststore)
		            self.cell = gtk.CellRendererText()
		            self.combobox.pack_start(self.cell, True)
		            self.combobox.add_attribute(self.cell, 'text', 1)
		            self.combobox.set_active(0)
		            self.dlg.show()
		        else:
		            self.wTree.get_widget("entry_login").set_text('')
		            self.wTree.get_widget("entry_password").set_text('')
		            message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
		            message.set_markup("Contraseña incorrecta")
		            message.run()
		            message.destroy()
		    else:
		        self.wTree.get_widget("entry_login").set_text('')
		        self.wTree.get_widget("entry_password").set_text('')
		        message = gtk.MessageDialog(type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_OK)
		        message.set_markup("Usuario no existe")
		        message.run()
		        message.destroy()

	def OnAddClients(self, widget):
	    self.wTree = gtk.glade.XML(self.gladefile, "catalogo_cliente")
	    #Get the actual dialog widget
	    self.dlg = self.wTree.get_widget("catalogo_cliente")
	    dic = {"on_SaveClients": self.OnSaveClients}
	    self.wTree.signal_autoconnect(dic)
	    self.dlg.show()

	def OnSaveClients(self, widget):
	    user = 'admin' #usuario de la base de datos postgres
	    password = 'whmcs' #password de la base de datos postgres
	    identificacion = self.wTree.get_widget("entry_identificacion_cliente").get_text()
	    telefono = self.wTree.get_widget("entry_telefono_cliente").get_text()
	    nombre = self.wTree.get_widget("entry_nombre_cliente").get_text()
	    direccion = self.wTree.get_widget("entry_direccion_cliente").get_text()
	    provincia = self.wTree.get_widget("entry_provincia_cliente").get_text()
	    telcelular = self.wTree.get_widget("entry_telcelular").get_text()
	    email = self.wTree.get_widget("entry_email_cliente").get_text()
	    s = xmlrpclib.ServerProxy ('http://%s:%s@192.168.1.45:8069/whmcs' % (user, password))

	    response = s.model.einvoice.einvoice.save_client(identificacion, telefono, nombre, direccion, provincia, telcelular, email, {})

	def OnSaveInvoice(self, widget):
	    print "Ingresa metodo de busqueda"
	    user = 'admin' #usuario de la base de datos postgres
	    password = 'whmcs' #password de la base de datos postgres
	    identificacion = self.wTree.get_widget("entry_identificacion_cliente").get_text()
	    date = self.wTree.get_widget("entry_fecha_factura").get_text()
	    moneda = self.wTree.get_widget("entry_moneda").get_text()
	    subtotal = self.wTree.get_widget("entry_subtotal").get_text()
	    total = self.wTree.get_widget("entry_total_factura").get_text()
	    vendedor = self.wTree.get_widget("entry_creada_por").get_text()
	    phonenumber= self.wTree.get_widget("entry_telefono_cliente").get_text()
	    address = self.wTree.get_widget("entry_direccion_cliente").get_text()
	    firstname = self.wTree.get_widget("entry_nombre_cliente").get_text()
	    s = xmlrpclib.ServerProxy ('http://%s:%s@192.168.1.45:8069/whmcs' % (user, password))
	    tipo = "factura"
	    id_factura = 29
	    maturity_date = date
	    items = []
	    lastname = ""
	    email= "etqm25@gmail.com"
	    city= "Loja"
	    state= "Loja"
	    country = "Ecuador"
	    print "Los datos ", date, moneda, subtotal, total, vendedor, phonenumber, address, firstname
	    response = s.model.einvoice.einvoice.save_invoice(tipo, id_factura, date, maturity_date, subtotal, total, identificacion, items, firstname, lastname, email, address, city, state, country, phonenumber, {})
	    self.entry_numero_factura = self.wTree.get_widget("entry_numero_factura")
	    self.entry_numero_factura.set_text(response)

	def OnSearchProduct(self, widget):
	    print "Self ", self
	    print "Ingresa metodo de busqueda"
	    name_product = self.wTree.get_widget("entry_descripcion_producto").get_text()
	    database = 'pymes' #base de datos
	    user = 'noduxdev' #usuario de la base de datos postgres
	    password = 'noduxdev' #password de la base de datos postgres
	    host = '192.168.1.45' #ip host
	    conn = psycopg2.connect(database=database,user= user, password=password, host=host)
	    cur = conn.cursor()
	    codigo = ""
	    cantidad= ""
	    descripcion = ""
	    self.product = Product(codigo, descripcion, cantidad)

	    if len(name_product) > 0:
	        #cur.execute("SELECT * FROM product_template WHERE name LIKE \"%{s}%\"",[name_product])
	        cur.execute("SELECT * FROM product_template WHERE name ILIKE '%cel%'")
	        products = cur.fetchall()
	    if products:
	        for p in products:
	            cur.execute("SELECT * FROM product_product WHERE id=%s", [p[0]])
	            producto = cur.fetchone()
	            if producto:
	                self.product.codigo = producto[2]
	            if p:
	                self.product.descripcion = p[4]
	                self.product.cantidad = p[0]
	            self.searchProductList.append([self.product.codigo, self.product.descripcion, self.product.cantidad])

	    view = gtk.TreeView(model=self.searchProductList)

	def AddProductListColumn(self, title, columnId):
		"""This function adds a column to the list view.
		First it create the gtk.TreeViewColumn and then set
		some needed properties"""

		column = gtk.TreeViewColumn(title, gtk.CellRendererText()
			, text=columnId)
		column.set_resizable(True)
		column.set_sort_column_id(columnId)
		self.treeview_detalle_producto.append_column(column)


	def AddPriceListColumn(self, title, columnId):
		"""This function adds a column to the list view.
		First it create the gtk.TreeViewColumn and then set
		some needed properties"""

		column = gtk.TreeViewColumn(title, gtk.CellRendererText()
			, text=columnId)
		column.set_resizable(True)
		column.set_sort_column_id(columnId)
		self.treeview_detalle_precios.append_column(column)

	def AddBodegasListColumn(self, title, columnId):
		"""This function adds a column to the list view.
		First it create the gtk.TreeViewColumn and then set
		some needed properties"""

		column = gtk.TreeViewColumn(title, gtk.CellRendererText()
			, text=columnId)
		column.set_resizable(True)
		column.set_sort_column_id(columnId)
		self.treeview_detalle_bodega.append_column(column)

	def OnSearchCliente(self, widget):
	    name_client = self.wTree.get_widget("entry_nombre_cliente").get_text()
	    id_client = self.wTree.get_widget("entry_identificacion_cliente").get_text()
	    database = 'pymes' #base de datos
	    user = 'noduxdev' #usuario de la base de datos postgres
	    password = 'noduxdev' #password de la base de datos postgres
	    host = '192.168.1.45' #ip host
	    conn = psycopg2.connect(database=database,user= user, password=password, host=host)
	    cur = conn.cursor()

	    if len(name_client) > 0:
		    cur.execute("SELECT * FROM party_party WHERE name LIKE %s",[name_client])
		    client = cur.fetchone()

		    cur.execute("SELECT * FROM party_address WHERE party=%s",[client[0]])
		    address = cur.fetchone()

		    cur.execute("SELECT * FROM party_contact_mechanism WHERE party=%s AND type='phone'",[client[0]])
		    contact = cur.fetchone()

		    if client[1]:
		        self.entry_id_cliente = self.wTree.get_widget("entry_id_cliente")
		        self.entry_id_cliente.set_text(client[1])

		    if client[4]:
		        self.entry_identificacion_cliente = self.wTree.get_widget("entry_identificacion_cliente")
		        self.entry_identificacion_cliente.set_text(client[4])

		    if address[11]:
		        self.entry_direccion_cliente = self.wTree.get_widget("entry_direccion_cliente")
		        self.entry_direccion_cliente.set_text(address[11])

		    if contact[5]:
		        self.entry_telefono_cliente = self.wTree.get_widget("entry_telefono_cliente")
		        self.entry_telefono_cliente.set_text(contact[5])

		    if client[1]:
		        self.entry_moneda = self.wTree.get_widget("entry_moneda")
		        self.entry_moneda.set_text(client[1])

		        self.entry_lista_precios = self.wTree.get_widget("entry_lista_precios")
		        self.entry_lista_precios.set_text(client[1])



	    elif len(id_client) > 0:
		    cur.execute("SELECT * FROM party_party WHERE vat_number = %s",[id_client])
		    client = cur.fetchone()

		    cur.execute("SELECT * FROM party_address WHERE party=%s",[client[0]])
		    address = cur.fetchone()

		    cur.execute("SELECT * FROM party_contact_mechanism WHERE party=%s AND type='phone'",[client[0]])
		    contact = cur.fetchone()

		    if client[1]:
		        self.entry_id_cliente = self.wTree.get_widget("entry_id_cliente")
		        self.entry_id_cliente.set_text(client[1])

		    self.entry_nombre_cliente = self.wTree.get_widget("entry_nombre_cliente")
		    self.entry_nombre_cliente.set_text(client[10])

		    if address[11]:
		        self.entry_direccion_cliente = self.wTree.get_widget("entry_direccion_cliente")
		        self.entry_direccion_cliente.set_text(address[11])

		    if contact[5]:
		        self.entry_telefono_cliente = self.wTree.get_widget("entry_telefono_cliente")
		        self.entry_telefono_cliente.set_text(contact[5])

		    if client[1]:
		        self.entry_moneda = self.wTree.get_widget("entry_moneda")
		        self.entry_moneda.set_text(client[1])

		        self.entry_lista_precios = self.wTree.get_widget("entry_lista_precios")
		        self.entry_lista_precios.set_text(client[1])

	def AddInvoiceListColumn(self, title, columnId):
	    """This function adds a column to the list view.
		First it create the gtk.TreeViewColumn and then set
		some needed properties"""

	    column = gtk.TreeViewColumn(title, gtk.CellRendererText()
			, text=columnId)
	    column.set_resizable(True)
	    column.set_sort_column_id(columnId)
	    self.treeview_detalle_de_factura.append_column(column)


	def check_password(self, password, hash_):
	    if not hash_:
	        return False
	    hash_method = hash_.split('$', 1)[0]
	    return getattr(self, 'check_' + hash_method)(password, hash_)

	def hash_sha1(self, password):
	    if isinstance(password, unicode):
	        password = password.encode('utf-8')
	    salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
	    hash_ = hashlib.sha1(password + salt).hexdigest()
	    return '$'.join(['sha1', hash_, salt])

	def check_sha1(self, password, hash_):
	    if isinstance(password, unicode):
	        password = password.encode('utf-8')
	    if isinstance(hash_, unicode):
	        hash_ = hash_.encode('utf-8')
	    hash_method, hash_, salt = hash_.split('$', 2)
	    salt = salt or ''
	    assert hash_method == 'sha1'
	    return hash_ == hashlib.sha1(password + salt).hexdigest()

class productDialog:
	"""This class is used to show wineDlg"""

	def __init__(self, codigo="", cantidad="", descripcion="", total=""):

		#setup the glade file
		self.gladefile = "facturador.glade"
		#setup the wine that we will return
		self.product = Product(codigo, cantidad, descripcion, total)

	def run(self):

		#load the dialog from the glade file
		self.wTree = gtk.glade.XML(self.gladefile, "factura_detalle")
		#Get the actual dialog widget
		self.dlg = self.wTree.get_widget("factura_detalle")
		#Get all of the Entry Widgets and set their text
		self.entry_codigo_producto = self.wTree.get_widget("entry_codigo_producto")
		self.entry_codigo_producto.set_text(self.product.codigo)

		self.entry_descripcion_producto = self.wTree.get_widget("entry_descripcion_producto")
		self.entry_descripcion_producto.set_text(self.product.descripcion)

		self.entry_importe = self.wTree.get_widget("entry_importe")
		self.entry_importe.set_text(self.product.price)

		self.entry_cantidad = self.wTree.get_widget("entry_cantidad")
		self.entry_cantidad.set_text(self.product.quantity)

		#run the dialog and store the response
		self.result = self.dlg.run()
		#get the value of the entry fields
		self.product.codigo = self.entry_codigo_producto.get_taxt()
		self.product.descripcion = self.entry_descripcion_producto.get_text()
		self.product.price = self.entry_importe.get_text()
		self.product.cantidad = self.entry_cantidad.get_text()

		#we are done with the dialog, destory it
		self.dlg.destroy()

		#return the result and the wine
		return self.result,self.product

class Invoice:

	def __init__(self,vendedor=""):

		self.vendedor = vendedor

	def getList(self):
		return [self.vendedor]

class Product:
    """This class represents all the wine information"""
    def __init__(self, codigo="", cantidad="", descripcion=""):
        self.codigo = codigo
        self.cantidad = cantidad
        self.descripcion = descripcion

	def getLista(self):
	    print "Ingresa a este metodo"
	    """This function returns a list made up of the
	    wine information.  It is used to add a wine to the
	    wineList easily"""
	    return [self.codigo, self.cantidad, self.descripcion]

class Bodega:
    def __init__(self, bodega="", cantidad=""):
        self.bodega = bodega
        self.cantidad = cantidad

	def getLista(self):
	    return [self.bodega, self.cantidad]

class PriceList:
    def __init__(self, precio=""):
        self.precio = precio

	def getLista(self):
	    return [self.precio]


if __name__ == "__main__":
	product = tpv()
	gtk.main()
