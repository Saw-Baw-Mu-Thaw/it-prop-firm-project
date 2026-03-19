import flet as ft
from datetime import datetime, timedelta
import requests

class LoginView(ft.View):
    
    async def login(self,e):
            # send these values to backend api with requests
            # print('login function,', self.usernameField.value, ',', self.passwordField.value)
            username = self.usernameField.value
            password = self.passwordField.value
            
            # for testing purposes
            data = {'username' : username, 'password' : password}
            response = requests.post("http://localhost:8000/token", data=data)
            
            if response.status_code == 200:
                print('Access token: ',response.json().get("access_token"))
                await self.page.push_route("/home")
            
    def __init__(self, path):
        login_margin = ft.Margin(10, 5, 10, 5)
        
        self.usernameField = ft.TextField(hint_text="John Doe", text_size=18, align=ft.Alignment.CENTER_LEFT,
                                expand=True, margin=login_margin)
        self.passwordField = ft.TextField(password=True, can_reveal_password=True, text_size=18, 
                        align=ft.Alignment.CENTER_LEFT, expand=True, margin=login_margin)
            
    
        login_column = ft.Column([
            ft.Text("Prop Firm", size=35, weight=ft.FontWeight.BOLD,align=ft.Alignment.TOP_CENTER
                    ,margin=login_margin),
            ft.Text("Username", size=16, align=ft.Alignment.CENTER_LEFT, margin=login_margin,
                    weight=ft.FontWeight.BOLD),
            self.usernameField,
            ft.Text("Password", size=16, weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT,
                    margin=login_margin),
            self.passwordField,
            ft.Button("Login", align=ft.Alignment.CENTER, margin=ft.Margin(0,10,0,10),
                      on_click=self.login)
        ])
        
        bs = ft.BorderSide(width=5, color=ft.Colors.BLACK, style=ft.BorderStyle.SOLID)
        bRadius = ft.BorderRadius(25,25,25,25)
        
        container_border =ft.Border(top=bs, bottom=bs, left=bs, right=bs)
        login_container = ft.Container(margin=ft.Margin(50,30,50,10),
                                    content=login_column,
                                    border=container_border, border_radius=bRadius)
        
        
        
        super().__init__(
            route=path,
            controls=[
                login_container
            ]
        )
        
class HomeView(ft.View):
    def __init__(self, route):
        
        live_tab = ft.Tab(label="Live Trading")
        
        backtest_tab = ft.Tab(label="Backtesting")
        
        strategy_tab = ft.Tab(label="Strategy")
        
        fromDateText = ft.Text()
        toDateText = ft.Text()
        
        def handle_fromDateChange(e):
            corrected_date = e.control.value + timedelta(days=1)
            fromDateText.value = corrected_date.strftime("%Y-%m-%d")
            
        def handle_toDateChange(e):
            corrected_date = e.control.value + timedelta(days=1)
            toDateText.value = corrected_date.strftime("%Y-%m-%d")
        
        fromDatePicker = ft.DatePicker(on_change=handle_fromDateChange)
        toDatePicker = ft.DatePicker(on_change=handle_toDateChange)
        
        controlMargin = ft.Margin().all(5)
        
        backtest_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Backtesting Center", size=36, weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT),
                    ft.Row(controls=[
                        ft.Text("Strategy: "),
                        ft.DropdownM2(
                            width=220,
                            options=[
                                ft.DropdownOption("Strategy 1", "Strategy 1")
                            ] # fetch strategies from database
                        )
                    ], margin=controlMargin),
                    ft.Row(controls=[
                        ft.Text("Currency Pair: "),
                        ft.DropdownM2(
                            width=220,
                            options=[
                                ft.DropdownOption("EUR/USD", "EUR/USD"),
                                ft.DropdownOption("USD/JPY", "USD/JPY"),
                                ft.DropdownOption("GBP/USD", "GBP/USD")
                            ] # fetch available pairs from database
                        )
                    ], margin=controlMargin),
                    ft.Row(controls=[
                        ft.Text("From: "),
                        fromDateText,
                        ft.Button(content='Pick Date', icon=ft.Icons.CALENDAR_MONTH,
                                  on_click=lambda e : self.page.show_dialog(fromDatePicker))
                    ], margin=controlMargin),
                    ft.Row(
                        controls=[
                            ft.Text("To: "),
                            toDateText,
                            ft.Button(content='Pick Date', icon=ft.Icons.CALENDAR_MONTH,
                                      on_click=lambda e: self.page.show_dialog(toDatePicker))
                        ],
                        margin=controlMargin
                    ),
                    ft.Button("Run Backtest", margin=controlMargin, on_click=lambda e: print("Run backtest with selected parameters")),
                    # send data to backend and fetch results
                    ft.Text("Results", size=30)
                    # Chart and backtest result table here
                ]
            )
        )
        
        strategy_container = ft.Container(
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Row(controls=[
                        ft.Text("Strategy Center", size=36, weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT, expand=True),
                        ft.Button(content="New Strategy", icon=ft.Icons.BUILD)    
                    ]),
                    ft.Divider(color=ft.Colors.BLACK, thickness=3),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Name"), expand=True),
                            ft.DataColumn(ft.Text("Actions"), expand=True)
                        ],
                        rows=[
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text("Demo Strategy")), 
                                ft.DataCell(ft.Button("Delete"))
                                ]),
                        ],
                        align=ft.Alignment.TOP_CENTER,
                        expand=True
                    )
                ]
            )   
        )
        
        
        home_tab = ft.Tabs(
            selected_index=0,
            length=3,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[live_tab, backtest_tab, strategy_tab],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            ft.Container(
                                content=ft.Text("Live Trading Screen")
                            ),
                            backtest_container
                            ,
                            strategy_container
                        ]
                    )
                ]
            ),   
        )
        
        super().__init__(
            route=route,
            appbar=ft.AppBar(title=ft.Text("Home")),
            controls=[home_tab],
            can_pop=False
        )
        
class StrategyBuilderView(ft.View):
    pass