"""
Модуль матрицы Эйзенхауэра
"""
import flet as ft


def create_eisenhower_matrix_page(page, data_manager):
    """Создает страницу матрицы Эйзенхауэра"""
    
    def refresh_matrix():
        """Обновляет матрицу на основе текущих задач"""
        # Загружаем задачи
        tasks = data_manager.get_data().get("tasks", [])
        
        # Группируем задачи по коэффициентам (1-4)
        quadrant_1 = [t for t in tasks if t.get("coefficient", 1) == 1 and not t.get("completed", False)]
        quadrant_2 = [t for t in tasks if t.get("coefficient", 1) == 2 and not t.get("completed", False)]
        quadrant_3 = [t for t in tasks if t.get("coefficient", 1) == 3 and not t.get("completed", False)]
        quadrant_4 = [t for t in tasks if t.get("coefficient", 1) == 4 and not t.get("completed", False)]
        
        # Очищаем контейнеры
        q1_list.controls.clear()
        q2_list.controls.clear()
        q3_list.controls.clear()
        q4_list.controls.clear()
        
        # Заполняем квадранты
        for task in quadrant_1:
            q1_list.controls.append(create_task_item(task))
        for task in quadrant_2:
            q2_list.controls.append(create_task_item(task))
        for task in quadrant_3:
            q3_list.controls.append(create_task_item(task))
        for task in quadrant_4:
            q4_list.controls.append(create_task_item(task))
        
        page.update()
    
    def create_task_item(task):
        """Создает элемент задачи для отображения в квадранте"""
        return ft.Container(
            content=ft.Text(
                task.get("title", ""),
                size=12,
                overflow=ft.TextOverflow.ELLIPSIS
            ),
            padding=5,
            margin=ft.Margin(0, 0, 0, 5),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=5
        )
    
    # Заголовок
    title = ft.Text(
        "Матрица Эйзенхауэра",
        size=28,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )
    
    # Списки задач для каждого квадранта
    q1_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=5,
        expand=True
    )
    q2_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=5,
        expand=True
    )
    q3_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=5,
        expand=True
    )
    q4_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=5,
        expand=True
    )
    
    # Квадрант 1: Срочно и важно
    quadrant_1 = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Срочно и важно",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                q1_list
            ], 
            spacing=5, 
            expand=True, 
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        ),
        padding=10,
        bgcolor=ft.Colors.RED_100,
        border_radius=10,
        expand=True,
        # width=300
    )
    
    # Квадрант 2: Не срочно, но важно
    quadrant_2 = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Не срочно, но важно",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                q2_list
            ], 
            spacing=5, 
            expand=True, 
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        ),
        padding=10,
        bgcolor=ft.Colors.GREEN_100,
        border_radius=10,
        expand=True,
        # width=300
    )
    
    # Квадрант 3: Срочно, но не важно
    quadrant_3 = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Срочно, но не важно",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                q3_list
            ], 
            spacing=5, 
            expand=True, 
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        ),
        padding=10,
        bgcolor=ft.Colors.YELLOW_100,
        border_radius=10,
        expand=True,
        # width=300
    )
    
    # Квадрант 4: Не срочно и не важно
    quadrant_4 = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Не срочно и не важно",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                q4_list
            ], 
            spacing=5, 
            expand=True, 
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        ),
        padding=10,
        bgcolor=ft.Colors.GREY_200,
        border_radius=10,
        expand=True,
        # width=300
    )
    
    # Кнопка обновления
    refresh_button = ft.ElevatedButton(
        "Обновить матрицу",
        icon=ft.Icons.REFRESH,
        on_click=lambda e: refresh_matrix()
    )
    
    # Инициализация матрицы
    refresh_matrix()
    
    return ft.Container(
        content=ft.Column([
            title,
            refresh_button,
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        quadrant_1,
                        quadrant_3
                    ], spacing=10, expand=True),
                    expand=True,
                    width=None
                ),
                ft.Container(
                    content=ft.Column([
                        quadrant_2,
                        quadrant_4
                    ], spacing=10, expand=True),
                    expand=True,
                    width=None
                )
            ], spacing=10, expand=True)
        ], spacing=15, expand=True),
        padding=20,
        expand=True
    )
