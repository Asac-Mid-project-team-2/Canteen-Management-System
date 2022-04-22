import json
from .Store import Store
import pandas as pd


class CanteenSystem:
    def __init__(self):
        self.chosen_items = {}

    @staticmethod
    def greeting():
        greet = (
            '''===================================
   Welcome to the Canteen System
===================================
              ''')
        print(greet)
        return greet

    def menu(self, key):
        store = Store()
        table, items = store.get_items(key)
        return table, items

    def _chosen_item(self, sub_category):
        TEXT_ITEM_IDX = 'Enter your item: '
        TEXT_ITEM_QTY = 'Enter quantity: '
        TEXT = 'Choose another item (C), Check out (O), back to categories (G) , Quit (Q): '

        def _store_items():
            item_idx = int(input(TEXT_ITEM_IDX))
            while item_idx > len(sub_category)-1 or item_idx < 0:
                item_idx = input(TEXT_ITEM_IDX)
            item_qty = int(input(TEXT_ITEM_QTY))
            item = sub_category[item_idx]  # ["Apple", "Fresh juice", 0.35]
            try:
                if self.chosen_items[item[0]]:
                    self.chosen_items[item[0]]["Quantity"] += item_qty
            except:
                self.chosen_items[item[0]] = {
                    "Price": item[2], "Quantity": item_qty}
        _store_items()
        user_input = input(TEXT)
        while True:
            if user_input.lower() == 'q':
                return user_input
            if user_input.lower() == 'g':
                return user_input
            if user_input.lower() == 'o':
                return user_input
            _store_items()
            user_input = input(TEXT)

    def order(self):
        TEXT = 'Enter category Hot food (H), Snacks (S), Drinks (d), Quit (Q): '
        user_input = input(TEXT)
        while True:
            if user_input.lower() == 'q':
                self._quiting()
                break
            if user_input.lower() == 'h':
                table, items = self.menu('Hot food')
                print(table)
                user_input = self._chosen_item(items)
            if user_input.lower() == 's':
                table, items = self.menu('Snacks')
                print(table)
                user_input = self._chosen_item(items)
            if user_input.lower() == 'd':
                table, items = self.menu('Drinks')
                print(table)
                user_input = self._chosen_item(items)
            if user_input.lower() == 'g':
                return self.order()
            if user_input.lower() == 'o':
                self.payment_method()
                return

    def recipe(self):
        df = pd.DataFrame(self.chosen_items).T
        df['Amount'] = df["Price"].multiply(df["Quantity"], axis="index")
        total_row = df.sum(axis=0)
        total_row = ['', total_row[1], total_row[2]]
        df.loc[''] = ['-------', '------', '-------']

        df.loc['Total'] = total_row
        return df, total_row[2]

    def payment_method(self):
        PAYMENT_TEXT = 'Payment method: Credit (R), Cash (S): '
        user_input = input(PAYMENT_TEXT).lower()
        if user_input == 's':
            return self.cash_payment()
        if user_input == 'r':
            return self.credit_payment()
        self.payment_method()

    def cash_payment(self):
        df, total = self.recipe()

        print(df.to_string(index=True))
        cash = float(input('Cash amount : '))
        change = cash - total
        df.loc['Cash'] = ['', '', cash]
        df.loc['Change'] = ['', '', change]
        print(df.to_string(index=True))

    def _get_students_data(self):
        try:
            with open('Student_info.json', 'r')as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return "File Not Found"

    def _id_search(self, id):
        students_data = self._get_students_data()
        for idx, student in enumerate(students_data):
            if student['id'] == id:
                return student, idx
        return None

    def _set_student_info(self, new_student_info, idx):
        old_students_info = self._get_students_data()
        old_students_info[idx] = new_student_info
        json_object = json.dumps(old_students_info, indent=4)
        with open('Student_info.json', 'w')as f:
            f.write(json_object)

    def credit_payment(self):
        if len(self.chosen_items) == 0:
            return self.order()
        df, total = self.recipe()
        print(df.to_string(index=True))
        student_id = int(input('Enter student ID: '))
        student_info, idx = self._id_search(student_id)
        if student_info == None:
            print("The student is not exist!")
            self.payment_method()
        else:
            student_info_table = pd.DataFrame(student_info, ['Student info']).T
            print(student_info_table, '\n\n', '_'*40)
            credit_balance = student_info['Balance']
            max_daily_credit = student_info['Max Daily Credit']
            if total <= max_daily_credit or total > credit_balance:
                new_balance = credit_balance - total
                student_info['Balance'] = new_balance
                df.loc['Av. Balance:'] = ['', '', credit_balance]
                df.loc['New Balance:'] = ['', '', new_balance]
                self._set_student_info(student_info, idx)
                print(df.to_string(index=True))
            else:
                print(
                    "The total exceed the max daily credit or your balance is not enough!")
                user_input = input(
                    'Do you want to Delete (D), Pay cash (S), or Quit (Q)?: ').lower()
                if user_input == 'd':
                    self.delete_item()
                if user_input == 's':
                    self.cash_payment()
                if user_input == 'q':
                    self._quiting()

    def delete_item(self):
        def _delete_again():
            while True:
                delete_again = input(
                    'Do you want to delete another item Y/N?: ').lower()
                if delete_again == 'y':
                    return self.delete_item()
                elif delete_again == 'n':
                    return self.credit_payment()

        user_input = input('Enter the name of the item to delete: ')
        try:
            quantity = self.chosen_items[user_input]['Quantity']  # 3 Meal 1
            if quantity > 1:  # 3 >1
                get_qty = int(input(
                    f'You have {quantity} items of {user_input}, how many item/s you want to delete: '))  # 3
                if get_qty >= quantity or get_qty < 0:
                    self.chosen_items.pop(user_input)
                    return _delete_again()
            if quantity == 1:
                self.chosen_items.pop(user_input)
                return _delete_again()

            self.chosen_items[user_input]['Quantity'] -= get_qty
            return _delete_again()
        except:
            print('The item does not exist!')
            self.delete_item()

    def _quiting(self):
        print("""
===============================================================
Thank you for visiting
===============================================================
""")


if __name__ == '__main__':
    import pandas as pd
    from Store import Store
    CanteenSystem.greeting()
    canteen = CanteenSystem()
    canteen.order()
    # s = Store()
    # table, items = s.get_items('Hot food')
    # print(type(table))

    def check_not_allowed_items():
        not_allowed = ["Meal 1", "Popcorn", "Apple"]
        cart = {
            'Meal 1': {
                'price': 2.0,
                'quantity': 3
            },
            'Popcorn': {
                'price': 2.0,
                'quantity': 3
            },
            'Meal 3': {
                'price': 2.0,
                'quantity': 3
            }
        }
        cart_keys = cart.keys()
        for item in not_allowed:
            try:
                if cart[item]:
                    cart.pop(item)
            except:
                continue
        print(cart)

    # check_not_allowed_items()
