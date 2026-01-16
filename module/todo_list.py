"""
Модуль To-do list
"""
import flet as ft
import uuid


def create_todo_list_page(page, data_manager):
    """Создает страницу To-do list"""
    
    # Контейнер для списка задач (левый)
    tasks_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        expand=True
    )
    
    # Правый контейнер (пока пустой)
    right_container = ft.Container(
        content=ft.Column([], spacing=15, expand=True),
        padding=20,
        expand=True
    )
    
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
        
        # Добавляем напрямую в менеджер данных
        tasks = data_manager.get_data().get("tasks", [])
        tasks.append(new_task)
        data_manager.data["tasks"] = tasks
        data_manager.save()
        
        task_input.value = ""
        refresh_tasks_list()
        page.update()
    
    def show_task_details(task_id):
        """Показывает детали задачи в правом контейнере"""
        # Загружаем актуальные данные задачи
        tasks = data_manager.get_data().get("tasks", [])
        task = next((t for t in tasks if t["id"] == task_id), None)
        
        if task:
            # Название задачи
            title_text = ft.Text(
                value=task.get("title", ""),
                size=24,
                weight=ft.FontWeight.BOLD
            )
            
            # Выбор коэффициента приоритета
            coefficient_dropdown = ft.Dropdown(
                value=task.get("coefficient", 1),
                label="Коэффициент приоритета",
                options=[
                    ft.dropdown.Option(1, "1 - Срочно и важно"),
                    ft.dropdown.Option(2, "2 - Не срочно, но важно"),
                    ft.dropdown.Option(3, "3 - Срочно, но не важно"),
                    ft.dropdown.Option(4, "4 - Не срочно и не важно"),
                ],
                width=250
            )
            
            # Кнопка сохранения коэффициента
            def save_coefficient_click(e):
                """Сохраняет выбранный коэффициент"""
                coefficient_value = int(coefficient_dropdown.value) if coefficient_dropdown.value else 1
                update_task_coefficient(task_id, coefficient_value, data_manager)
                # Обновляем отображение для подтверждения сохранения
                show_task_details(task_id)
            
            save_coefficient_btn = ft.ElevatedButton(
                "Сохранить",
                icon=ft.Icons.SAVE,
                on_click=save_coefficient_click,
                width=150
            )
            
            # Поле для редактирования описания
            description_field = ft.TextField(
                value=task.get("description", ""),
                label="Описание задачи",
                hint_text="Введите описание задачи",
                multiline=True,
                min_lines=10,
                max_lines=20,
                expand=True,
                on_blur=lambda e: update_task_description(task_id, e.control.value, data_manager)
            )
            
            right_container.content = ft.Column([
                title_text,
                ft.Row([
                    coefficient_dropdown,
                    save_coefficient_btn
                ], spacing=10),
                ft.Divider(),
                ft.Text("Описание задачи", size=18, weight=ft.FontWeight.BOLD),
                description_field
            ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)
        else:
            right_container.content = ft.Column([], spacing=15, expand=True)
        
        page.update()
    
    def update_task_description(task_id, description, data_manager):
        """Обновляет описание задачи"""
        tasks = data_manager.get_data().get("tasks", [])
        for task in tasks:
            if task["id"] == task_id:
                task["description"] = description
                break
        data_manager.data["tasks"] = tasks
        data_manager.save()
    
    def update_task_coefficient(task_id, coefficient, data_manager):
        """Обновляет коэффициент приоритета задачи"""
        # Обновляем коэффициент напрямую в data_manager.data
        tasks = data_manager.get_data().get("tasks", [])
        # tasks = data_manager.data.get("tasks", [])
        for task in tasks:
            if task.get("id") == task_id:
                task["coefficient"] = coefficient
                break
        # Сохраняем данные в файл
        data_manager.data["tasks"] = tasks
        data_manager.save()
    
    def refresh_tasks_list():
        """Обновляет список задач"""
        tasks_list.controls.clear()
        
        # Загружаем задачи из менеджера
        tasks = data_manager.get_data().get("tasks", [])
        
        for task in tasks:
            task_card = create_task_card(task, data_manager, refresh_tasks_list, page, show_task_details)
            tasks_list.controls.append(task_card)
    
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
            # Левый контейнер - ввод и список задач
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
            # Вертикальный разделитель
            ft.VerticalDivider(width=1),
            # Правый контейнер (пока пустой)
            right_container
        ], spacing=0, expand=True),
        expand=True
    )


def create_task_card(task, data_manager, refresh_callback, page, show_details_callback):
    """Создает карточку задачи"""
    task_id = task["id"]
    
    # Чекбокс выполнения с увеличенным размером и зеленым цветом при True
    completed_checkbox = ft.Checkbox(
        value=task.get("completed", False),
        scale=1.5,  # Увеличенный размер
    )
    if task.get("completed", False):
        completed_checkbox.fill_color = ft.Colors.GREEN_600
    
    def on_checkbox_change(e):
        completed_checkbox.fill_color = ft.Colors.GREEN_600 if e.control.value else None
        toggle_task_completion(task_id, e.control.value, data_manager, refresh_callback, page)
    
    completed_checkbox.on_change = on_checkbox_change
    
    # Поле названия задачи
    title_field = ft.Text(
        value=task.get("title", ""),
        size=16,
        weight=ft.FontWeight.BOLD,
        expand=True
    )
    
    # Кнопка удаления задачи
    def delete_task_click(e):
        """Удаляет задачу"""
        tasks = data_manager.get_data().get("tasks", [])
        tasks = [t for t in tasks if t["id"] != task_id]
        data_manager.data["tasks"] = tasks
        data_manager.save()
        refresh_callback()
        page.update()
    
    delete_btn = ft.IconButton(
        icon=ft.Icons.DELETE,
        tooltip="Удалить задачу",
        on_click=delete_task_click
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
    
    # Обработчик клика на карточку задачи
    def on_task_click(e):
        """Обработчик клика на задачу - показывает детали в правом контейнере"""
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
                        on_click=on_task_click,
                        padding=5,
                        border_radius=5
                    ),
                    delete_btn
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
            on_click=on_task_click
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
    
    def on_subtask_checkbox_change(e):
        subtask_checkbox.fill_color = ft.Colors.GREEN_600 if e.control.value else None
        toggle_subtask(e)
    
    subtask_checkbox.on_change = on_subtask_checkbox_change
    
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
