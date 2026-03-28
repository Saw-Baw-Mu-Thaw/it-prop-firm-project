import flet as ft
import requests


class StrategyBuilderView(ft.View):
    def __init__(self, route):
        self.active_code_field: ft.TextField | None = None

        self.stratNameField = ft.TextField(hint_text="Strategy Name", width=300)
        self.initTextField = ft.TextField(
            expand=True,
            multiline=True,
            min_lines=10,
            max_lines=20,
            keyboard_type=ft.KeyboardType.MULTILINE,
            on_focus=self._set_active_code_field,
        )
        self.nextTextField = ft.TextField(
            expand=True,
            multiline=True,
            min_lines=10,
            max_lines=20,
            keyboard_type=ft.KeyboardType.MULTILINE,
            on_focus=self._set_active_code_field,
        )
        self.calcIndicatorsTextField = ft.TextField(
            expand=True,
            multiline=True,
            min_lines=10,
            max_lines=20,
            keyboard_type=ft.KeyboardType.MULTILINE,
            on_focus=self._set_active_code_field,
        )

        self.builder = ft.Container(
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Text("Strategy Builder)", size=36, weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT),
                    self.stratNameField,
                    ft.Button("Save Strategy", icon=ft.Icons.SAVE, align=ft.Alignment.CENTER_LEFT, on_click=self.save_strategy),
                    ft.Text("Init", tooltip="Code to run when strategy is initialized", size=30, weight=ft.FontWeight.BOLD,
                            align=ft.Alignment.CENTER_LEFT),
                    self.initTextField,
                    ft.Text("Next", tooltip="Code to run on every tick/candle", size=30, weight=ft.FontWeight.BOLD,
                            align=ft.Alignment.CENTER_LEFT),
                    self.nextTextField,
                    ft.Text("Calculate Indicators", tooltip="Code to calculate indicators. Runs on every tick/candle before Next",
                            size=30, weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT),
                    self.calcIndicatorsTextField
                ]
            ),
            expand=True
        )

        super().__init__(
            route=route,
            appbar=ft.AppBar(title=ft.Text("Strategy Builder")),
            controls=[self.builder],
            can_pop=False,
            on_confirm_pop=self.ask_pop_permission
        )

    async def save_strategy(self, e):
        strategy_code = {
            "name" : self.stratNameField.value,
            "init" : self.initTextField.value,
            "next" : self.nextTextField.value,
            "calc_indicators" : self.calcIndicatorsTextField.value
        }
        token = await e.page.shared_preferences.get("token")
        headers = {'Content-Type' : 'application/json',
                   'Authorization' : f'Bearer {token}'}
        response = requests.post("http://localhost:8000/strategy", json=strategy_code,
                                 headers=headers)
        
        if response.status_code == 200:
            print("Strategy saved successfully")
            await e.page.push_route('/home')
        else:
            print("Error saving strategy")
    
    def _set_active_code_field(self, e: ft.Event[ft.TextField]):
        self.active_code_field = e.control

    @staticmethod
    def _selection_offset_to_index(value: str, offset: int | None) -> int:
        if offset is None or offset < 0:
            return len(value)

        if "\r\n" not in value:
            return min(offset, len(value))

        # Flet selection offsets are LF-based, but Windows text can be stored as CRLF.
        logical = 0
        i = 0
        target = max(0, offset)
        while i < len(value) and logical < target:
            if value[i] == "\r" and i + 1 < len(value) and value[i + 1] == "\n":
                i += 2
            else:
                i += 1
            logical += 1

        return i

    async def _handle_keyboard(self, e: ft.KeyboardEvent):
        if not self.active_code_field or (e.key or "").lower() != "tab":
            return

        field = self.active_code_field
        value = field.value or ""
        selection = field.selection

        if selection is None:
            start = len(value)
            end = len(value)
        else:
            start_offset = min(selection.base_offset, selection.extent_offset)
            end_offset = max(selection.base_offset, selection.extent_offset)
            start = self._selection_offset_to_index(value, start_offset)
            end = self._selection_offset_to_index(value, end_offset)

        indent = "    "
        field.value = f"{value[:start]}{indent}{value[end:]}"
        caret = start + len(indent)
        field.selection = ft.TextSelection(base_offset=caret, extent_offset=caret)

        self.update()
        await field.focus()

    def did_mount(self):
        self.page.on_keyboard_event = self._handle_keyboard

    def will_unmount(self):
        if self.page and self.page.on_keyboard_event == self._handle_keyboard:
            self.page.on_keyboard_event = None

    async def ask_pop_permission(self,e):
        async def on_dlg_yes(e):
            self.page.pop_dialog()
            await self.confirm_pop(True)
            
        async def on_dlg_no(e):
            self.page.pop_dialog()
            await self.confirm_pop(False)
            
        dlg_modal = ft.AlertDialog(
            title=ft.Text("Unsaved Changes"),
            content=ft.Text("You have unsaved changes. Are you sure you want to leave?"),
            actions=[
                ft.TextButton("Yes", on_click=on_dlg_yes),
                ft.TextButton("No", on_click=on_dlg_no)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.show_dialog(dlg_modal)
