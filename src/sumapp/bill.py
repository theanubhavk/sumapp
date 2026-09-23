import flet as ft
import datetime
import asyncio

from src.sumapp.constants import SHG_NAMES, HEAD_NAMES
from src.sumapp.db.database import db
from src.sumapp.db.models import Base
from src.sumapp.db.repositories import HeadRepos

def add_row(head_name:str, datetime: str, shgs: list):
    with db.get_session() as session:
        repo = HeadRepos(session)
        for shg in shgs:
            repo.add(
                head_name=head_name,
                shg_name=shg.controls[0].value.lower(),
                amount=shg.controls[1].value,
                datetime=datetime
            )

def main(page: ft.Page):
    page.title = "Bill Entry System"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # page.theme_mode = ft.ThemeMode.SYSTEM 

    page.padding = 0
    page.scroll = ft.ScrollMode.ADAPTIVE

    # with db.get_session() as session:
    #     repo = HeadRepos(session)
    #     print(str(repo.get_all()))

    # ==========================================
    # 1. Date Picker Setup
    # ==========================================
    # def handle_date_change(e):
    #     if e.control.value:
    #         date_button.text = e.control.value.strftime("%Y-%m-%d")
    #         date_button.update()

    # date_picker = ft.DatePicker(
    #     on_change=handle_date_change,
    #     first_date=datetime.datetime(2020, 1, 1),
    #     last_date=datetime.datetime(2030, 12, 31),
    # )
    # page.overlay.append(date_picker)

    date_button_text = ft.Text("Select Date")

    def handle_date_change(e):
        if e.control.value:
            selected_date = e.control.value
            if isinstance(selected_date, datetime.datetime):
                # Compensate for the framework's -1 day UTC/local timezone serialization shift
                selected_date = selected_date + datetime.timedelta(days=1)
                selected_date = selected_date.date()
                
            date_button_text.value = selected_date.strftime("%Y-%m-%d")
            date_button_text.update()

    date_picker = ft.DatePicker(
        on_change=handle_date_change,
        first_date=datetime.datetime(2020, 1, 1),
        last_date=datetime.datetime(2030, 12, 31),
    )

    # ==========================================
    # 2. Card Header Controls
    # ==========================================
    bill_type_dropdown = ft.Dropdown(
        label="Head Name",
        options=[ft.dropdown.Option(head) for head in HEAD_NAMES],
        expand=True
        # width=200,
    )

    # CHANGED: ft.ElevatedButton -> ft.Button | ft.icons -> ft.Icons
    date_button = ft.Button(
        date_button_text,
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda _: page.show_dialog(date_picker),
        expand=True
        # width=150,
    )

    # ==========================================
    # 3. Card Body Controls
    # ==========================================
    items_column = ft.Column(
        spacing=5, 
        height=160,                # <--- Restricts how tall the list can get
        scroll=ft.ScrollMode.AUTO  # <--- Adds a scrollbar when items exceed the height
    )

    # Made async to handle auto-scrolling
    async def add_item_row(e):
        def delete_item(e_delete):
            items_column.controls.remove(item_row)
            page.update()

        item_row = ft.Row(
            controls=[
                ft.Dropdown(
                    label="SHG Name",
                    options=[ft.dropdown.Option(shg) for shg in SHG_NAMES],
                    expand=2
                    # width=150,
                ),
                ft.TextField(
                    label="Amount", 
                    expand=1,
                    # width=100,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    input_filter=ft.NumbersOnlyInputFilter()
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE, 
                    icon_color="red", 
                    on_click=delete_item,
                    tooltip="Remove SHG"
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            wrap=False #UI
        )
        
        items_column.controls.append(item_row)
        page.update()

        # Smoothly scroll down to the newly added item row
        await items_column.scroll_to(offset=100000, duration=300)

    add_item_button = ft.IconButton(
        icon=ft.Icons.ADD_CIRCLE,
        icon_color="blue",
        icon_size=30,
        tooltip="Add new SHG",
        on_click=add_item_row,
    )
    # ==========================================
    # 4. Card Footer Controls 
    # ==========================================
    async def handle_submit(e):
        if not bill_type_dropdown.value:
            page.show_dialog(ft.SnackBar(content=ft.Text("Please select a Head Name!", color="white"), bgcolor="red"))
            return

        # Validation: Check Date
        if date_button_text.value == "Select Date" or not date_button_text.value:
            page.show_dialog(ft.SnackBar(content=ft.Text("Please select a Date!", color="white"), bgcolor="red"))
            return

        # Validation: Check at least 1 item exists
        if not items_column.controls:
            page.show_dialog(ft.SnackBar(content=ft.Text("Please add at least 1 SHG!", color="white"), bgcolor="red"))
            return

        # Validation: Check if item fields are fully completed
        for index, row in enumerate(items_column.controls):
            category = row.controls[0].value
            count = row.controls[1].value
            if not category or not count:
                page.show_dialog(ft.SnackBar(content=ft.Text(f"Item {index + 1} is missing Category or Count!", color="white"), bgcolor="red"))
                return

        submit_button.disabled = True
        submit_button_text.value = "Saving..." 
        page.update()

        # adding row to DB
        await asyncio.to_thread(
            add_row, 
            head_name=bill_type_dropdown.value,
            datetime=date_button_text.value,
            shgs=items_column.controls
        )

        page.show_dialog(ft.SnackBar(content=ft.Text("SHG submitted successfully!", color="white"), bgcolor="green"))

        bill_type_dropdown.value = None
        date_button_text.value = "Select Date"
        
        # 2. Clear all item rows
        items_column.controls.clear()
        
        # 3. Add one fresh, empty item row back
        await add_item_row(None)

        submit_button.disabled = False
        submit_button_text.value = "Submit SHG"
        
        # 4. Update the page to show the empty form
        page.update()

    # CHANGED: ft.ElevatedButton -> ft.Button
    submit_button_text = ft.Text("Submit Head")
    submit_button = ft.Button(
        content=submit_button_text,
        color="white",
        bgcolor="green",
        on_click=handle_submit,
    )

    # ==========================================
    # 5. Assemble the Card
    # ==========================================
    bill_card = ft.Card(
        visible=False, 
        width=500,
        elevation=5,
        content=ft.Container(
            padding=15,
            content=ft.Column(
                controls=[
                    ft.Text("New Head Entry", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Row([bill_type_dropdown, date_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=10),
                    ft.Row([ft.Text("SHGs List", size=16, weight=ft.FontWeight.W_500), add_item_button]),
                    items_column,
                    ft.Divider(),
                    ft.Row([submit_button], alignment=ft.MainAxisAlignment.END)
                ]
            )
        )
    )

    # ==========================================
    # 6. Main Page Layout & Add Bill Button
    # ==========================================
    async def show_card(e):
        bill_card.visible = True
        if not items_column.controls:
            await add_item_row(None)
        page.update()

    # CHANGED: ft.icons -> ft.Icons
    add_bill_icon = ft.FloatingActionButton(
        icon=ft.Icons.POST_ADD,
        # text="Add Bill",
        on_click=show_card,
        shape=ft.CircleBorder()
        # width=150
    )

    top_action_row = ft.Row([add_bill_icon], alignment=ft.MainAxisAlignment.END)
    responsive_container = ft.SafeArea(
        ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    col={"xs": 12, "sm": 10, "md": 8, "lg": 6},
                    controls=[
                        ft.Container(height=10), 
                        top_action_row,
                        ft.Container(height=15), 
                        bill_card,
                        ft.Container(height=20) # UI FIX: Added bottom padding so the button isn't hugging the screen edge
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ]
        )
    )
    
    page.add(responsive_container)

    # page.add(
    #     ft.Container(height=20), 
    #     add_bill_icon,
    #     ft.Container(height=20), 
    #     bill_card
    # )

# if __name__ == "__main__":
# # 1. Schema setup
#     try:
#         Base.metadata.create_all(db.engine)
#     except Exception as e:
#         print(f"[Critical Error] Failed to initialize local database: {e}")
#         sys.exit(1)

#     # 2. Startup Sync (Safe catch for offline mode)
#     try:
#         db.sync_with_cloud()
#         print("[Net] Synced with cloud on startup.")
#     except Exception:
#         print("[Net] Offline mode: Skipping startup sync.")

#     # 3. Run the Flet App
#     try:
#         ft.run(main)
#     except KeyboardInterrupt:
#         pass  # Handle Ctrl+C cleanly without crashing the event loop

#     # 4. Exit Sync (Completely silent to prevent BrokenPipeError)
#     try:
#         db.sync_with_cloud()
#     except Exception:
#         pass