import os
from datetime import datetime
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp

from database import init_db, get_db, backup_database, restore_database, get_app_dir

# Set portrait preview window size for local desktop testing
if platform != "android":
    Window.size = (390, 750)

KV = '''
MDBoxLayout:
    orientation: "vertical"

    MDTopAppBar:
        title: "AEW Billing & ERP"
        right_action_items: [["refresh", lambda x: app.refresh_all_data()]]
        elevation: 2

    MDBottomNavigation:
        id: nav_bar

        # ---------------- 1. DASHBOARD OVERVIEW TAB ----------------
        MDBottomNavigationItem:
            name: "tab_dashboard"
            text: "Overview"
            icon: "view-dashboard"

            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "12dp"
                    adaptive_height: True

                    MDCard:
                        orientation: "vertical"
                        padding: "16dp"
                        size_hint_y: None
                        height: "105dp"
                        elevation: 1
                        md_bg_color: 0.94, 0.97, 1.0, 1.0

                        MDLabel:
                            text: "TOTAL BILLED (CURRENT FY)"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.01, 0.52, 0.78, 1.0
                        MDLabel:
                            id: lbl_turnover
                            text: "₹ 0.00"
                            font_style: "H5"
                            bold: True
                        MDLabel:
                            id: lbl_inv_count
                            text: "0 invoices recorded"
                            font_style: "Caption"
                            theme_text_color: "Secondary"

                    MDCard:
                        orientation: "vertical"
                        padding: "16dp"
                        size_hint_y: None
                        height: "90dp"
                        elevation: 1

                        MDLabel:
                            text: "OPEN DELIVERY CHALLANS"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: 0.85, 0.47, 0.02, 1.0
                        MDLabel:
                            id: lbl_open_dc
                            text: "0 Pending"
                            font_style: "H6"
                            bold: True

        # ---------------- 2. INVOICE GENERATOR TAB ----------------
        MDBottomNavigationItem:
            name: "tab_invoice"
            text: "New Invoice"
            icon: "receipt"

            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "12dp"
                    adaptive_height: True

                    MDTextField:
                        id: txt_inv_num
                        hint_text: "Invoice Number"
                        mode: "rectangle"

                    MDTextField:
                        id: txt_cust_id
                        hint_text: "Customer ID"
                        input_filter: "int"
                        mode: "rectangle"

                    MDTextField:
                        id: txt_amount
                        hint_text: "Taxable Subtotal (₹)"
                        input_filter: "float"
                        mode: "rectangle"
                        on_text: app.recalculate_taxes()

                    MDLabel:
                        id: lbl_gst_split
                        text: "CGST (9%): ₹0.00 | SGST (9%): ₹0.00"
                        font_style: "Caption"

                    MDLabel:
                        id: lbl_inv_total
                        text: "Total Amount: ₹ 0.00"
                        font_style: "Subtitle1"
                        bold: True

                    MDRaisedButton:
                        text: "Save Tax Invoice"
                        pos_hint: {"center_x": .5}
                        on_release: app.save_invoice()

        # ---------------- 3. CUSTOMER MASTER TAB ----------------
        MDBottomNavigationItem:
            name: "tab_customer"
            text: "Parties"
            icon: "account-multiple"

            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "12dp"
                    adaptive_height: True

                    MDTextField:
                        id: txt_cust_name
                        hint_text: "Party / Company Name*"
                        mode: "rectangle"

                    MDTextField:
                        id: txt_cust_gstin
                        hint_text: "GSTIN / Tax ID"
                        mode: "rectangle"

                    MDTextField:
                        id: txt_cust_phone
                        hint_text: "Phone Number"
                        mode: "rectangle"

                    MDTextField:
                        id: txt_cust_address
                        hint_text: "Factory / Work Address"
                        mode: "rectangle"

                    MDRaisedButton:
                        text: "Add Customer"
                        pos_hint: {"center_x": .5}
                        on_release: app.save_customer()

        # ---------------- 4. BACKUP & RESTORE TAB ----------------
        MDBottomNavigationItem:
            name: "tab_backup"
            text: "Backups"
            icon: "database-sync"

            ScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "14dp"
                    adaptive_height: True

                    MDCard:
                        orientation: "vertical"
                        padding: "16dp"
                        size_hint_y: None
                        height: "150dp"
                        elevation: 1

                        MDLabel:
                            text: "Local Snapshot Backup"
                            font_style: "Subtitle1"
                            bold: True
                        MDLabel:
                            text: "Creates an atomic snapshot copy in your app storage."
                            font_style: "Caption"
                            theme_text_color: "Secondary"

                        MDRaisedButton:
                            text: "Create Backup Now"
                            on_release: app.trigger_backup()

                    MDCard:
                        orientation: "vertical"
                        padding: "16dp"
                        size_hint_y: None
                        height: "150dp"
                        elevation: 1

                        MDLabel:
                            text: "Restore Database"
                            font_style: "Subtitle1"
                            bold: True
                        MDLabel:
                            text: "Restores from the latest available backup file."
                            font_style: "Caption"
                            theme_text_color: "Secondary"

                        MDRectangleFlatButton:
                            text: "Restore Latest Backup"
                            on_release: app.trigger_restore()
'''

class AEWAndroidApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        init_db()
        return Builder.load_string(KV)

    def on_start(self):
        self.refresh_all_data()

    def show_toast(self, text):
        """Crash-proof toast messaging supporting both Android native and desktop fallbacks."""
        if platform == "android":
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Toast = autoclass('android.widget.Toast')
                String = autoclass('java.lang.String')
                context = PythonActivity.mActivity
                context.runOnUiThread(
                    lambda: Toast.makeText(
                        context,
                        String(str(text)),
                        Toast.LENGTH_SHORT
                    ).show()
                )
                return
            except Exception as e:
                print(f"[Android Toast Error]: {e}")

        # Desktop fallback
        try:
            from kivymd.uix.snackbar import Snackbar
            from kivymd.uix.label import MDLabel
            Snackbar(
                MDLabel(
                    text=str(text),
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                ),
                duration=2.0
            ).open()
        except Exception:
            print(f"[APP LOG]: {text}")

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
            cur.execute("SELECT COUNT(*), IFNULL(SUM(total), 0.0) FROM invoices")
            inv_count, total_turnover = cur.fetchone()
            self.root.ids.lbl_turnover.text = f"₹ {total_turnover:,.2f}"
            self.root.ids.lbl_inv_count.text = f"{inv_count} invoice(s) recorded"

            cur.execute("SELECT COUNT(*) FROM delivery_challans WHERE status = 'Open'")
            open_dcs = cur.fetchone()[0]
            self.root.ids.lbl_open_dc.text = f"{open_dcs} Open Dispatch(es)"

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
            cur.execute(
                "INSERT INTO customers (name, tax_id, phone, address) VALUES (?, ?, ?, ?)",
                (name, gstin, phone, address)
            )
            conn.commit()

        self.root.ids.txt_cust_name.text = ""
        self.root.ids.txt_cust_gstin.text = ""
        self.root.ids.txt_cust_phone.text = ""
        self.root.ids.txt_cust_address.text = ""
        self.show_toast(f"Customer '{name}' saved!")

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
            self.show_toast(f"Error: {str(e)}")

    def trigger_backup(self):
        ok, res = backup_database()
        if ok:
            self.show_toast(f"Backup saved: {os.path.basename(res)}")
        else:
            self.show_toast(f"Backup error: {res}")

    def trigger_restore(self):
        backup_dir = os.path.join(get_app_dir(), "backups")
        if not os.path.exists(backup_dir) or not os.listdir(backup_dir):
            self.show_toast("No local backups found to restore.")
            return

        files = sorted(
            [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".db")],
            key=os.path.getmtime,
            reverse=True
        )
        if files:
            ok, msg = restore_database(files[0])
            self.show_toast(msg)
            if ok:
                self.refresh_all_data()

if __name__ == "__main__":
    AEWAndroidApp().run()
