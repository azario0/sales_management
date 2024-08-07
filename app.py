import customtkinter as ctk
import csv
from datetime import datetime
import os
from tkinter import messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SalesMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sales Monitor")
        self.geometry("800x600")

        self.products = self.load_products()
        self.orders = self.load_orders()

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.products_tab = self.tabview.add("Products")
        self.orders_tab = self.tabview.add("Orders")
        self.history_tab = self.tabview.add("Order History")

        self.setup_products_tab()
        self.setup_orders_tab()
        self.setup_history_tab()

        self.update_product_list()

    def setup_products_tab(self):
        frame = ctk.CTkFrame(self.products_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Add Product section
        add_frame = ctk.CTkFrame(frame)
        add_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(add_frame, text="Add New Product", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        ctk.CTkLabel(add_frame, text="Product Name:").grid(row=1, column=0, padx=5, pady=5)
        self.product_name = ctk.CTkEntry(add_frame)
        self.product_name.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(add_frame, text="Price (DZD):").grid(row=2, column=0, padx=5, pady=5)
        self.product_price = ctk.CTkEntry(add_frame)
        self.product_price.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(add_frame, text="Quantity:").grid(row=3, column=0, padx=5, pady=5)
        self.product_quantity = ctk.CTkEntry(add_frame)
        self.product_quantity.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkButton(add_frame, text="Add Product", command=self.add_product).grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Update/Delete Product section
        update_frame = ctk.CTkFrame(frame)
        update_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(update_frame, text="Update/Delete Product", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        ctk.CTkLabel(update_frame, text="Select Product:").grid(row=1, column=0, padx=5, pady=5)
        self.update_product_select = ctk.CTkComboBox(update_frame, values=[p['name'] for p in self.products])
        self.update_product_select.grid(row=1, column=1, padx=5, pady=5)
        self.update_product_select.bind("<<ComboboxSelected>>", self.on_product_select)

        ctk.CTkLabel(update_frame, text="New Price (DZD):").grid(row=2, column=0, padx=5, pady=5)
        self.update_price = ctk.CTkEntry(update_frame)
        self.update_price.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(update_frame, text="New Quantity:").grid(row=3, column=0, padx=5, pady=5)
        self.update_quantity = ctk.CTkEntry(update_frame)
        self.update_quantity.grid(row=3, column=1, padx=5, pady=5)

        update_button = ctk.CTkButton(update_frame, text="Update Product", command=self.update_product)
        update_button.grid(row=4, column=0, padx=5, pady=5)

        delete_button = ctk.CTkButton(update_frame, text="Delete Product", command=self.delete_product, fg_color="red", hover_color="darkred")
        delete_button.grid(row=4, column=1, padx=5, pady=5)

        # Product List
        list_frame = ctk.CTkFrame(frame)
        list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(list_frame, text="Product List", font=("Arial", 16, "bold")).pack(pady=5)
        
        self.product_list = ctk.CTkTextbox(list_frame, height=200)
        self.product_list.pack(fill="both", expand=True, padx=5, pady=5)

        self.update_product_list()

    def delete_product(self):
        selected_product = self.update_product_select.get()
        
        if selected_product:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the product '{selected_product}'?")
            if confirm:
                self.products = [p for p in self.products if p['name'] != selected_product]
                self.save_products()
                self.update_product_list()
                self.update_price.delete(0, 'end')
                self.update_quantity.delete(0, 'end')
                messagebox.showinfo("Success", f"Product '{selected_product}' has been deleted")
        else:
            messagebox.showerror("Error", "Please select a product to delete")

    def on_product_select(self, event):
        selected_product = self.update_product_select.get()
        product = next((p for p in self.products if p['name'] == selected_product), None)
        if product:
            self.update_price.delete(0, 'end')
            self.update_price.insert(0, str(product['price']))
            self.update_quantity.delete(0, 'end')
            self.update_quantity.insert(0, str(product['quantity']))
    
    def setup_orders_tab(self):
        frame = ctk.CTkFrame(self.orders_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.order_items = []

        ctk.CTkLabel(frame, text="Select Product:").grid(row=0, column=0, padx=5, pady=5)
        self.product_select = ctk.CTkComboBox(frame, values=[p['name'] for p in self.products])
        self.product_select.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=5)
        self.order_quantity = ctk.CTkEntry(frame)
        self.order_quantity.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkButton(frame, text="Add to Order", command=self.add_to_order).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.order_list = ctk.CTkTextbox(frame, height=200)
        self.order_list.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.total_label = ctk.CTkLabel(frame, text="Total: 0 DZD")
        self.total_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        ctk.CTkButton(frame, text="Place Order", command=self.place_order).grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def setup_history_tab(self):
        frame = ctk.CTkFrame(self.history_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(frame, text="Search by Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        self.search_date = ctk.CTkEntry(frame)
        self.search_date.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(frame, text="Search", command=self.search_orders).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.order_history = ctk.CTkTextbox(frame, height=400)
        self.order_history.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.update_order_history()

    def add_product(self):
        name = self.product_name.get()
        price = self.product_price.get()
        quantity = self.product_quantity.get()

        if name and price and quantity:
            self.products.append({"name": name, "price": float(price), "quantity": int(quantity)})
            self.save_products()
            self.update_product_list()
            self.product_name.delete(0, 'end')
            self.product_price.delete(0, 'end')
            self.product_quantity.delete(0, 'end')

    def update_product_list(self):
        self.product_list.delete('1.0', 'end')
        for i, product in enumerate(self.products):
            self.product_list.insert('end', f"{i+1}. {product['name']} - {product['price']} DZD - Qty: {product['quantity']}\n")
        
        # Update both product select dropdowns
        product_names = [p['name'] for p in self.products]
        if hasattr(self, 'product_select'):
            self.product_select.configure(values=product_names)
        if hasattr(self, 'update_product_select'):
            self.update_product_select.configure(values=product_names)

    def update_product(self):
        selected_product = self.update_product_select.get()
        new_price = self.update_price.get()
        new_quantity = self.update_quantity.get()

        if selected_product and new_price and new_quantity:
            product = next((p for p in self.products if p['name'] == selected_product), None)
            if product:
                product['price'] = float(new_price)
                product['quantity'] = int(new_quantity)
                self.save_products()
                self.update_product_list()
                messagebox.showinfo("Success", f"Product '{selected_product}' updated successfully")
            else:
                messagebox.showerror("Error", "Product not found. It might have been deleted.")
        else:
            messagebox.showerror("Error", "Please fill all fields")

    def add_to_order(self):
        product_name = self.product_select.get()
        quantity = int(self.order_quantity.get())

        product = next((p for p in self.products if p['name'] == product_name), None)
        if product and quantity > 0:
            if quantity <= product['quantity']:
                self.order_items.append({"product": product, "quantity": quantity})
                self.update_order_list()
            else:
                messagebox.showerror("Error", "Insufficient quantity available")

    def update_order_list(self):
        self.order_list.delete('1.0', 'end')
        total = 0
        for item in self.order_items:
            product = item['product']
            quantity = item['quantity']
            subtotal = product['price'] * quantity
            total += subtotal
            self.order_list.insert('end', f"{product['name']} - Qty: {quantity} - Subtotal: {subtotal} DZD\n")
        self.total_label.configure(text=f"Total: {total} DZD")

    def place_order(self):
        if self.order_items:
            order = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "items": self.order_items,
                "total": sum(item['product']['price'] * item['quantity'] for item in self.order_items)
            }
            self.orders.append(order)
            self.save_orders()

            for item in self.order_items:
                product = item['product']
                product['quantity'] -= item['quantity']
            self.save_products()

            self.order_items = []
            self.update_order_list()
            self.update_product_list()
            self.update_order_history()
            messagebox.showinfo("Success", "Order placed successfully")

    def update_order_history(self):
        self.order_history.delete('1.0', 'end')
        for order in self.orders:
            self.order_history.insert('end', f"Date: {order['date']}\n")
            for item in order['items']:
                self.order_history.insert('end', f"  {item['product']['name']} - Qty: {item['quantity']}\n")
            self.order_history.insert('end', f"Total: {order['total']} DZD\n\n")

    def search_orders(self):
        search_date = self.search_date.get()
        if search_date:
            matching_orders = [order for order in self.orders if order['date'].startswith(search_date)]
            self.order_history.delete('1.0', 'end')
            for order in matching_orders:
                self.order_history.insert('end', f"Date: {order['date']}\n")
                for item in order['items']:
                    self.order_history.insert('end', f"  {item['product']['name']} - Qty: {item['quantity']}\n")
                self.order_history.insert('end', f"Total: {order['total']} DZD\n\n")

    def load_products(self):
        if os.path.exists('products.csv'):
            with open('products.csv', 'r') as f:
                reader = csv.DictReader(f)
                return [{**row, 'price': float(row['price']), 'quantity': int(row['quantity'])} for row in reader]
        return []

    def save_products(self):
        with open('products.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'price', 'quantity'])
            writer.writeheader()
            writer.writerows(self.products)

    def load_orders(self):
        if os.path.exists('orders.csv'):
            with open('orders.csv', 'r') as f:
                reader = csv.DictReader(f)
                orders = []
                for row in reader:
                    order = {
                        'date': row['date'],
                        'total': float(row['total']),
                        'items': eval(row['items'])
                    }
                    orders.append(order)
                return orders
        return []

    def save_orders(self):
        with open('orders.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'total', 'items'])
            writer.writeheader()
            for order in self.orders:
                writer.writerow({
                    'date': order['date'],
                    'total': order['total'],
                    'items': str(order['items'])
                })

if __name__ == "__main__":
    app = SalesMonitorApp()
    app.mainloop()