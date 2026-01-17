"""
Модуль трекера привычек
"""
import flet as ft
import uuid


def create_habit_tracker_page(page, data_manager):
    """Создает страницу трекера привычек"""
    
    # Загрузка привычек из данных (используем список для обновления)
    habits_data = data_manager.get_data().get("habits", [])
    habits_data = list(habits_data)  # Создаем копию для работы
    
    # Контейнер для списка привычек
    habits_list = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
        expand=True
    )
    
    def refresh_habits_list():
        """Обновляет список привычек"""
        # Обновляем данные из менеджера
        habits_data.clear()
        habits_data.extend(data_manager.get_data().get("habits", []))
        
        habits_list.controls.clear()
        
        for habit in habits_data:
            habit_row = create_habit_row(habit, data_manager, refresh_habits_list, page)
            habits_list.controls.append(habit_row)
    
    def create_habit_click(e):
        """Создает новую привычку"""
        habit_id = str(uuid.uuid4())
        new_habit = {
            "id": habit_id,
            "name": "Новая привычка",
            "count": 0
        }
        
        # Добавляем напрямую в менеджер данных
        habits = data_manager.get_data().get("habits", [])
        habits.append(new_habit)
        data_manager.data["habits"] = habits
        data_manager.save()
        
        # Обновляем локальный список
        habits_data.clear()
        habits_data.extend(habits)
        
        refresh_habits_list()
        page.update()
    
    # Кнопка создания привычки
    create_button = ft.ElevatedButton(
        "Cоздать привычку",
        icon=ft.Icons.ADD,
        on_click=create_habit_click
    )
    
    # Инициализация списка привычек
    refresh_habits_list()
    
    return ft.Container(
        content=ft.Column([
            # Кнопка создания
            create_button,
            
            # Список привычек
            habits_list
        ], spacing=15, expand=True),
        padding=20,
        expand=True
    )


def create_habit_row(habit, data_manager, refresh_callback, page):
    """Создает строку привычки"""
    habit_id = habit["id"]
    name_field_ref = ft.Ref[ft.TextField]()
    
    def toggle_habit_completion(e):
        """Обрабатывает нажатие на галочку - увеличивает счетчик"""
        habits = data_manager.get_data().get("habits", [])
        for h in habits:
            if h["id"] == habit_id:
                h["count"] = h.get("count", 0) + 1
                break
        data_manager.data["habits"] = habits
        data_manager.save()
        refresh_callback()
        page.update()
    
    def update_habit_name(e):
        """Обновляет название привычки"""
        habits = data_manager.get_data().get("habits", [])
        for h in habits:
            if h["id"] == habit_id:
                h["name"] = e.control.value
                break
        data_manager.data["habits"] = habits
        data_manager.save()
    
    def delete_habit(e):
        """Удаляет привычку"""
        habits = data_manager.get_data().get("habits", [])
        habits = [h for h in habits if h["id"] != habit_id]
        data_manager.data["habits"] = habits
        data_manager.save()
        refresh_callback()
        page.update()
    
    # Поле названия привычки
    name_field = ft.TextField(
        ref=name_field_ref,
        value=habit.get("name", ""),
        hint_text="Название привычки",
        expand=True,
        on_blur=update_habit_name
    )
    
    # Чекбокс для отметки выполнения (увеличенный размер, справа от названия)
    completion_checkbox = ft.Checkbox(
        scale=1.5,  # Увеличенный размер
        on_change=toggle_habit_completion,
        tooltip="Нажать для выполнения"
    )
    
    # Счетчик нажатий
    count_text = ft.Text(
        str(habit.get("count", 0)),
        size=18,
        weight=ft.FontWeight.BOLD,
        width=50,
        text_align=ft.TextAlign.CENTER
    )
    
    # Кнопка удаления
    delete_btn = ft.IconButton(
        icon=ft.Icons.DELETE,
        tooltip="Удалить привычку",
        on_click=delete_habit
    )
    
    # Обновление счетчика при изменении данных
    def update_count():
        habits = data_manager.get_data().get("habits", [])
        for h in habits:
            if h["id"] == habit_id:
                count_text.value = str(h.get("count", 0))
                break
    
    update_count()
    
    return ft.Card(
        content=ft.Container(
            content=ft.Row([
                name_field,
                completion_checkbox,
                count_text,
                ft.Text("раз", size=14),
                delete_btn
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15
        ),
        margin=ft.Margin(0, 0, 0, 10)
    )
