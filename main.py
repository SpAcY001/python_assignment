import sqlite3
import sys

import pandas as pd

from modules import electric_product, electronic_product, product

if __name__ == "__main__":
    filename = "data.csv"
    df = pd.read_csv(filename)
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)

    print(df.to_string())
    objects: list[product] = []

    for index, row in df.iterrows():
        if row["type"] == "ELECTRIC":
            prod = electric_product(
                row["Product_id"], row["Name"], row["Price"], row["Stock"]
            )
            objects.append(prod)
        elif row["type"] == "ELECTRONIC":
            eprod = electronic_product(
                row["Product_id"], row["Name"], row["Price"], row["Stock"]
            )
            objects.append(eprod)
        else:
            print("error")
        # objects.append(prod)
    # firstproduct = objects[0]
    # print(f"product id is: {firstproduct.id},
    # product name is :{firstproduct.name}")
    conn = sqlite3.connect("product_inventory.db", check_same_thread=False)
    print("opened database successfully")
    newconn = sqlite3.connect("sales_transactions.db")
    print("opened sales database successfully")

    conn.execute(
        """CREATE TABLE IF NOT EXISTS INVENTORY
                ( ID INT PRIMARY KEY NOT NULL,
                NAME TEXT NOT NULL,
                PRICE REAL NOT NULL,
                STOCK INT,
                TYPE TEXT NOT NULL);"""
    )
    print("table created successfully")

    newconn.execute(
        """CREATE TABLE IF NOT EXISTS sales
                ( ID INT NOT NULL,
                TRANSACTION_DATE DATE DEFAULT CURRENT_TIMESTAMP,
                NAME TEXT NOT NULL,
                TOTAL_QUANTITY INT,
                PRICE REAL NOT NULL,
                PAYMENT_MODE TEXT NOT NULL);"""
    )
    print("table created successfully")
    # data = {"id": [4], "name": ["spacy"], "salary": [1600000]}
    # df = pd.DataFrame(data)

    table_name = "INVENTORY"
    df.to_sql(table_name, conn, if_exists="replace", index=False)

    def update_csv():
        df.to_csv("data.csv", index=False)

    def update_sql():
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    def csv_reader(file_name):
        for row in open(file_name, "r"):
            yield row

    # demonstrating yield, here using return will result in first line of the file only
    # open() returns a generator object, we can iterate through line by line.
    csv_gen = csv_reader("data.csv")
    row_count = 0
    for row in csv_gen:
        row_count += 1
    print(f"Row count is {row_count}")

    while True:
        print(
            " \n1.add product\n"
            "2.update product details\n"
            "3.search product \n"
            "4.delete product\n"
            "5.view product\n"
            "6.generate report\n"
            "7.#SALES#\n"
            "8.exit"
        )
        try:
            val = int(input("enter your choice  :"))
            if val >= 8:
                raise Exception
        except ValueError:
            print("\n\n enter only numeric values")
        except Exception:
            print("\n\n Enter correct values")
        if val == 1:
            while True:
                try:
                    id = int(input("enter product id :"))
                    break
                except Exception as e:
                    print("error occured {}, id should be numeric only !\n".format(e))
            if any(df["Product_id"] == id):
                print("product already exist.")
            else:
                name = input("enter product name :")
                while True:
                    try:
                        price = float(input("enter product price :"))
                        break
                    except Exception:
                        print("price should be int or float\n")

                while True:
                    try:
                        stock = int(input("enter available stock :"))
                        break
                    except Exception:
                        print("stock should be int ! \n")
                # type = input("enter product type :")
                print(
                    "\n select product type choose 1 or 2 :\n"
                    "1: product is of type Electric\n "
                    "2: product is of type Electronic"
                )
                while True:
                    try:
                        choice = int(input("enter you choice :"))
                        if choice >= 4 or choice <= 0:
                            raise Exception
                        break
                    except ValueError:
                        print("choice sohuld be int only\n")
                    except Exception:
                        print("choice should be numeric and between 1 to 3 only \n")
                if choice == 1:
                    new_obj = electric_product(id, name, price, stock)
                    objects.append(new_obj)
                    new_obj.add(df, filename, table_name, conn)
                elif choice == 2:
                    tnew_obj = electronic_product(id, name, price, stock)
                    objects.append(tnew_obj)
                    tnew_obj.add(df, filename, table_name, conn)
                else:
                    print("entered wrong choice")
        elif val == 2:
            up_id = int(
                input("enter the product id which you want to update details :")
            )
            if any(df["Product_id"] == up_id):
                print(
                    "\n what do you want to update :\n"
                    "1. modify price \n"
                    "2. update stock \n"
                    "3. change product name\n"
                )
                choice = int(input("enter your choice to update :"))
                temp_obj = product(id=10, name=None, price=10, stock=None)
                temp_obj.update_product(df, choice, objects, up_id, table_name, conn)
            else:
                print("product does not exist \n")

        elif val == 3:
            print(
                "\n on what basis do you want to search :\n"
                "1: based on product name \n"
                "2: based on product type \n"
                "3: based on price range \n"
            )
            choice = int(input("enter your choice :"))
            temp_obj = product(id=10, name=None, price=10, stock=None)
            temp_obj.search_product(choice, conn)

        elif val == 4:
            print("\n deleting from inventory where stock = 0 \n")
            temp_obj = product(id=10, name=None, price=10, stock=None)
            temp_obj.delete_inv(df, objects, table_name, conn)

        elif val == 5:
            print("\n displaying all the products available in the inventory \n")
            temp_obj = product(id=10, name=None, price=10, stock=None)
            temp_obj.view_product(conn, table_name)
        elif val == 6:
            print(
                "\n generate reports\n"
                "what kind of report do you want :\n"
                "1: report showing products low in stock \n"
                "2: report showing products with highest price \n"
            )
            choice = int(input("enter your choice :"))
            temp_obj = product(id=10, name=None, price=10, stock=None)
            print(df.to_string())
            temp_obj.gen_report(choice, df, conn)

        elif val == 7:
            print("\n SALES TRANSACTIONS \n")
            newcursor = newconn.cursor()
            sid = int(input("enter the product id which user wants to buy :"))
            if any(df["Product_id"] == sid):
                squant = int(input("enter the quantity :"))

                for index, row in df.iterrows():
                    if (
                        df.loc[index, "Product_id"] == sid
                        and squant <= df.loc[index, "Stock"]
                    ):
                        paymentmode = input("enter the payment mode :")
                        totalprice = objects[index].get_total_price(squant)
                        newcursor.execute(
                            "insert into sales"
                            "(ID,NAME,TOTAL_QUANTITY,PRICE,PAYMENT_MODE)"
                            "values (?,?,?,?,?)",
                            (
                                objects[index].id,
                                objects[index].name,
                                squant,
                                totalprice,
                                paymentmode,
                            ),
                        )
                        print("inserted successfully")
                        df.loc[index, "Stock"] = objects[index].stock - squant
                        df.to_csv(filename, index=False)
                        df.to_sql(table_name, conn, if_exists="replace", index=False)
                        newconn.commit()
                        break
            else:
                print("product does not exist \n")

        elif val == 8:
            print("you have exited from program")
            conn.close()
            newconn.close()
            sys.exit()
