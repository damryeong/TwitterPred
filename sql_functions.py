import pandas as pd

USER = "user"
PASS = "pass"
HOST = "127.0.0.1:0000"

#CREATE A DATABASE
def create_db(dbname):
	import MySQLdb as sql
	db = sql.connect(HOST,USER,PASS)
	cursor = db.cursor()
	sql = 'DROP DATABASE IF EXISTS '+ dbname
	cursor.execute(sql)
	sql = 'CREATE DATABASE ' + dbname +";"
	cursor.execute(sql)
	db.close()

#create_db("test")

#CREATE A TABLE WITH DESCRIPTION PROVIDED AS DICTIONARY
def create_table(dbname, tablename,desc):
	import MySQLdb as sql
	db = sql.connect(HOST,USER,PASS,dbname)
	cursor = db.cursor()
	cursor.execute('DROP TABLE IF EXISTS '+ tablename)
	temp_str = []
	for i in range(len(desc)):
		k,v = list(desc.items())[i]
		if(i!=len(desc)-1):
			temp_str.append(str(k)+" "+str(v)+",")
		else:
			temp_str.append(str(k)+" "+str(v))

	#temp_str[-1]  = temp_str[-1].translate({ord(','):None})
	sql = "CREATE TABLE "+tablename+"( "+' '.join(temp_str)+" );"
	print(sql)
	cursor.execute(sql)
	db.close()

#create_table("test","Persons",{"ID":"INT NOT NULL","NAME":"VARCHAR(30)","AGE":"INT","SEX":"CHAR(1)"})

#INSERT A VALUE IN SQL A LIST OF TUPLES
def insert_value(dbname,tablename,values,collist = None):
	import MySQLdb as sql
	db = sql.connect(HOST,USER,PASS,dbname)
	cursor = db.cursor()
	values = list(map(str,list(map(tuple,values))))
	values = ",".join(values)
	if(collist!=None):
		sql = "INSERT INTO " +tablename+" "+collist+" VALUES "+values+";"
	else:
		sql = "INSERT INTO "+tablename+" VALUES "+values+";"
	try:
	   # Execute the SQL command
	   cursor.execute(sql)
	   print("Executing the command")
	   # Commit your changes in the database
	   db.commit()
	except Exception as e:
	   # Rollback in case there is any error
	   print(e)
	   print("\nError! Rolling back")
	   db.rollback()
	db.close()

#insert_value("test","Persons",[[1,"Peter",10,"M"],[2,"Charlie",20,"M"]])

def read_table(dbname,tablename,condition = None):
	import MySQLdb as sql
	db = sql.connect(HOST,USER,PASS,dbname)
	cursor = db.cursor()
	if (condition!=None):
		sql = "SELECT * FROM "+tablename+" "+condition+";"
	else:
		sql = "SELECT * FROM "+tablename+";"
	try:
	   # Execute the SQL command
	   cursor.execute(sql)
	   results = list(cursor.fetchall())
	   #This returns a list of tuple  which will have tuple as a tuple in the list
	except Exception as e:
		print(e)
		print("\nError!")
	db.close()
	return results

# res  = read_table("test","Persons")
# print(res)

def modify_query(dbname,query = None):
	if(query==None):
		return
	else:
		import MySQLdb as sql
		db = sql.connect(HOST,USER,PASS,dbname)
		cursor = db.cursor()
	try:
	   # Execute the SQL command
	   cursor.execute(query)
	   # Commit your changes in the database
	   db.commit()
	except:
	   # Rollback in case there is any error
	   db.rollback()

	# disconnect from server
	db.close()


def pandas_to_sql(df,dbname,tablename):
	from sqlalchemy import create_engine
	engine = create_engine('mysql://'+USER+":"+PASS+"@"+HOST+'/'+dbname,echo=False)
	##df = pd.read_csv(filename)
	#Can add if_exists = 'replace' and index_label = 'id' etc too. Check documentation for the same.
	df.to_sql(tablename,con=engine,if_exists = 'append',index=False)

def sql_to_pandas(dbname,tablename,query,params=None):
	from sqlachemy import create_engine
	engine = create_engine('mysql://'+USER+":"+PASS+"@"+HOST+'/'+dbname,echo=False)
	#https://stackoverflow.com/questions/24408557/pandas-read-sql-with-parameters
	df  = pd.read_sql(query,params)
	return df