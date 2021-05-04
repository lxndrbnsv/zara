import datetime
import traceback

import pymysql

import config as cfg


class WriteResultsToDB:
    def __init__(self, results):
        connection = pymysql.connect(
            host=cfg.db_data["host"],
            user=cfg.db_data["user"],
            password=cfg.db_data["password"],
            db=cfg.db_data["db"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

        for result in results:
            try:
                print(result["name"], flush=True)
                ts = datetime.datetime.now()

                shop_id = 5
                product_ref = result["ref"]
                parsed = ts
                updated = ts
                name = result["name"]
                available = 1
                brand = "Zara"
                art = result["art"]
                current_price = result["price"]
                currency = "EUR"
                description = result["description"]
                material = result["materials"]
                dimensions = None
                images = ", ".join(result["pictures"])
                img_main = result["pictures"][0]
                img_additional = ", ".join(result["pictures"])
                category = result["cat_id"]
                color = result["color"]
                sizes = result["sizes"]

                with connection.cursor() as cursor:
                    insert_query = (
                        "INSERT INTO parsed_products ("
                        "shop_id, product_ref, parsed, updated, name,"
                        " available, brand, art, current_price, currency,"
                        " description, material, dimensions,"
                        " images, img_main, img_additional, category, color, size)"
                        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,"
                        " %s, %s, %s, %s, %s, %s, %s, %s);"
                    )
                    insert_values = (
                        shop_id,
                        product_ref,
                        parsed,
                        updated,
                        name,
                        available,
                        brand,
                        art,
                        current_price,
                        currency,
                        description,
                        material,
                        dimensions,
                        images,
                        img_main,
                        img_additional,
                        category,
                        color,
                        sizes,
                    )
                    cursor.execute(insert_query, insert_values)

                    connection.commit()
            except IndexError:
                pass
            except Exception:
                pass

            connection.close()

        print("Written!", flush=True)
