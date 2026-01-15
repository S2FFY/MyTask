"""
Модуль To-do list
"""
import flet as ft
import uuid


def create_todo_list_page(page, data_manager):
    """Создает страницу To-do list"""
    
    # Загрузка задач из данных
    tasks_data = data_manager.get_data().get("tasks", [])
    
    # Контейнер для списка задач (центральный)
    tasks_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        expand=True
    )
    
    # Правая панель с деталями задачи (пустая по умолчанию)
    details_container = ft.Container(
        content=ft.Column([], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO),
        padding=20,
        border=ft.Border(left=ft.BorderSide(1, ft.Colors.GREY_300)),
        width=400,
        visible=False,
        expand=True
    )
    
    # Переменная для хранения выбранной задачи
    selected_task_id = {"value": None}
    
    def show_task_details(task_id):
        """Показывает детали выбранной задачи"""
        selected_task_id["value"] = task_id
        # Всегда берем данные из актуального источника
        current_tasks = data_manager.get_data().get("tasks", [])
        task = next((t for t in current_tasks if t["id"] == task_id), None)
        
        if task:
            # Создаем компоненты деталей
            title_field = ft.TextField(
                value=task.get("title", ""),
                label="Название задачи",
                expand=True,
                on_blur=lambda e: update_task_field(task_id, "title", e.control.value, data_manager, refresh_details_only)
            )
            
            coefficient_dropdown = ft.Dropdown(
                value=task.get("coefficient", 1),
                label="Коэффициент приоритета",
                options=[
                    ft.dropdown.Option(1, "1 - Срочно и важно"),
                    ft.dropdown.Option(2, "2 - Не срочно, но важно"),
                    ft.dropdown.Option(3, "3 - Срочно, но не важно"),
                    ft.dropdown.Option(4, "4 - Не срочно и не важно"),
                ],
                width=300
            )
            def on_coefficient_change(e):
                update_task_field(task_id, "coefficient", int(e.control.value), data_manager, refresh_details_only)
            coefficient_dropdown.on_change = on_coefficient_change
            
            description_field = ft.TextField(
                value=task.get("description", ""),
                label="Описание задачи",
                hint_text="Описание задачи",
                multiline=True,
                min_lines=5,
                max_lines=10,
                expand=True,
                on_blur=lambda e: update_task_field(task_id, "description", e.control.value, data_manager, refresh_details_only)
            )
            
            def delete_task_click(e):
                """Удаляет задачу"""
                tasks = data_manager.get_data().get("tasks", [])
                tasks = [t for t in tasks if t["id"] != task_id]
                data_manager.data["tasks"] = tasks
                data_manager.save()
                selected_task_id["value"] = None
                refresh_all()
                page.update()
            
            delete_btn = ft.ElevatedButton(
                "Удалить задачу",
                icon=ft.Icons.DELETE,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED_600,
                on_click=delete_task_click
            )
            
            # Первый контейнер: название задачи и кнопка удаления
            first_container = ft.Container(
                content=ft.Column([
                    ft.Text("Название задачи", size=16, weight=ft.FontWeight.BOLD),
                    title_field,
                    delete_btn
                ], spacing=10, expand=False),
                padding=15,
                border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_300))
            )
            
            # Второй контейнер: коэффициент, описание
            second_container = ft.Container(
                content=ft.Column([
                    ft.Text("Детали задачи", size=16, weight=ft.FontWeight.BOLD),
                    coefficient_dropdown,
                    description_field
                ], spacing=10, expand=True),
                padding=15,
                expand=True
            )
            
            details_container.content = ft.Column([
                first_container,
                second_container
            ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
            details_container.visible = True
        else:
            # Очищаем содержимое и скрываем панель
            details_container.content = ft.Column([], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)
            details_container.visible = False
        
        page.update()
    
    def refresh_details_only():
        """Обновляет только детали задачи без пересоздания списка"""
        if selected_task_id["value"]:
            show_task_details(selected_task_id["value"])
        else:
            page.update()
    
    def refresh_all():
        """Обновляет все компоненты"""
        # Сохраняем выбранную задачу
        current_selected = selected_task_id["value"]
        
        # Обновляем данные
        tasks_data.clear()
        tasks_data.extend(data_manager.get_data().get("tasks", []))
        refresh_tasks_list()
        page.update()
        
        # Восстанавливаем выбранную задачу
        if current_selected:
            # Проверяем, что задача еще существует
            if any(t["id"] == current_selected for t in tasks_data):
                selected_task_id["value"] = current_selected
                show_task_details(current_selected)
            else:
                selected_task_id["value"] = None
                details_container.visible = False
        else:
            details_container.visible = False
        
        page.update()
    
    # Поле ввода новой задачи
    task_input = ft.TextField(
        hint_text="напишите что-нибудь",
        expand=True,
        on_submit=lambda e: add_task(e.control.value)
    )
    
    def add_task(title):
        """Добавляет новую задачу"""
        if not title or not title.strip():
            return
        
        task_id = str(uuid.uuid4())
        new_task = {
            "id": task_id,
            "title": title.strip(),
            "description": "",
            "completed": False,
            "coefficient": 1,
            "subtasks": []
        }
        
        tasks_data.append(new_task)
        data_manager.data["tasks"] = tasks_data
        data_manager.save()
        
        task_input.value = ""
        refresh_all()
    
    def refresh_tasks_list():
        """Обновляет список задач"""
        tasks_list.controls.clear()
        
        for task in tasks_data:
            task_card = create_task_card(task, data_manager, refresh_all, page, show_task_details, selected_task_id)
            tasks_list.controls.append(task_card)
        page.update()
    
    def add_task_click(e):
        """Обработчик кнопки добавления задачи"""
        add_task(task_input.value)
    
    # Кнопка добавления задачи
    add_button = ft.ElevatedButton(
        "Добавить",
        icon=ft.Icons.ADD,
        on_click=add_task_click
    )
    
    # Инициализация списка задач
    refresh_tasks_list()
    
    return ft.Container(
        content=ft.Row([
            # Центральная часть - поле ввода, кнопка и список задач
            ft.Container(
                content=ft.Column([
                    # Поле ввода и кнопка
                    ft.Row([
                        task_input,
                        add_button
                    ], spacing=10),
                    
                    # Список задач
                    tasks_list
                ], spacing=15, expand=True),
                padding=20,
                expand=True
            ),
            # Правая часть - детали задачи (показывается только при выборе)
            details_container
        ], spacing=0, expand=True),
        expand=True
    )


def create_task_card(task, data_manager, refresh_callback, page, show_details_callback, selected_task_id):
    """Создает карточку задачи"""
    task_id = task["id"]
    
    # Чекбокс выполнения с увеличенным размером и зеленым цветом при True
    def create_checkbox(value):
        checkbox = ft.Checkbox(
            value=value,
            scale=1.5,  # Увеличенный размер
        )
        if value:
            checkbox.fill_color = ft.Colors.GREEN_600
        return checkbox
    
    completed_checkbox = create_checkbox(task.get("completed", False))
    completed_checkbox.on_change = lambda e: toggle_task_completion(task_id, e.control.value, data_manager, refresh_callback, page)
    
    # Поле названия задачи (только для отображения, кликабельное)
    title_field = ft.Text(
        value=task.get("title", ""),
        size=16,
        weight=ft.FontWeight.BOLD if task_id == selected_task_id.get("value") else ft.FontWeight.NORMAL,
        expand=True
    )
    
    # Контейнер для подзадач
    subtasks_container = ft.Column(spacing=5)
    
    def load_subtasks():
        """Загружает подзадачи"""
        subtasks_container.controls.clear()
        tasks = data_manager.get_data().get("tasks", [])
        current_task = next((t for t in tasks if t["id"] == task_id), None)
        if current_task:
            subtasks = current_task.get("subtasks", [])
            for subtask in subtasks:
                subtask_row = create_subtask_row(
                    task_id,
                    subtask,
                    data_manager,
                    load_subtasks,
                    page
                )
                subtasks_container.controls.append(subtask_row)
    
    def add_subtask_click(e):
        """Добавляет новую подзадачу"""
        subtask_id = str(uuid.uuid4())
        new_subtask = {
            "id": subtask_id,
            "title": "",
            "completed": False
        }
        
        tasks = data_manager.get_data().get("tasks", [])
        for t in tasks:
            if t["id"] == task_id:
                if "subtasks" not in t:
                    t["subtasks"] = []
                t["subtasks"].append(new_subtask)
                break
        
        data_manager.data["tasks"] = tasks
        data_manager.save()
        load_subtasks()
        page.update()
    
    load_subtasks()
    
    # Кнопка добавления подзадачи
    add_subtask_btn = ft.TextButton(
        "Добавить подзадачу",
        icon=ft.Icons.ADD,
        on_click=add_subtask_click
    )
    
    # Обработчик клика на карточку
    def on_card_click(e):
        show_details_callback(task_id)
    
    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                # Заголовок и чекбокс
                ft.Row([
                    completed_checkbox,
                    ft.Container(
                        content=title_field,
                        expand=True,
                        on_click=on_card_click,
                        padding=5,
                        border_radius=5,
                        bgcolor=ft.Colors.BLUE_50 if task_id == selected_task_id.get("value") else None
                    )
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                
                # Подзадачи
                ft.Container(
                    content=ft.Column([
                        add_subtask_btn,
                        subtasks_container
                    ], spacing=5),
                    padding=ft.Padding(40, 0, 0, 0),
                    border=ft.Border(left=ft.BorderSide(2, ft.Colors.BLUE_200))
                )
            ], spacing=10),
            padding=15,
            on_click=on_card_click
        ),
        margin=ft.Margin(0, 0, 0, 10)
    )


def create_subtask_row(task_id, subtask, data_manager, refresh_callback, page):
    """Создает строку подзадачи"""
    subtask_id = subtask["id"]
    
    def toggle_subtask(e):
        """Переключает состояние подзадачи"""
        tasks = data_manager.get_data().get("tasks", [])
        for task in tasks:
            if task["id"] == task_id:
                for st in task.get("subtasks", []):
                    if st["id"] == subtask_id:
                        st["completed"] = e.control.value
                        break
                break
        data_manager.data["tasks"] = tasks
        data_manager.save()
        refresh_callback()
        page.update()
    
    def update_subtask_title(e):
        """Обновляет название подзадачи"""
        tasks = data_manager.get_data().get("tasks", [])
        for task in tasks:
            if task["id"] == task_id:
                for st in task.get("subtasks", []):
                    if st["id"] == subtask_id:
                        st["title"] = e.control.value
                        break
                break
        data_manager.data["tasks"] = tasks
        data_manager.save()
    
    def delete_subtask(e):
        """Удаляет подзадачу"""
        tasks = data_manager.get_data().get("tasks", [])
        for task in tasks:
            if task["id"] == task_id:
                task["subtasks"] = [st for st in task.get("subtasks", []) if st["id"] != subtask_id]
                break
        data_manager.data["tasks"] = tasks
        data_manager.save()
        refresh_callback()
        page.update()
    
    # Чекбокс с увеличенным размером и зеленым цветом при True
    checkbox_value = subtask.get("completed", False)
    subtask_checkbox = ft.Checkbox(
        value=checkbox_value,
        scale=1.3,  # Увеличенный размер
    )
    if checkbox_value:
        subtask_checkbox.fill_color = ft.Colors.GREEN_600
    subtask_checkbox.on_change = toggle_subtask
    
    return ft.Row([
        subtask_checkbox,
        ft.TextField(
            value=subtask.get("title", ""),
            hint_text="Название подзадачи",
            expand=True,
            on_blur=update_subtask_title
        ),
        ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_size=16,
            tooltip="Удалить подзадачу",
            on_click=delete_subtask
        )
    ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER)


def toggle_task_completion(task_id, completed, data_manager, refresh_callback, page):
    """Переключает состояние выполнения задачи"""
    tasks = data_manager.get_data().get("tasks", [])
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = completed
            break
    data_manager.data["tasks"] = tasks
    data_manager.save()
    refresh_callback()
    page.update()


def update_task_field(task_id, field, value, data_manager, refresh_callback):
    """Обновляет поле задачи"""
    tasks = data_manager.get_data().get("tasks", [])
    for task in tasks:
        if task["id"] == task_id:
            task[field] = value
            break
    data_manager.data["tasks"] = tasks
    data_manager.save()
    if refresh_callback:
        refresh_callback()