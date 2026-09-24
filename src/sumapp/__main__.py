import flet as ft
import flet.fastapi as flet_fastapi
from flet.fastapi import app_manager, FletApp
import sys, os, asyncio, uvicorn

from src.sumapp.db.database import db
from src.sumapp.db.models import Base

# import bill
from src.sumapp import bill
from src.sumapp import report

app = flet_fastapi.FastAPI()

def main(page: ft.Page):
    page.title = "Management Dashboard"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.scroll = ft.ScrollMode.ADAPTIVE # Enables smooth native scrolling
    
    # ==========================================
    # Global Theme Toggle Logic
    # ==========================================
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.SYSTEM:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_icon.icon = ft.Icons.LIGHT_MODE
        elif page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_icon.icon = ft.Icons.DARK_MODE
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM
            theme_icon.icon = ft.Icons.SETTINGS_SYSTEM_DAYDREAM
        page.update()

    theme_icon = ft.IconButton(
        icon=ft.Icons.SETTINGS_SYSTEM_DAYDREAM,
        icon_color="white",
        on_click=toggle_theme,
        tooltip="Toggle Theme (System/Light/Dark)"
    )

    # ==========================================
    # Routing Engine
    # ==========================================
    def navigate(route_string):
        page.route = route_string
        render_route(route_string)

    def render_route(route_string):
        page.views.clear()
        
        # ==========================================
        # 1. HOME DASHBOARD VIEW
        # ==========================================
        if route_string == "/":
            # UI FIX: Use a ResponsiveRow so cards stack vertically on phones and sit side-by-side on desktop
            dashboard_cards = ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        col={"xs": 12, "sm": 10, "md": 5, "lg": 4},
                        content=ft.Card(
                            elevation=5,
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.POST_ADD, size=50, color="blue"),
                                    ft.Text("Head Entry", size=20, weight=ft.FontWeight.BOLD)
                                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=30, ink=True,
                                on_click=lambda _: navigate("/entry")
                            )
                        )
                    ),
                    ft.Container(
                        col={"xs": 12, "sm": 10, "md": 5, "lg": 4},
                        content=ft.Card(
                            elevation=5,
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.ANALYTICS, size=50, color="green"),
                                    ft.Text("Reports", size=20, weight=ft.FontWeight.BOLD)
                                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=30, ink=True,
                                on_click=lambda _: navigate("/report") 
                            )
                        )
                    )
                ]
            )

            page.views.append(
                ft.View(
                    route="/",
                    padding=0,
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Main Menu"), 
                            bgcolor="blue", 
                            color="white",
                            actions=[theme_icon] # Injects the theme toggle into the header
                        ),
                        # UI FIX: SafeArea and constraint container keep the dashboard from stretching on ultrawides
                        ft.SafeArea(
                            ft.Container(
                                padding=20,
                                expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Container(height=30),
                                        ft.Text("System Dashboard", size=32, weight=ft.FontWeight.BOLD),
                                        ft.Text("Select a module to get started", size=16, color="grey"),
                                        ft.Container(height=40),
                                        dashboard_cards
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            )
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
            
        # ==========================================
        # 2. BILL ENTRY VIEW 
        # ==========================================
        elif route_string == "/entry":
            page.views.append(
                ft.View(
                    route="/entry",
                    padding=0,
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Head Entry"), 
                            bgcolor="blue", 
                            color="white", 
                            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: navigate("/")),
                            actions=[theme_icon] # Keeps the theme toggle available inside the module
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
            bill.main(page)

        # ==========================================
        # 3. REPORT VIEW
        # ==========================================
        elif route_string == "/report":
            page.views.append(
                ft.View(
                    route="/report",
                    padding=0,
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Reports & Analytics"), 
                            bgcolor="green", 
                            color="white", 
                            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: navigate("/")),
                            actions=[theme_icon] # Keeps the theme toggle available inside the module
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
            report.main(page)
            
        page.update()

    # Hardware Back Button configuration 
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        navigate(top_view.route)

    # Listen for browser forward/back buttons
    def route_change(e):
        render_route(e.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Boot up the app directly to the Home page
    navigate("/")

app.mount("/", flet_fastapi.app(main))

@app.websocket("/ws")
async def flet_app(websocket):
    await FletApp(
        loop=asyncio.get_running_loop(),
        executor=app_manager.executor,
        main=main,
        before_main=None,
    ).handle(websocket)

if __name__ == "__main__":
    try:
        Base.metadata.create_all(db.engine)
    except Exception as e:
        print(f"[Critical Error] Failed to initialize local database: {e}")
        sys.exit(1)

    try:
        db.sync_with_cloud()
        print("[Net] Synced with cloud on startup.")
    except Exception:
        print("[Net] Offline mode: Skipping startup sync.")

    try:
        # ft.run(main, port=int(os.getenv("PORT", "8000")))
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000"))
        )
    except KeyboardInterrupt:
        pass  

    try:
        db.sync_with_cloud()
    except Exception:
        pass