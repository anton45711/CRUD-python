from flask import Flask
from flask import render_template,request, redirect,url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory


from datetime import datetime #tiempo de la foto
import os 

app= Flask(__name__)
app.secret_key="Develoteca"





mysql= MySQL()  

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistema'
mysql.init_app(app)

CARPETA= os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
   return send_from_directory(app.config['CARPETA'],nombreFoto)



@app.route('/')
def index():

    sql ="SELECT * FROM `empleados`;"
    conn= mysql.connect() #conexion a la base de datos
    cursor=conn.cursor() #almacenar todo lo que vamos a ejecutar
    cursor.execute(sql)  #ejecutar instruccion

    empleados=cursor.fetchall()
    print(empleados)

    conn.commit()       #terminar instruccion
    return render_template('empleados/index.html', empleados=empleados)

@app.route('/destroy/<int:id>')                 #funcion para eliminar
def destroy(id):

    conn= mysql.connect() #conexion a la base de datos
    cursor=conn.cursor() #almacenar todo lo que vamos a ejecutar
    
    
    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id) #selecciona la foto a eliminar
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0])) #actualizar foto
   

    cursor.execute("DELETE FROM empleados WHERE id=%s",(id))
    conn.commit()
    return redirect('/')






@app.route('/edit/<int:id>')
def edit(id):
    
    conn= mysql.connect() #conexion a la base de datos
    cursor=conn.cursor() #almacenar todo lo que vamos a ejecutar
    
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))  #ejecutar instruccion
    empleados=cursor.fetchall()
    conn.commit()       #terminar instrucciON
    
    return render_template('empleados/edit.html',empleados=empleados)  

@app.route('/update', methods=['POST'])
def update():                               #funcion para actualizar
    
    _nombre=request.form['txtNombre']      #traer todos los datos para actualizar
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']
    id=request.form['txtID']

    sql ="UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s ;"

    datos=(_nombre,_correo,id) #los valores se acomodan deacuerdo a la variable datos

    conn= mysql.connect()      #conexion a la base de datos
    cursor=conn.cursor()       #almacenar todo lo que vamos a ejecutar

    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S") #año,hora,minutos y segundos de la foto
    
    if _foto.filename!='':#crear un nuevo nombre diferente a la anterior para foto
       
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto) #evitar sabreescribir la foto anterior

        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id) #selecciona la foto a eliminar
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0])) #actualizar foto
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql,datos)  #ejecutar instruccion

    conn. commit()             #terminar instruccion
    
    return redirect('/')

@app.route('/create')                                                        #codigo para insertar 
def create():

   return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])                                       #codigo para modificar
def storage():

    _nombre=request.form['txtNombre']
    _correo=request.form['txtCorreo']
    _foto=request.files['txtFoto']


    if _nombre=='' or _correo=='' or _foto=='': #validaciones

        flash('Recuerda llenar los datos de los campos')
        return redirect(url_for('create'))


    now=datetime.now()
    tiempo=now.strftime("%Y%H%M%S") #año,hora,minutos y segundos de la foto
    if _foto.filename!='':#crear un nuevo nombre diferente a la anterior para foto
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto) #evitar sabreescribir la foto anterior



    sql ="INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s, %s, %s); "

    datos=(_nombre,_correo,nuevoNombreFoto) #los valores se acomodan deacuerdo a la variable datos

    conn= mysql.connect()      #conexion a la base de datos
    cursor=conn.cursor()       #almacenar todo lo que vamos a ejecutar
    cursor.execute(sql,datos)  #ejecutar instruccion
    conn. commit()             #terminar instruccion

    return redirect('/')#direccior al index
   


if __name__== '__main__':
    app.run(debug=True)
