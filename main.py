import csv
import requests
from bs4 import BeautifulSoup
# Python Version 3.10


class Product:

    def __int__(self):
        self.url = None
        self.name = None
        self.price = None
        self.sku = None
        self.categories = []
        self.description = None
        self.image_url = None

    def __str__(self):
        return f"Product - {self.name}, {self.url}, {self.price}, {self.sku}, {self.categories}, " \
               f"{self.description}, {self.image_url}"



class Scrapper:

    def __init__(self, url):
        self.url = url

    def scrap_content(self):
        response = requests.get(self.url)
        content = BeautifulSoup(response.text, "html.parser")
        product_content = content.find_all("ul", class_="products").pop()
        products = product_content.find_all("li", class_="product")
        self.process_products(products)

    def process_products(self, products):
        all_products = []
        print("Processing products...")
        for product in products:
            product_image = product.find("img")["src"]
            product_price = product.find("span", class_="price").text
            product_main_details = product.find("h3", class_="woocommerce-loop-product__title")
            product_name = product_main_details.find("a").text
            product_url = product_main_details.find("a")["href"]
            details = self.get_product_details(product_url)
            details["name"] = product_name
            details["url"] = product_url
            details["image_url"] = product_image
            details["price"] = product_price
            p = self.create_product(details)
            all_products.append(p)
        self.save_to_csv(all_products)
        print("Process complete.")

    def get_product_details(self, product_url):
        response = requests.get(product_url)
        content = BeautifulSoup(response.text, "html.parser")
        product_content = content.find("div", class_="product")
        product_summary = product_content.find("div", class_="product-summary")
        summary = product_summary.find("div", class_="summary")
        name = summary.find("h1", class_="product_title").text
        product_meta = product_summary.find("div", class_="product_meta")
        sku = product_meta.find("span", class_="sku").text
        categories_content = product_meta.find("span", class_="posted_in").find_all("a")
        categories = []
        for cat in categories_content:
            category = cat.text
            categories.append(category)
        return {
            "description": name,
            "sku": sku,
            "categories": categories
        }

    def create_product(self, details):
        product = Product()
        product.name = details.get("name")
        product.url = details.get("url")
        product.price = details.get("price")
        product.sku = details.get("sku")
        product.categories = details.get("categories", [])
        product.description = details.get("description")
        product.image_url = details.get("image_url")
        return product

    def save_to_csv(self, products):
        print("Saving products to csv")
        with open("product_details.csv", mode="w") as csv_file:
            writer = csv.writer(csv_file, quotechar='"')
            header = ["Name", "URL", "Price", "SKU", "Categories", "Description", "Image URL"]
            writer.writerow(header)
            for p in products:
                writer.writerow([p.name, p.url, p.price, p.sku, p.categories, p.description, p.image_url])

    def run(self):
        print(f"Running scrapper for url {self.url}")
        self.scrap_content()


if __name__ == '__main__':
    url = "https://www.copunderdog.com/product-category/sneakers/"
    scrapper = Scrapper(url)
    scrapper.run()
