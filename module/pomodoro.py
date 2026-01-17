import flet as ft
import asyncio
import time
import platform

if platform.system() == "Windows":
    import winsound
else:
    winsound = None


def create_pomodoro_page(page, data_manager):
    """Создает страницу помодоро (UI обновляется каждую секунду через page.run_task)"""

    # Состояние таймера в data_manager (не теряется при переключении вкладок)
    pomodoro = data_manager.data.setdefault(
        "pomodoro",
        {
            "running": False,
            "seconds": 25 * 60,
            "time_input_value": "25",
            "end_ts": None,  # timestamp окончания
        },
    )

    # Рантайм на уровне page (чтобы одна фоновая задача на всю сессию)
    if not hasattr(page, "_pomodoro_runtime"):
        page._pomodoro_runtime = {"task": None, "render": None}
    rt = page._pomodoro_runtime

    def format_time(seconds: int) -> str:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def play_sound_sync():
        if platform.system() == "Windows" and winsound:
            try:
                winsound.Beep(1000, 500)
                time.sleep(0.2)
                winsound.Beep(1000, 500)
            except Exception:
                pass

    def _is_mounted(ctrl: ft.Control) -> bool:
        # До монтирования ctrl.page может бросать RuntimeError
        return getattr(ctrl, "_Control__page", None) is not None

    # Поле ввода времени
    time_input = ft.TextField(
        hint_text="Введите время в минутах (например, 25)",
        value=str(pomodoro.get("time_input_value", "25")),
        width=200,
        text_align=ft.TextAlign.CENTER,
    )

    # Отображение таймера
    timer_display = ft.Text(
        "00:00",
        size=72,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    # Кнопки
    start_button = ft.ElevatedButton(
        "Начать",
        icon=ft.Icons.PLAY_ARROW,
        width=200,
        height=50,
    )
    reset_button = ft.ElevatedButton(
        "Сбросить",
        icon=ft.Icons.REFRESH,
        width=200,
    )

    def save_time_input_value(value: str):
        pomodoro["time_input_value"] = str(value)
        data_manager.save()

    time_input.on_change = lambda e: save_time_input_value(e.control.value)

    def recompute_remaining_if_running():
        """Пересчитать seconds по end_ts, если таймер запущен."""
        if pomodoro.get("running") and pomodoro.get("end_ts") is not None:
            remaining = int(pomodoro["end_ts"] - time.time())
            if remaining <= 0:
                pomodoro["seconds"] = 0
                pomodoro["running"] = False
                pomodoro["end_ts"] = None
                data_manager.save()
                return True  # finished
            else:
                pomodoro["seconds"] = remaining
        return False

    def render():
        # Если запущен — поддерживаем seconds актуальным
        finished = recompute_remaining_if_running()
        if finished:
            # звук лучше не блокировать UI
            try:
                asyncio.create_task(asyncio.to_thread(play_sound_sync))
            except Exception:
                # fallback: синхронно
                play_sound_sync()

        timer_display.value = format_time(int(pomodoro.get("seconds", 0)))

        if pomodoro.get("running"):
            start_button.text = "Пауза"
            start_button.icon = ft.Icons.PAUSE
        else:
            start_button.text = "Начать"
            start_button.icon = ft.Icons.PLAY_ARROW

        # Обновляем страницу, если контролы уже на странице
        if _is_mounted(timer_display) and _is_mounted(start_button):
            page.update()

    # Сохраняем render, чтобы фоновая задача всегда дергала актуальную отрисовку
    rt["render"] = render

    async def pomodoro_loop():
        """Фоновый цикл: тикает раз в секунду и обновляет UI (когда вкладка смонтирована)."""
        while True:
            await asyncio.sleep(1)
            if rt.get("render"):
                rt["render"]()

    # Запускаем фоновую задачу один раз на page
    if rt.get("task") is None or (hasattr(rt["task"], "done") and rt["task"].done()):
        rt["task"] = page.run_task(pomodoro_loop)

    def start_timer_click(e):
        # Пауза
        if pomodoro.get("running"):
            if pomodoro.get("end_ts") is not None:
                pomodoro["seconds"] = max(0, int(pomodoro["end_ts"] - time.time()))
            pomodoro["running"] = False
            pomodoro["end_ts"] = None
            data_manager.save()
            render()
            return

        # Старт
        if int(pomodoro.get("seconds", 0)) <= 0:
            try:
                minutes = int(time_input.value or pomodoro.get("time_input_value", "25"))
                if minutes <= 0:
                    minutes = 25
            except ValueError:
                minutes = 25
                time_input.value = "25"
                save_time_input_value("25")

            pomodoro["seconds"] = minutes * 60
            pomodoro["time_input_value"] = str(minutes)

        pomodoro["running"] = True
        pomodoro["end_ts"] = time.time() + int(pomodoro["seconds"])
        data_manager.save()
        render()

    def reset_timer_click(e):
        pomodoro["running"] = False
        pomodoro["seconds"] = 0
        pomodoro["end_ts"] = None
        data_manager.save()
        render()

    start_button.on_click = start_timer_click
    reset_button.on_click = reset_timer_click

    # Первичная отрисовка (без падения — update только после mount)
    render()

    return ft.Container(
        content=ft.Column(
            [
                ft.Text("Помодоро", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(
                    content=timer_display,
                    width=300,
                    height=300,
                    border_radius=150,
                    bgcolor=ft.Colors.BLUE_100,
                    alignment=ft.Alignment.CENTER,
                    margin=ft.Margin(0, 20, 0, 20),
                ),
                ft.Row(
                    [ft.Text("Время (минуты):", size=16), time_input],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Row(
                    [start_button, reset_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            expand=True,
        ),
        padding=20,
        expand=True,
)
