import csv
from threading import Thread


class product:
    def __init__(self, id, name, price, stock):
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("Price must be a non-negative integer or float")
        if not isinstance(id, int) or id < 0:
            raise ValueError("ID must be a non-negative integer")
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def add(self, df, filename, table_name, conn):
        df.loc[len(df.index)] = [self.id, self.name, self.price, self.stock, self.type]
        row = [self.id, self.name, self.price, self.stock, self.type]
        with open(filename, "a") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(row)
        df.tail(1).to_sql(table_name, conn, if_exists="append", index=False)
        # conn.close()

    def view_product(self, conn, table_name):
        cursor = conn.cursor()
        sql_query = f"select * from {table_name}"
        cursor.execute(sql_query)
        op = cursor.fetchall()
        for row in op:
            print(row)
        cursor.close()

    def get_total_price(self):
        return self.price * self.stock

    def update_product(self, df, choice, objects, up_id, table_name, conn):
        for index, row in df.iterrows():
            if row["Product_id"] == up_id:
                if choice == 1:
                    newprice = float(input("enter new price :"))

                    objects[index].price = newprice
                    # row["Price"] = objects[index].price
                    df.loc[index, "Price"] = objects[index].price
                    break
                elif choice == 2:
                    newstock = int(input("enter the new stock"))
                    objects[index].stock = newstock
                    # row["Stock"] = objects[index].stock
                    df.loc[index, "Stock"] = objects[index].stock
                    break
                elif choice == 3:
                    newname = input("enter new product name :")
                    objects[index].name = newname
                    print(objects[index].name)
                    # row["Name"] = objects[index].name
                    df.loc[index, "Name"] = objects[index].name
                    # print(row["Name"])
                    break
        # df.to_csv(filename, index=False)
        # df.to_sql(table_name, conn, if_exists="replace", index=False)

        csv_thread = ThreadWithReturnValue(target=update_csv, args=(df,))
        sql_thread = ThreadWithReturnValue(
            target=update_sql, args=(df, table_name, conn)
        )
        csv_thread.start()
        sql_thread.start()
        csv_thread.join()
        sql_thread.join()
        print("updated successfully using multi threading\n")

    def search_product(self, choice, conn):
        if choice == 1:
            pname = input("enter product name :")
            op = conn.execute("select * from INVENTORY where Name=?", (pname,))
            for row in op:
                print(row)
        elif choice == 2:
            ptype = input("enter product type(ELECTRIC OR ELECTRONIC) :")
            cursor = conn.cursor()
            cursor.execute("select * from INVENTORY where type=?", (ptype,))
            op = cursor.fetchall()
            for row in op:
                print(row)
        elif choice == 3:
            prange1 = float(input("enter lower limit :"))
            prange2 = float(input("enter higher limit :"))
            cursor = conn.cursor()
            cursor.execute(
                "select * from INVENTORY where Price between ? and ?",
                (prange1, prange2),
            )
            op = cursor.fetchall()
            for row in op:
                print(row)
            cursor.close()

    def delete_inv(self, df, objects, table_name, conn):
        templist = []
        for index, row in df.iterrows():
            if row["Stock"] == 0:
                df = df.drop(index)
                templist.append(objects[index])
                df.to_csv("data.csv", index=False)
                df.to_sql(table_name, conn, if_exists="replace", index=False)
        for i in templist:
            del i
        print(df.to_string())

    def gen_report(self, choice, df, conn):
        if choice == 1:
            newfile = "lowstock.csv"
            tstock = int(input("enter the base stock value :"))
            fields = ["prod_id", "name", "price", "stock", "type"]
            row_toadd = []
            for index, row in df.iterrows():
                if row["Stock"] <= tstock:
                    row_toadd.append(
                        [
                            row["Product_id"],
                            row["Name"],
                            row["Price"],
                            row["Stock"],
                            row["type"],
                        ]
                    )
            with open(newfile, "w") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(fields)
                csvwriter.writerows(row_toadd)
        elif choice == 2:
            newfile2 = "highprice.csv"
            cursor = conn.cursor()
            cursor.execute("select AVG(Price) from inventory")
            avg_value = cursor.fetchone()[0]
            cursor.close()
            print(f"the avg value of product prices is {avg_value} \n")
            fields2 = ["prod_id", "name", "price", "stock", "type"]
            row_toadd2 = []
            for index, row in df.iterrows():
                if row["Price"] >= avg_value:
                    row_toadd2.append(
                        [
                            row["Product_id"],
                            row["Name"],
                            row["Price"],
                            row["Stock"],
                            row["type"],
                        ]
                    )
            with open(newfile2, "w") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(fields2)
                csvwriter.writerows(row_toadd2)


class electric_product(product):
    def __init__(self, id, name, price, stock):
        self.type = "ELECTRIC"
        product.__init__(self, id, name, price, stock)

    def get_total_price(self, quant):
        return self.price * quant


class electronic_product(product):
    def __init__(self, id, name, price, stock):
        self.type = "ELECTRONIC"
        product.__init__(self, id, name, price, stock)

    def get_total_price(self, quant):
        return self.price * quant


class ThreadWithReturnValue(Thread):
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None
    ):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def update_csv(df):
    df.to_csv("data.csv", index=False)


def update_sql(df, table_name, conn):
    df.to_sql(table_name, conn, if_exists="replace", index=False)
