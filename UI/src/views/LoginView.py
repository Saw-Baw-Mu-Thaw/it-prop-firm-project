import flet as ft
import requests


class LoginView(ft.View):

    async def login(self, e):
        # send these values to backend api with requests
        # print('login function,', self.usernameField.value, ',', self.passwordField.value)
        username = self.usernameField.value
        password = self.passwordField.value

        # for testing purposes
        data = {'username': username, 'password': password}
        response = requests.post("http://localhost:8000/token", data=data)

        if response.status_code == 200:
            # print('Access token: ', response.json().get("access_token"))
            token = response.json().get("access_token")
            await self.page.shared_preferences.set("token", token)
            self.page.views.remove(self)
            await self.page.push_route("/home")
        else:
            self.login_failed()

    def login_failed(self):
        self.errorText.visible = True
        self.page.update()

    def __init__(self, path):
        login_margin = ft.Margin(10, 5, 10, 5)

        self.usernameField = ft.TextField(hint_text="John Doe", text_size=18, align=ft.Alignment.CENTER_LEFT,
                                          expand=True, margin=login_margin)
        self.passwordField = ft.TextField(password=True, can_reveal_password=True, text_size=18,
                                          align=ft.Alignment.CENTER_LEFT, expand=True, margin=login_margin)

        self.errorText = ft.Text("Error. Invalid username or password.", color=ft.Colors.RED, visible=False,
                                 align=ft.Alignment.CENTER, margin=ft.Margin(10, 5, 10, 5), bgcolor=ft.Colors.YELLOW)

        login_column = ft.Column([
            ft.Text("Prop Firm", size=35, weight=ft.FontWeight.BOLD,
                    align=ft.Alignment.TOP_CENTER, margin=login_margin),
            ft.Text("Username", size=16, align=ft.Alignment.CENTER_LEFT, margin=login_margin,
                    weight=ft.FontWeight.BOLD),
            self.usernameField,
            ft.Text("Password", size=16, weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT,
                    margin=login_margin),
            self.passwordField,
            ft.Button("Login", align=ft.Alignment.CENTER, margin=ft.Margin(0, 10, 0, 10),
                      on_click=self.login),
            self.errorText
        ])

        bs = ft.BorderSide(width=5, color=ft.Colors.BLACK,
                           style=ft.BorderStyle.SOLID)
        bRadius = ft.BorderRadius(25, 25, 25, 25)

        container_border = ft.Border(top=bs, bottom=bs, left=bs, right=bs)
        login_container = ft.Container(margin=ft.Margin(50, 30, 50, 10),
                                       content=login_column,
                                       border=container_border, border_radius=bRadius)

        super().__init__(
            route=path,
            controls=[
                login_container
            ]
        )

