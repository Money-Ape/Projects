import mysql.connector as im_typing

def money_ape():

    print("\033[1;93m __  __                                _          \033[0m")
    print("\033[1;93m|  \\/  | ___  _ __   ___ _   _        / \\   _ __   ___ \033[0m")
    print("\033[1;93m| |\\/| |/ _ \\| '_ \\ / _ \\ | | |_____ / _ \\ | '_ \\ / _ \\\033[0m")
    print("\033[1;93m| |  | | (_) | | | |  __/ |_| |_____/ ___ \\| |_) |  __/\033[0m")
    print("\033[1;93m|_|  |_|\\___/|_| |_|\\___|\\__, |    /_/   \\_\\ .__/ \\___|\033[0m")
    print("\033[1;93m                         |___/             |_|\033[0m")
    print("\033[1;32m\n                    Github : Money-Ape\033[0m {verison : 1.1}\n")
money_ape()

usr=input("Enter SQL username : ")
passcode=input("Enter SQL password : ")
con=im_typing.connect(
    host="localhost",
    user=usr,
    passwd=passcode
    .format('{}','{}')
)
cur=con.cursor()

def create_schema():
    database=input("Enter databse name : ")
    q=(f"create schema {database}")
    cur.execute(q)

def create_table():
    display=("show databases")
    cur.execute(display)
    for database in cur:
        print(database)
    exist_schema=input("Enter Existing database name : ")
    q1=(f"use {exist_schema}")
    cur.execute(q1)
    
    print("\nOnly one column can be affected..!",
          "\nFurther options will be provided\n"
    )
    tb_name=input("Enter the New Table Name : ")
    f_name=input(f"Enter Field Name for {tb_name} table : ")
    sqlstr_data={
        "integer":"int",
        "alpha":"char",
        "var-char":"varchar",
        "large_int":"bigint",
        "decimal":"float"
    }
    sqlstr_list=[
        "\ninteger => Number",
        "alpha => alphabet",
        "var-char => various character",
        "large_int => larger integer",
        "decimal => integer with decimal places\n",
    ]
    for list in sqlstr_list:
        print(list)
    sqlstr_input=input("Field data type : ")
    sqlrange=int(input(f"Enter the range of {sqlstr_input} : "))
    f_data_type = sqlstr_data[sqlstr_input]+f"({sqlrange})"
    tb_st=(f"create table {tb_name}({f_name} {f_data_type})")
    cur.execute(tb_st)
    con.commit()
    option=input(f"Do you want to add more columns to {tb_name} \n(y/n) : ")
    if option=="y":
        columns=int(input("Enter the number of columns : "))
        while (True):
            structure=0
            for structure in range(columns):
                structure+=1
                print(structure)
                f_name=input(f"Enter Field Name for {tb_name} table : ")
                for list in sqlstr_list:
                    print(list)
                sqlstr_input=input("Field data type : ")
                sqlrange=int(input(f"Enter the range of {sqlstr_input} : "))
                f_data_typ = sqlstr_data[sqlstr_input]+f"({sqlrange})"
                str_col=(f"alter table {tb_name} add {f_name} {f_data_typ}")
                cur.execute(str_col)
                con.commit()
            break
    else:
        None

def display_schema():
    display=("show databases")
    cur.execute(display)
    for database in cur:
        print(database)
        
    if cur:
        while display:
            option=input("\nDo you want to Display Tables from Databases (y/n) : ")
            if (option=="y"):
                databases=input("Enter the Existing Database name : ")
                display=(f"show tables from {databases}\n")
                cur.execute(display)
                for table in cur:
                    print(table)
                       
            elif (option=="n"):
                ask=input("Describe the Structure of the given Table (y/n) : ")
                if (ask=="y"):
                    databases=input("Enter the Existing Database name : ")
                    q1=(f"use {databases}")
                    display=(f"show tables from {databases}\n")
                    cur.execute(display)
                    for table in cur:
                        print(table)
                    def table_structure():
                        tb_name=input("\nEnter the Table Name : ")
                        q2=(f"desc {tb_name}")
                        cur.execute(q1)
                        cur.execute(q2)
                        dt=cur.fetchall()
                        for structure in dt:
                            print(structure)
                    table_structure()
                    
                else:
                    break
            else:
                break
    else:
        None

def display_table():
    display_s=("show databases")
    cur.execute(display_s)
    for database in cur:
        print(database)
    
    D_tables=input("\nEnter the Existing database name : ")
    display_t=(f"\nshow tables from {D_tables}")
    cur.execute(display_t)
    for table in cur:
        print(table)
    option=input("\nDo you want to display the records for Particular Table (y/n) : ")
    if option=="y":
        tb_name=input("Enter the Existing Table name : ")
        rec=(f"\nselect * from {D_tables}.{tb_name}")
        cur.execute(rec)
        dr=cur.fetchall()
        for records in dr:
            print(records)
    else:
        None

def update_table():
    while update_table:
        display=("show schemas")
        cur.execute(display)
        for database in cur:
            print(database)
        
        exist_schema=input("\nEnter Existing database name : ")
        qt=(f"show tables from {exist_schema}")
        cur.execute(qt)
        for tables in cur:
            print(tables)
            
        use=(f"use {exist_schema}")
        cur.execute(use)
        
        tb_name=input("Enter the Existing Table name : ")
        qts=(f"desc {tb_name}")
        qtv=(f"select * from {tb_name}")
        cur.execute(qts)
        dt=cur.fetchall()
        cur.execute(qtv)
        dt2=cur.fetchall()
        while True:
            for table_s in dt:
                print(table_s)
            for table_v in dt2:
                print(table_v)
            break
            
        f_name=input("Enter the Existing Field Name : ")
        update_changes=input("Enter the new value : ")
        f1_name=input(f"Enter another field which related to {f_name} : ")
        data=input(f"Enter {f1_name} value : ")
        
        cur.execute(f"update {tb_name} set {f_name}='{update_changes}' where {f1_name}='{data}'")
        con.commit()
            
        break


op=[1,2,3,4,5,6]
while op:
    print("\n1 => Create a New Database",
          "\n2 => Update the Table",
          "\n3 => Display Databases",
          "\n4 => Display Tables",
          "\n5 => Create a New Table",
          "\n6 => Exit"
    )
    
    go=int(input("\nEnter your option : "))
    if op[0]==go:
        create_schema()
    elif op[1]==go:
        update_table()
    elif op[2]==go:
        display_schema()
    elif op[3]==go:
        display_table()
    elif op[4]==go:
        create_table()
    elif op[5]==go:
        quit()
    else:
        print("invalid choice..!")
            
con.close()
