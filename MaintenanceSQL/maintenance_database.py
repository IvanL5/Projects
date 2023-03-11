import pandas as pd
import sqlite3 as db
import csv
import matplotlib.pyplot as plt

#Reads table data as string list from csv files in the working directory
#The following code is from:
#csv to string list: https://stackoverflow.com/questions/24662571/python-import-csv-to-list
#csv skip header: https://evanhahn.com/python-skip-header-csv-reader/


with open("Operator.csv") as f:
    reader = csv.reader(f)
    next(reader)
    Operator = list(reader)
    
with open("Equipment.csv") as f:
    reader = csv.reader(f)
    next(reader)
    Equipment = list(reader)
    
with open("Maintenance.csv") as f:
    reader = csv.reader(f)
    next(reader)
    MaintenanceLog = list(reader)

#Created a database class

class database:
    
    #Creates the database with the name provided in the arguement
    def __init__(self,name):
        
        self.conn = db.connect(name)
        self.cursor = self.conn.cursor()
    
    #Executes the SQL query provided in the arguement
    def execute(self,sql):
        
        self.cursor.execute(sql)
        
    #Executes the SQL query with each row from the source data
    def executemany(self,source,sql):
        
        self.cursor.executemany(sql,source)
        
    #Executes the SQL query provided in the arguement and prints it to the console.
    def query(self,sql):
        
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        for row in res:
            print(row)
           
    #Saves all changes made to the database
    def commit(self):
        
        self.conn.commit()
        
    #Closes the connection
    def close(self):
        
        self.conn.close()
        
#Creates the database called "maintenance.py"
maintenanceDB = database("maintenance.py")

#Executes SQL code to remove each of the table if it already exists in the database
maintenanceDB.cursor.execute("DROP TABLE IF EXISTS Operator;")
maintenanceDB.cursor.execute("DROP TABLE IF EXISTS Equipment;")
maintenanceDB.cursor.execute("DROP TABLE IF EXISTS MaintenanceLog;")

#Creates the Operator table
Operator_table = maintenanceDB.cursor.execute("""
        
    CREATE TABLE IF NOT EXISTS Operator(
        OperatorID INT,
        FName VARCHAR(50),
        LName VARCHAR(50),
        TrainingLevel VARCHAR(1),
        PRIMARY KEY(OperatorID)
    );
    
""")

#Creates the Equipment table
Equipment_table = maintenanceDB.cursor.execute("""
        
    CREATE TABLE IF NOT EXISTS Equipment(
        EquipmentID INT,
        Vendor VARCHAR(50),
        EquipmentType VARCHAR(50),
        Model VARCHAR(50),
        PRIMARY KEY(EquipmentID)
    );
    
""")

#Creates the maintenanceLog table
MaintenanceLog_table = maintenanceDB.cursor.execute("""

    CREATE TABLE IF NOT EXISTS MaintenanceLog(
        MaintenanceID INT,
        OperatorID INT,
        EquipmentID INT,
        MaintenanceType VARCHAR(50),
        Duration INT,
        MaintenanceDate DATE,
        MaintenanceLocation VARCHAR(50),
        PRIMARY KEY(MaintenanceID)
        FOREIGN KEY(OperatorID) REFERENCES Operator,
        FOREIGN KEY(EquipmentID) REFERENCES Equipment
    );
    
""")

#SQL code for populating the created tables with data
Operator_populate = "INSERT INTO Operator (OperatorID, FName, LName, TrainingLevel) VALUES(?, ?, ?, ?)"
Equipment_populate = "INSERT INTO Equipment (EquipmentID, Vendor, EquipmentType, Model) VALUES(?, ?, ?, ?)"
MaintenanceLog_populate = "INSERT INTO MaintenanceLog (MaintenanceID, OperatorID, EquipmentID, MaintenanceType, Duration, MaintenanceDate, MaintenanceLocation) VALUES(?, ?, ?, ?, ?, ?, ?)"

#Executes SQL code for populating each of the created tables with data from string lists
maintenanceDB.executemany(Operator, Operator_populate)
maintenanceDB.executemany(Equipment, Equipment_populate)
maintenanceDB.executemany(MaintenanceLog, MaintenanceLog_populate)

#Saves previous changes made to the database
maintenanceDB.commit()

#prints the Equipment table to the console
print("\n")
print("Equipment Table:")
maintenanceDB.query("""

    SELECT * FROM Equipment;

"""
)
print("\n")

#prints the Operator table to the console
print("Operator Table:")
maintenanceDB.query("""

    SELECT * FROM Operator;

"""
)
print("\n")

#prints the MaintenanceLog table to the console
print("MaintenanceLog Table:")
maintenanceDB.query("""

    SELECT * FROM MaintenanceLog;

"""
)
print("\n")

#Queries data from the database and visualizes that data in bar charts for Query 1, 2 and 3
#The following code is from:
#SQL Query to dataframe: https://datacarpentry.org/python-ecology-lesson/09-working-with-sql/index.html
#sqlite3 concatenate strings: https://www.sqlitetutorial.net/sqlite-string-functions/sqlite-concat/

# Query 1: How many maintenances were performed by each operator
df1 = pd.read_sql_query("""

    SELECT o.FName || ' ' || o.LName AS Name, COUNT(m.MaintenanceID) AS Count
    FROM Operator AS o LEFT JOIN MaintenanceLog AS m ON o.OperatorID = m.OperatorID
    GROUP BY o.OperatorID;

""", maintenanceDB.conn)

plt.bar(df1['Name'],df1['Count'])
plt.title('How many maintenances were performed by each operator?')
plt.xlabel('Name')
plt.ylabel('Count')
plt.show()

#Query 2: How many maintenances are associated to each equipment model?
df2 = pd.read_sql_query("""

    SELECT e.Model AS Model, COUNT(m.MaintenanceID) AS Count
    FROM Equipment AS e LEFT JOIN MaintenanceLog AS m ON e.EquipmentID = m.EquipmentID
    GROUP BY e.EquipmentID;

""", maintenanceDB.conn)

plt.bar(df2['Model'],df2['Count'])
plt.title('How many maintenances are associated to each equipment model?')
plt.xlabel('Model')
plt.ylabel('Count')
plt.show()

#Query 3: What is the average maintenance duration by operator training level?
df3 = pd.read_sql_query("""

    SELECT o.TrainingLevel AS Training_Level, ROUND(AVG(m.Duration),2) AS Average_Duration
    FROM Operator AS o INNER JOIN MaintenanceLog AS m ON o.OperatorID = m.OperatorID
    GROUP BY o.TrainingLevel
    
""", maintenanceDB.conn)

plt.bar(df3['Training_Level'],df3['Average_Duration'])
plt.title('What is the average maintenance duration by operator training level?')
plt.xlabel('Training Level')
plt.ylabel('Average Duration in Hours')
plt.show()

#Queries data from the database and prints that data to the console for queries 4 and 5

#Query 4: What Equipment Types has Brenden Lester worked on during maintenance?
print("What Equipment Types has Brenden Lester worked on during maintenance?")
maintenanceDB.query("""

    SELECT DISTINCT e.EquipmentType
    FROM Equipment AS e 
    INNER JOIN MaintenanceLog AS m ON e.EquipmentID = m.EquipmentID
    INNER JOIN Operator AS o ON m.OperatorID = o.OperatorID
    WHERE o.FName = 'Brenden' AND o.LName = 'Lester';
    

""")
print("\n")

#Query 5: List all preventative maintenances that were performed at Site 1 prior June
print("List all preventative maintenances that were performed at Site 1 prior June 2022")
maintenanceDB.query("""

    SELECT * FROM MaintenanceLog
    WHERE MaintenanceType = 'Preventative' AND MaintenanceDate < '2022-06-01' AND MaintenanceLocation = 'Site 1'

""")