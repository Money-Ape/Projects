import pickle
import random
import mysql.connector as ms

u=input("Enter My_SQL Username : ")
p=input("Enter your My_SQL Password : ")
con=ms.connect(
    host="localhost",
    user=u ,
    passwd=p,
    database="atm_machine"
    .format('{}','{}')
)
cur=con.cursor()

print("========================================================")

print("                        Welcome")
print("========================================================")

# In this project i had used my usbdrive location. for your own, change the location of file wherever you want to execute.

def login():

    while usr=="n":
        atm_pin=int(input("Enter your ATM PIN : "))
        check_exists=("select exists(select * from user_data where ATM_PIN={}".format(atm_pin))
        
        if check_exists:
            ac_name=input("Enter your Account Name : ")
            check_again=("select exists(select * from user_data where Username='{}' ".format(ac_name))

            if ac_name:

                def cash_withdraw():
                    atm_pin=int(input("Enter your ATM PIN : "))
                    money=int(input("Enter amount you would like to WITHDRAW : "))
                    bal=("select Account_Balance from user_data where ATM_PIN={} ".format(atm_pin))
                    bal_left=("update user_data set Account_Balance=Account_Balance-{} where ATM_PIN={}".format(money,atm_pin))
                    cur.execute(bal_left)
                    con.commit()
                    
                def check_balance():
                    ac_num=int(input("Enter your Account number : "))
                    bal=("select Account_Balance from user_data where Account_num={} ".format(ac_num))
                    cur.execute(bal)
                    am=cur.fetchall()
                    print(am)

                while True:
                    print(
                        "\n1 => Banking(cash withdrawl)",
                        "\n2 => Check Balance",
                        "\n3 => EXIT"
                    )
                    ch=input("Enter Choice : ")
                    if ch=="1":
                        cash_withdraw()
                                                    
                    elif (ch=="2"):
                        check_balance()

                    else:
                        exit()

            else:
                print("Oops.! username not found.!")
                
        else:
            print("you entered an incorrect PIN.!")


def option_1():
    atm_pin=int(input("Enter 4 digit PIN : "))
    a1=[0, 1, 2, 3]

    if (len(str(atm_pin))==len(a1)):
        print("========================================================")
        print("                  Welcome to ATM")
        print("========================================================")

        print("Make sure password will be 8 character or more than",)
        password=input("setup your password : ")
        print("==============# Remember your Password #================")
        print("Password : ",password)
        print("========================================================")

        b1=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        mob_no=int(input("Enter 10 digit mobile number : "))
        
        if (len(str(mob_no))==len(b1)):
            print(" :-) Moblie no. : ",mob_no)
            username=input("Enter your Name : ")

            v=input("Details that you had mentioned, are correct.? (y/n) : ")
            if v=="y":
                num1="0123456789"
                num2="9876543210"
                all=num1+num2
                length=12
                account="".join(random.sample(all,length))
                print("================# Remember your Ac_no #================= ")
                print("Account no.: ", account)
                acc_balance=5000
                print("You recieved 5000 cash prize for opening new account")
                
                sqlquery=("insert into user_data values('{}',{},{},'{}',{},{})".format(username, mob_no, atm_pin, password, account, acc_balance))
                cur.execute(sqlquery)
                con.commit()                


                                                  # To Sign-up and Sign-in in an Account.


op=[1,2,3]

while op:
    print(
        "1 to Sign-up/Login",
        "\n2 to Check in System Users Account Data",
        "\n3 to Exit"
    )
    print("========================================================")
    go=int(input("Enter your choice : "))

    if go==op[0]:
        usr=input("New User(create an account) y/n : ")
        if usr=="y":
            option_1()
            
        else: 
            login()

    elif go==op[1]:
        def auth():
            f_ad=open("D:/ATM_Project/ATM_Records_admin.txt","rb") # you have to create your own binary file to hold password for authentication.
            ad=input("Verify Athourisation : ")
            print("========================================================")
            Line=pickle.load(f_ad)
            
            if ad in Line:
                auth=("select * from user_data")
                cur.execute(auth)
                v=cur.fetchall()
                for row in v:
                    print(
                        "Username : ",row[0],
                        "\nMobile num : ",row[1],
                        "\nATM PIN : ",row[2],
                        "\nATM Password : ",row[3],
                        "\nAccount num : ",row[4],
                        "\nAccount Balance : ",row[5]
                    )
                    print("========================================================")
                    
            else:
                quit()

            f_ad.close()
            
        auth()

    else:
        quit()
con.close()
