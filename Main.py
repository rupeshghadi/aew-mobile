import os
from datetime import datetime
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.filemanager import MDFileManager

from database import init_db, get_db, backup_database, restore_database, get_app_dir

# Set portrait aspect ratio for desktop preview testing
Window.size = (390, 750)

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            type: "small"
            MDTopAppBarTitle:
                text: "AEW Billing & ERP"
            MDTopAppBarTrailingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "refresh"
                    on_release: app.refresh_all_data()

        MDBottomNavigation:
            id: nav_bar

            # ---------------- DASHBOARD TAB ----------------
            MDBottomNavigationItem:
                name: "tab_dashboard"
                text: "Overview"
                icon: "view-dashboard"

                MDScrollView:
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "16dp"
                        spacing: "12dp"
                        adaptive_height: True

                        MDCard:
                            style: "elevated"
                            padding: "16dp"
                            size_hint_y: None
                            height: "110dp"
                            md_bg_color: 0.94, 0.97, 1.0, 1.0

                            MDBoxLayout:
                                orientation: "vertical"
                                MDLabel:
                                    text: "TOTAL BILLED (CURRENT FY)"
                                    font_style: "Label"
                                    role: "small"
                                    theme_text_color: "Custom"
                                    text_color: 0.01, 0.52, 0.78, 1.0
                                MDLabel:
                                    id: lbl_turnover
                                    text: "₹ 0.00"
                                    font_style: "Headline"
                                    role: "medium"
                                    bold: True
                                MDLabel:
                                    id: lbl_inv_count
                                    text: "0 invoices recorded"
                                    font_style: "Body"
                                    role: "small"
                                    theme_text_color: "Secondary"

                        MDCard:
                            style: "outlined"
                            padding: "16dp"
                            size_hint_y: None
                            height: "90dp"

                            MDBoxLayout:
                                orientation: "vertical"
                                MDLabel:
                                    text: "OPEN DELIVERY CHALLANS"
                                    font_style: "Label"
                                    role: "small"
                                    theme_text_color: "Custom"
                                    text_color: 0.85, 0.47, 0.02, 1.0
                                MDLabel:
                                    id: lbl_open_dc
                                    text: "0 Pending"
                                    font_style: "Headline"
                                    role: "small"
                                    bold: True

            # ---------------- NEW INVOICE TAB ----------------
            MDBottomNavigationItem:
                name: "tab_invoice"
                text: "New Invoice"
                icon: "receipt"

                MDScrollView:
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "16dp"
                        spacing: "12dp"
                        adaptive_height: True

                        MDTextField:
                            id: txt_inv_num
                            mode: "outlined"
                            MDTextFieldHintText:
                                text: "Invoice Number"

                        MDTextField:
                            id: txt_cust_id
                            mode: "outlined"
                            input_filter: "int"
                            MDTextFieldHintText:
                                text: "Customer ID"

                        MDTextField:
                            id: txt_amount
                            mode: "outlined"
                            input_filter: "float"
                            on_text: app.recalculate_taxes()
                            MDTextFieldHintText:
                                text: "Taxable Subtotal (₹)"

                        MDBoxLayout:
                            orientation: "horizontal"
                            size_hint_y: None
                            height: "30dp"
                            MDLabel:
                                id: lbl_gst_split
                                text: "CGST (9%): ₹0.00 | SGST (9%): ₹0.00"
                                font_style: "Body"
                                role: "small"

                        MDLabel:
                            id: lbl_inv_total
                            text: "Total Amount: ₹ 0.00"
                            font_style: "Title"
                            role: "medium"
                            bold: True

                        MDButton:
                            style: "filled"
                            pos_hint: {"center_x": .5}
                            on_release: app.save_invoice()
                            MDButtonText:
                                text: "Save Tax Invoice"

            # ---------------- CUSTOMER MASTER TAB ----------------
            MDBottomNavigationItem:
                name: "tab_customer"
                text: "Parties"
                icon: "account-multiple"

                MDScrollView:
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "16dp"
                        spacing: "12dp"
                        adaptive_height: True

                        MDTextField:
                            id: txt_cust_name
                            mode: "outlined"
                            MDTextFieldHintText:
                                text: "Party / Company Name*"

                        MDTextField:
                            id: txt_cust_gstin
                            mode: "outlined"
                            MDTextFieldHintText:
                                text: "GSTIN / Tax ID"

                        MDTextField:
                            id: txt_cust_phone
                            mode: "outlined"
                            MDTextFieldHintText:
                                text: "Phone Number"

                        MDTextField:
                            id: txt_cust_address
                            mode: "outlined"
                            MDTextFieldHintText:
                                text: "Factory / Work Address"

                        MDButton:
                            style: "filled"
                            pos_hint: {"center_x": .5}
                            on_release: app.save_customer()
                            MDButtonText:
                                text: "Add Customer"

            # ---------------- BACKUP & RESTORE TAB ----------------
            MDBottomNavigationItem:
                name: "tab_backup"
                text: "Backups"
                icon: "database-sync"

                MDScrollView:
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "16dp"
                        spacing: "14dp"
                        adaptive_height: True

                        MDCard:
                            style: "elevated"
                            padding: "16dp"
                            size_hint_y: None
                            height: "170dp"

                            MDBoxLayout:
                                orientation: "vertical"
                                spacing: "6dp"
                                MDLabel:
                                    text: "Local Snapshot Backup"
                                    font_style: "Title"
                                    role: "small"
                                    bold: True
                                MDLabel:
                                    text: "Save an atomic snapshot of your database to local storage or export to Google Drive."
                                    font_style: "Body"
                                    role: "small"
                                    theme_text_color: "Secondary"

                                MDButton:
                                    style: "filled"
                                    on_release: app.trigger_backup()
                                    MDButtonText:
                                        text: "Create Backup Now"

                        MDCard:
                            style: "outlined"
                            padding: "16dp"
                            size_hint_y: None
                            height: "170dp"

                            MDBoxLayout:
                                orientation: "vertical"
                                spacing: "6dp"
                                MDLabel:
                                    text: "Restore Database"
                                    font_style: "Title"
                                    role: "small"
                                    bold: True
                                MDLabel:
                                    text: "Restore all ERP records from an existing .db file. A pre-restore safety copy is created first."
                                    font_style: "Body"
                                    role: "small"
                                    theme_text_color: "Secondary"

                                MDButton:
                                    style: "tonal"
                                    on_release: app.open_file_selector()
                                    MDButtonText:
                                        text: "Choose .db Backup to Restore"
'''

class AEWAndroidApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "SteelBlue"
        self.theme_cls.theme_style = "Light"
        init_db()

        # Initialize File Manager for Restore operations
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.on_file_selected,
            ext=[".db", ".sqlite"]
        )
        return Builder.load_string(KV)

    def on_start(self):
        self.refresh_all_data()

    def show_toast(self, message):
        MDSnackbar(
            MDSnackbarText(text=message),
            y="24dp",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9
        ).open()

    def recalculate_taxes(self):
        try:
            val = float(self.root.ids.txt_amount.text or 0.0)
            cgst = val * 0.09
            sgst = val * 0.09
            total = val + cgst + sgst
            self.root.ids.lbl_gst_split.text = f"CGST (9%): ₹{cgst:,.2f} | SGST (9%): ₹{sgst:,.2f}"
            self.root.ids.lbl_inv_total.text = f"Total Amount: ₹ {total:,.2f}"
        except ValueError:
            pass

    def refresh_all_data(self):
        with get_db() as conn:
            cur = conn.cursor()

            # Dashboard totals
            cur.execute("SELECT COUNT(*), IFNULL(SUM(total), 0.0) FROM invoices")
            inv_count, total_turnover = cur.fetchone()
            self.root.ids.lbl_turnover.text = f"₹ {total_turnover:,.2f}"
            self.root.ids.lbl_inv_count.text = f"{inv_count} invoice(s) recorded"

            cur.execute("SELECT COUNT(*) FROM delivery_challans WHERE status = 'Open'")
            open_dcs = cur.fetchone()[0]
            self.root.ids.lbl_open_dc.text = f"{open_dcs} Open Dispatch(es)"

            # Autoincrement invoice sequence
            cur.execute("SELECT COUNT(*) FROM invoices")
            next_seq = cur.fetchone()[0] + 1
            self.root.ids.txt_inv_num.text = f"AEW/2026-27/{next_seq:03d}"

    def save_customer(self):
        name = self.root.ids.txt_cust_name.text.strip()
        gstin = self.root.ids.txt_cust_gstin.text.strip().upper()
        phone = self.root.ids.txt_cust_phone.text.strip()
        address = self.root.ids.txt_cust_address.text.strip()

        if not name:
            self.show_toast("Party Name is required.")
            return

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO customers (name, tax_id, phone, address)
                VALUES (?, ?, ?, ?)
            """, (name, gstin, phone, address))
            conn.commit()

        self.root.ids.txt_cust_name.text = ""
        self.root.ids.txt_cust_gstin.text = ""
        self.root.ids.txt_cust_phone.text = ""
        self.root.ids.txt_cust_address.text = ""
        self.show_toast(f"Customer '{name}' saved successfully!")

    def save_invoice(self):
        inv_num = self.root.ids.txt_inv_num.text.strip()
        cust_id_raw = self.root.ids.txt_cust_id.text.strip()
        taxable_raw = self.root.ids.txt_amount.text.strip()

        if not inv_num or not cust_id_raw or not taxable_raw:
            self.show_toast("Please fill in all invoice fields.")
            return

        subtotal = float(taxable_raw)
        cgst = subtotal * 0.09
        sgst = subtotal * 0.09
        total = subtotal + cgst + sgst
        date_str = datetime.now().strftime("%d-%m-%Y")

        try:
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO invoices (
                        invoice_num, customer_id, invoice_date, financial_year,
                        subtotal, cgst_rate, cgst_amount, sgst_rate, sgst_amount, total
                    ) VALUES (?, ?, ?, '2026-27', ?, 9.0, ?, 9.0, ?, ?)
                """, (inv_num, int(cust_id_raw), date_str, subtotal, cgst, sgst, total))
                conn.commit()

            self.show_toast(f"Invoice {inv_num} registered!")
            self.root.ids.txt_amount.text = ""
            self.root.ids.txt_cust_id.text = ""
            self.refresh_all_data()
        except Exception as e:
            self.show_toast(f"Error saving invoice: {str(e)}")

    # ---------------- BACKUP & RESTORE HANDLERS ----------------
    def trigger_backup(self):
        ok, res = backup_database()
        if ok:
            fname = os.path.basename(res)
            self.show_toast(f"Backup saved: {fname}")
        else:
            self.show_toast(f"Backup error: {res}")

    def open_file_selector(self):
        start_dir = os.path.join(get_app_dir(), "backups")
        if not os.path.exists(start_dir):
            start_dir = get_app_dir()
        self.file_manager.show(start_dir)

    def on_file_selected(self, path):
        self.exit_file_manager()
        ok, msg = restore_database(path)
        self.show_toast(msg)
        if ok:
            self.refresh_all_data()

    def exit_file_manager(self, *args):
        self.file_manager.close()

if __name__ == "__main__":
    AEWAndroidApp().run()