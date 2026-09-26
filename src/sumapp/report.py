import flet as ft
import asyncio

from src.sumapp.db.database import db
from src.sumapp.db.repositories import HeadRepos

from src.sumapp.constants import SHG_NAMES, HEAD_NAMES

def read_shg_report(head_name: str) -> dict:
    with db.get_session() as session:
        repo = HeadRepos(session)
        report = repo.get_all_shg_summaries(head_name=head_name)
    return report

def read_shg_rows(head_name: str, shg_name: str) -> list[dict]:
    with db.get_session() as session:
        repo = HeadRepos(session)
        records = repo.get_shg_records_by_year(
            head_name=head_name, 
            target_shg_name=shg_name
        )
    return records

def main(page: ft.Page):
    page.title = "Bill & Item Report"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.scroll = ft.ScrollMode.ADAPTIVE

    # ==========================================
    # 1. UI Controls Setup
    # ==========================================
    bill_type_dropdown = ft.Dropdown(
        label="Select Head Name",
        options=[ft.dropdown.Option(head) for head in HEAD_NAMES],
        expand=True
        # width=200,
    )

    calculate_button_text = ft.Text("Calculate")
    calculate_button = ft.Button(
        content=calculate_button_text,
        icon=ft.Icons.CALCULATE,
        color="white",
        bgcolor="blue",
        # width=150,
        height=50,
    )

    # ==========================================
    # 2. Main Data Table & Total UI
    # ==========================================
    # The table is initially hidden until "Calculate" is clicked
    results_table = ft.DataTable(
        # visible=False,
        columns=[
            # ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("SHG", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Total Amount", weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Total Records", weight=ft.FontWeight.BOLD), numeric=True),
            ft.DataColumn(ft.Text("Action", weight=ft.FontWeight.BOLD)),
        ],
        rows=[]
    )
    table_container = ft.Column(
        controls=[
            ft.Row(
                controls=[results_table],
                scroll=ft.ScrollMode.ADAPTIVE, # Allows horizontal swiping
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        height=350,                # UI FIX: Prevents the table from stretching the whole page
        scroll=ft.ScrollMode.AUTO, # Allows vertical scrolling within the table area
        visible=False 
    )

    # ==========================================
    # 3. Drill-Down Dialog (Eye Icon Pop-up)
    # ==========================================
    # This is the secondary table that opens when the eye icon is clicked
    drill_down_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Amount"), numeric=True),
            ],
            rows=[]
        )
    drill_down_table_container = ft.Row(
        controls=[drill_down_table],
        scroll=ft.ScrollMode.ADAPTIVE,
        alignment=ft.MainAxisAlignment.CENTER
    )

    drill_down_dialog = ft.AlertDialog(
        title=ft.Text("SHG Details"),
        content=ft.Container(
            width=500, # UI FIX: Expands the dialog window to a standard desktop width
            content=ft.Column(
                controls=[drill_down_table_container], 
                scroll=ft.ScrollMode.AUTO, 
                height=300
            )
        ),
        actions=[ft.Button("Close", on_click=lambda e: close_dialog(e))]
    )

    def close_dialog(e):
        drill_down_dialog.open = False
        page.update()

    async def handle_eye_click(e):
        # Retrieve the specific shg and head that was clicked
        # We stored these in the button's 'data' property during row creation
        row_data = e.control.data 

        shg_records = await asyncio.to_thread(
            read_shg_rows,
            head_name=row_data["head"],
            shg_name=row_data["shg"]
        )
        
        drill_down_table.rows.clear()
        for record in shg_records:
            drill_down_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(record["datetime"])),
                    ft.DataCell(ft.Text(str(record["amount"])))
                ])
            )

        drill_down_dialog.title = ft.Row(
            controls=[
                ft.Text(row_data['head'], size=18, weight=ft.FontWeight.BOLD),
                ft.Text(row_data['shg'].capitalize(), size=14, color="grey"),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            expand=True
        )
        
        # Open the dialog
        page.show_dialog(drill_down_dialog)

    # ==========================================
    # 4. Calculate Button Logic
    # ==========================================
    async def handle_calculate(e):
        # 1. Validation
        if not bill_type_dropdown.value:
            page.show_dialog(ft.SnackBar(content=ft.Text("Please select Head name first!", color="white"), bgcolor="red"))
            return

        # 2. UI Loading State
        calculate_button.disabled = True
        calculate_button_text.value = "Calculating..."
        page.update()

        summary = await asyncio.to_thread(
            read_shg_report,
            head_name=bill_type_dropdown.value
        )
        # await asyncio.sleep(0.5) 
        
        results_table.rows.clear()
        for i, (shg_name, data) in enumerate(summary.items(), start=1):
            eye_icon = ft.IconButton(
                icon=ft.Icons.REMOVE_RED_EYE,
                icon_color="blue",
                tooltip="View Details",
                data={"id": i, "shg": shg_name, "head": bill_type_dropdown.value}, 
                on_click=handle_eye_click
            )
            results_table.rows.append(
                ft.DataRow(
                    cells=[
                        # ft.DataCell(ft.Text(str(i))),
                        ft.DataCell(ft.Text(shg_name)),
                        ft.DataCell(ft.Text(str(data["total_amount"]))),
                        ft.DataCell(ft.Text(str(data["total_rows"]))),
                        ft.DataCell(eye_icon), # The 4th column is the action button
                    ]
                )
            )

        results_table.visible = True
        table_container.visible = True
        
        calculate_button.disabled = False
        calculate_button_text.value = "Calculate"
        page.update()

    calculate_button.on_click = handle_calculate

    # ==========================================
    # 5. Page Layout Assembly
    # ==========================================
    report_card = ft.Card(
        elevation=4,
        content=ft.Container(
            padding=15, 
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[bill_type_dropdown, calculate_button],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    table_container # UI FIX: Injects the horizontally scrollable wrapper instead of the raw table
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
    )

    # UI FIX: Standardizes constraints so desktop isn't stretched and mobile doesn't crash
    responsive_container = ft.SafeArea(
        ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    col={"xs": 12, "sm": 11, "md": 9, "lg": 8}, # Wider grid than bill.py to accommodate 5 table columns
                    controls=[
                        ft.Container(height=20),
                        ft.Text("Reporting & Calculations", size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10), 
                        report_card,
                        ft.Container(height=40) 
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ]
        )
    )

    page.add(responsive_container)

# ft.run(main, port=8551)