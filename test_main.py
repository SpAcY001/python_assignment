import sqlite3

import pandas as pd
import pytest

from main import electronic_product, product


# Fixture for setting up the initial state for testing
@pytest.fixture
def setup():
    filename = "test_data.csv"
    df = pd.DataFrame(columns=["Product_id", "Name", "Price", "Stock", "type"])
    table_name = "test_INVENTORY"
    conn = sqlite3.connect("test_inventory.db")

    conn.execute(
        """CREATE TABLE IF NOT EXISTS test_INVENTORY
            (Product_id  NOT NULL,
             Name TEXT NOT NULL,
             Price REAL NOT NULL,
             Stock INT,
             type TEXT NOT NULL);"""
    )

    yield df, filename, table_name, conn

    # Clean up resources
    conn.close()


def test_add_method(setup):
    df, filename, table_name, conn = setup

    prod = electronic_product(1, "Test Product", 10.0, 20)

    # Call the add method
    prod.add(df, filename, table_name, conn)
    df.tail(1).to_sql(table_name, conn, if_exists="append", index=False)

    assert len(df) == 1
    assert df.loc[0, "Product_id"] == 1
    assert df.loc[0, "Name"] == "Test Product"
    assert df.loc[0, "Price"] == 10.0
    assert df.loc[0, "Stock"] == 20
    assert df.loc[0, "type"] == "ELECTRONIC"


def test_view_product_method(setup, capsys):
    df, filename, table_name, conn = setup

    prod = electronic_product(id=10, name=None, price=10, stock=None)

    prod.view_product(conn, table_name)

    captured = capsys.readouterr()
    assert "(1, 'Test Product', 10.0, 20, 'ELECTRONIC')\n" in captured.out


def test_price():
    with pytest.raises(
        ValueError, match="Price must be a non-negative integer or float"
    ):
        product(1, "Test Product", -10, 20)


def test_id_with_zero_or_negative():
    with pytest.raises(ValueError, match="ID must be a non-negative integer"):
        electronic_product(-1, "Test Product", 10.0, 20)


# def test_coverage():
#     pytest.main(["--cov=.", "--cov-report=html"])


if __name__ == "__main__":
    pytest.main()
