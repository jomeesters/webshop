__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"


from models import db, User, Product, Tag, Transaction, ProductTag
from whoosh.index import create_in
from whoosh.fields import Schema, ID, TEXT
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin
import os


def search(term):
    """
    Return a list of products with names or descriptions containing the given term (case-insensitive).
    """
    results = Product.select().where(
        (Product.name.ilike(f"%{term}%")) | (Product.description.ilike(f"%{term}%"))
    )
    return results


def list_user_products(user_id):
    """Return a list of products owned by the user with the given user_id."""
    user = User.get_by_id(user_id)
    return user.products


def list_products_per_tag(tag_id):
    """Return a list of products associated with the tag with the given tag_id."""
    tag = Tag.get_by_id(tag_id)
    return tag.tagged_products


def add_product_to_catalog(user_id, product_data):
    """
    Add a product to the catalog of the user with the given user_id.
    product_data should be a dictionary containing keys 'name', 'description', 'price', and 'quantity'.
    """
    user = User.get_by_id(user_id)
    product = Product.create(**product_data, owner=user)
    return product


def update_stock(product_id, new_quantity):
    """Update the stock quantity of the product with the given product_id to the given new_quantity."""
    product = Product.get_by_id(product_id)
    product.quantity = new_quantity
    product.save()


def purchase_product(product_id, buyer_id, quantity):
    """
    Record a purchase of the product with the given product_id by the user with the given buyer_id.
    The given quantity of the product will be deducted from the stock.
    """
    product = Product.get_by_id(product_id)
    buyer = User.get_by_id(buyer_id)

    if product.quantity < quantity:
        raise ValueError("Not enough stock available.")

    product.quantity -= quantity
    product.save()

    transaction = Transaction.create(buyer=buyer, product=product, quantity=quantity)
    return transaction


def remove_product(product_id):
    """Remove the product with the given product_id from the catalog."""
    product = Product.get_by_id(product_id)
    product.delete_instance()


def validate_product_data(product_data):
    """Validate product data before adding it to the database."""
    if not product_data["name"] or not product_data["description"]:
        raise ValueError("Product name and description must not be empty.")

    if product_data["price"] < 0 or product_data["quantity"] < 0:
        raise ValueError("Product price and quantity must be positive numbers.")


class WhooshIndex:
    def __init__(self, index_dir):
        schema = Schema(id=ID(unique=True, stored=True), name=TEXT, description=TEXT)
        self.index = create_in(index_dir, schema)

    def add_document(self, id, name, description):
        writer = self.index.writer()
        writer.add_document(id=str(id), name=name, description=description)
        writer.commit()

    def search(self, term):
        with self.index.searcher() as searcher:
            query_parser = MultifieldParser(["name", "description"], self.index.schema)
            query_parser.add_plugin(FuzzyTermPlugin())
            query = query_parser.parse(term)
            results = searcher.search(query)
            return [result["id"] for result in results]


def print_all_products():
    """Print all products in the database."""
    products = Product.select()
    for product in products:
        print(
            f"ID: {product.id}, Name: {product.name}, Description: {product.description}, Price: {product.price}, Stock: {product.quantity}"
        )

    print_all_products()


def populate_test_database():
    """Populate the database with example data for testing purposes.

    This function creates example data in the database for testing purposes. The created data includes users, products,
    tags, and transactions. The created users have ids 1,2 and 3. The created products are a Hoodie, Gloves, Socks,
    a Jacket and a Shirt. The Hoodie and the Gloves have tags 'Winter' and 'Clothing'. The Socks has tag 'Clothing'
    and the Jacket has tag 'Outerwear'. The created transactions include purchases of the Hoodie and the Gloves by user 1,
    and a purchase of the Socks by user 2.
    """

    # Create users
    user1 = User.create(name="Jo", address="Palingstraat 13", billing_info="Visa 1234")
    user2 = User.create(
        name="Lisa", address="Zoutstraat 55", billing_info="Mastercard 5678"
    )
    user3 = User.create(
        name="Max", address="Vestdijk 36", billing_info="American Express 6789"
    )

    # Create products
    product1 = Product.create(
        name="Hoodie",
        description="Warm and cozy",
        price=109.99,
        quantity=10,
        owner=user1,
    )
    product2 = Product.create(
        name="Gloves",
        description="Stylish and warm",
        price=29.99,
        quantity=15,
        owner=user1,
    )
    product3 = Product.create(
        name="Socks",
        description="Warm and stylish",
        price=14.99,
        quantity=25,
        owner=user3,
    )
    product4 = Product.create(
        name="Coat",
        description="Waterproof and warm",
        price=199.99,
        quantity=5,
        owner=user2,
    )
    product5 = Product.create(
        name="Shirt",
        description="Stylish and colourful",
        price=129.99,
        quantity=5,
        owner=user3,
    )

    # Create tags
    tag1, _ = Tag.get_or_create(name="Winter")
    tag2, _ = Tag.get_or_create(name="Clothing")
    tag3, _ = Tag.get_or_create(name="Outerwear")

    # Assign tags to products
    ProductTag.create(product=product1, tag=tag1)
    ProductTag.create(product=product1, tag=tag2)
    ProductTag.create(product=product1, tag=tag3)
    ProductTag.create(product=product2, tag=tag1)
    ProductTag.create(product=product2, tag=tag3)
    ProductTag.create(product=product3, tag=tag2)
    ProductTag.create(product=product4, tag=tag2)
    ProductTag.create(product=product4, tag=tag3)
    ProductTag.create(product=product5, tag=tag2)

    if not os.path.exists("index"):
        os.makedirs("index")

    # Index products for search
    index = WhooshIndex(index_dir="index")
    for product in Product.select():
        index.add_document(
            id=product.id, name=product.name, description=product.description
        )

    # Create transactions
    Transaction.create(buyer=user1, product=product1, quantity=1)
    Transaction.create(buyer=user1, product=product2, quantity=2)
    Transaction.create(buyer=user2, product=product3, quantity=5)


def init_database():
    """Initialize the database by creating tables for the models."""
    db.create_tables([User, Product, Tag, Transaction, ProductTag])


def clear_database():
    """Clear the database by dropping the tables of the models."""
    db.drop_tables([User, Product, Tag, Transaction, ProductTag])


def create_tables():
    """Create the tables for the models."""
    with db:
        db.create_tables([User, Product, Tag, Transaction, ProductTag])


def main():
    """Main function to run the Betsy Webshop application."""
    while True:
        print("\nBetsy Webshop Menu")
        print("1. Search for products")
        print("2. List user products")
        print("3. List products per tag")
        print("4. Add product to catalog")
        print("5. Update stock")
        print("6. Purchase product")
        print("7. Remove product")
        print("8. Exit")

        choice = input("Enter the number of your choice: ").strip()

        # Validate user input
        try:
            choice = int(choice)
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 8.")
            continue

        print(f"User input: {choice}")

        # Process user choice
        if choice == 1:
            term = input("Enter a search term: ")
            results = search(term)
            for product in results:
                print(
                    f"Product name: {product.name}, Description: {product.description}, Price: {product.price}, Quantity: {product.quantity}"
                )
        elif choice == 2:
            user_id = int(input("Enter the user ID: "))
            products = list_user_products(user_id)
            for product in products:
                print(
                    f"Product name: {product.name}, Description: {product.description}, Price: {product.price}, Quantity: {product.quantity}"
                )
        elif choice == 3:
            try:
                tag_id = int(input("Enter the tag ID: "))
                product_tags = list_products_per_tag(tag_id)
                if product_tags:
                    for product_tag in product_tags:
                        product = product_tag.product
                        print(
                            f"Product name: {product.name}, Description: {product.description}, Price: {product.price}, Quantity: {product.quantity}"
                        )
                else:
                    print("No products found with the given tag ID. Please try again.")
            except ValueError:
                print("Invalid tag ID. Please enter a valid integer.")
            except Tag.DoesNotExist:
                print("The specified tag ID does not exist. Please try again.")
            except Exception as e:
                print(f"An error occurred: {e}. Please try again.")

        elif choice == 4:
            user_id = int(input("Enter the user ID: "))
            name = input("Enter the product name: ")
            description = input("Enter the product description: ")
            price = float(input("Enter the product price: "))
            quantity = int(input("Enter the product quantity: "))
            product_data = {
                "name": name,
                "description": description,
                "price": price,
                "quantity": quantity,
            }
            add_product_to_catalog(user_id, product_data)
            print(f"Product {name} added to the catalog of user {user_id}.")

        elif choice == 5:
            product_id = int(input("Enter the product ID: "))
            new_quantity = int(input("Enter the new quantity: "))
            update_stock(product_id, new_quantity)
            print(
                f"The stock for product {product_id} has been successfully updated by {new_quantity} units."
            )

        elif choice == 6:
            product_id = int(input("Enter the product ID: "))
            buyer_id = int(input("Enter the buyer ID: "))
            quantity = int(input("Enter the quantity to purchase: "))
            purchase_product(product_id, buyer_id, quantity)
            print(
                f"You have successfully purchased {quantity} units of product {product_id}."
            )

        elif choice == 7:
            product_id = int(input("Enter the product ID: "))
            remove_product(product_id)
            print(
                f"Product {product_id} has been successfully removed from the catalog."
            )

        elif choice == 8:
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 8.")


if __name__ == "__main__":
    clear_database()
    init_database()
    populate_test_database()
    main()
