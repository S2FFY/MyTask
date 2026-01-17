"""
Приложение MyTasks
"""
import flet as ft
from module.data_manager import load_data, save_data
from module.todo_list import create_todo_list_page
from module.habit_tracker import create_habit_tracker_page
from module.eisenhower_matrix import create_eisenhower_matrix_page
from module.pomodoro import create_pomodoro_page
from module.settings import create_settings_page


class DataManager:
    """Класс для управления данными приложения"""
    def __init__(self):
        self.data = load_data()
    
    def get_data(self):
        return self.data
    
    def save(self):
        save_data(self.data)
    
    def update_data(self, new_data):
        self.data.update(new_data)
        self.save()


def main(page: ft.Page):
    """Главная приложения"""
    # Настройка страницы
    page.title = "MyTasks"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Инициализация менеджера данных
    data_manager = DataManager()
    
    # Загрузка темы
    theme = data_manager.get_data().get("theme", "light")
    if theme == "dark":
        page.theme_mode = ft.ThemeMode.DARK
    
    # Заголовок приложения
    header = ft.Container(
        content=ft.Text(
            "MyTasks",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        ),
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding(0, 10, 0, 10),
        border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_400))
    )
    
    # Контентная область
    content_area = ft.Container(
        content=create_todo_list_page(page, data_manager),
        expand=True,
        padding=20
    )
    
    # Функция для переключения вкладок
    def on_navigation_change(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            content_area.content = create_todo_list_page(page, data_manager)
        elif selected_index == 1:
            content_area.content = create_habit_tracker_page(page, data_manager)
        elif selected_index == 2:
            content_area.content = create_eisenhower_matrix_page(page, data_manager)
        elif selected_index == 3:
            content_area.content = create_pomodoro_page(page, data_manager)
        elif selected_index == 4:
            content_area.content = create_settings_page(page, data_manager)
        page.update()
    
    # NavigationRail
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        leading=ft.FloatingActionButton(
            icon=ft.Icons.APPS,
            tooltip="Myt=Tasks",
            content=ft.Text("MyTasks"),
            on_click=lambda _: None
        ),
        group_alignment=-0.25,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CHECKLIST,
                selected_icon=ft.Icons.CHECKLIST,
                label="To-do list",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TRACK_CHANGES,
                selected_icon=ft.Icons.TRACK_CHANGES,
                label="Трекер привычек",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.GRID_VIEW,
                selected_icon=ft.Icons.GRID_VIEW,
                label="Матрица",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TIMER,
                selected_icon=ft.Icons.TIMER,
                label="Помодоро",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS,
                selected_icon=ft.Icons.SETTINGS,
                label="Настройки",
            ),
        ],
        on_change=on_navigation_change,
    )
    
    # Основной layout
    page.add(
        header,
        ft.Row(
            [
                nav_rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        ),
    )


if __name__ == "__main__":
    ft.run(main)
