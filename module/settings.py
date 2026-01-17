"""
Модуль настроек
"""
import flet as ft


def create_settings_page(page, data_manager):
    """Создает страницу настроек"""
    
    # Загрузка текущей темы
    current_theme = data_manager.get_data().get("theme", "light")
    
    # Переключатель темы
    theme_switch = ft.Switch(
        label="Темная тема",
        value=(current_theme == "dark"),
        on_change=lambda e: change_theme(e.control.value, page, data_manager)
    )
    
    def change_theme(is_dark, page, data_manager):
        """Изменяет тему приложения"""
        theme = "dark" if is_dark else "light"
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        
        # Сохраняем тему в данные
        data_manager.data["theme"] = theme
        data_manager.save()
        
        page.update()
    
    return ft.Container(
        content=ft.Column([
            # Заголовок
            ft.Text(
                "Настройки",
                size=28,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            
            # Переключатель темы
            ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DARK_MODE, size=40),
                        ft.Column([
                            ft.Text("Тема приложения", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("Выберите светлую или темную тему", size=14),
                            theme_switch
                        ], spacing=5, expand=True)
                    ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20
                ),
                margin=ft.Margin(0, 20, 0, 0)
            ),
            
            # Информация о приложении
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("О приложении", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("MyTasks", size=16),
                        ft.Text("Версия 1.0.0", size=14),
                        ft.Text("Приложение для управления задачами, привычками и продуктивностью", size=12)
                    ], spacing=10),
                    padding=20
                ),
                margin=ft.Margin(0, 20, 0, 0)
            )
        ], 
        spacing=20,
        expand=True),
        padding=20,
        expand=True
    )
