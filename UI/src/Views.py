import flet as ft
from datetime import datetime, timedelta
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


class HomeView(ft.View):
    def __init__(self, route):

        live_tab = ft.Tab(label="Live Trading")

        backtest_tab = ft.Tab(label="Backtesting")

        strategy_tab = ft.Tab(label="Strategy")

        fromDateText = ft.Text()
        toDateText = ft.Text()
        
        # TODO : Get strategies from database and populate dropdown
        strategyPicker = ft.DropdownM2(
                                width=220,
                                options=[
                                    ft.DropdownOption(
                                        "Strategy 1", "Strategy 1")
                                ]  # fetch strategies from database
                            )
        
        curPairPicker = ft.DropdownM2(
                                width=220,
                                options=[
                                    ft.DropdownOption("EURUSD", "EUR/USD"),
                                    ft.DropdownOption("AUDUSD", "AUD/USD"),
                                    ft.DropdownOption("GBPUSD", "GBP/USD")
                                ]
                            )
        
        timeframePicker = ft.DropdownM2(
                                width=220,
                                options=[
                                    ft.DropdownOption("15M", "15 Minutes"),
                                    ft.DropdownOption("1H", "1 Hour"),
                                    ft.DropdownOption("4H", "4 Hours"),
                                ] 
                            )

        def handle_fromDateChange(e):
            corrected_date = e.control.value + timedelta(days=1)
            fromDateText.value = corrected_date.strftime("%Y-%m-%d")

        def handle_toDateChange(e):
            corrected_date = e.control.value + timedelta(days=1)
            toDateText.value = corrected_date.strftime("%Y-%m-%d")

        self.fromDatePicker = ft.DatePicker(on_change=handle_fromDateChange)
        self.toDatePicker = ft.DatePicker(on_change=handle_toDateChange)
        # suffix text should be quote currency
        self.cashField = ft.TextField(
            value="10000", width=100)
        self.hedgingField = ft.Switch(
            value=False, tooltip="Whether to allow hedging in the backtest")
        self.spreadField = ft.TextField(
            value="0", width=100, tooltip="Spread to use in backtest")
        self.commissionField = ft.TextField(
            value="0", width=100, tooltip="Commission to use in backtest")
        self.tradeOnCloseField = ft.Switch(
            value=False, tooltip="Whether to only execute trades at the close of a candle")
        self.exclusiveOrdersField = ft.Switch(
            value=False, tooltip="Whether to only allow one open position at a time")

        controlMargin = ft.Margin().all(5)
        
        async def send_backtest_params(e):
            params = {
                "strategy" : strategyPicker.value,
                "symbol" : curPairPicker.value,
                "timeframe" : timeframePicker.value,
                "from_date" : fromDateText.value,
                "to_date" : toDateText.value,
                "cash" : float(self.cashField.value),
                "hedging" : self.hedgingField.value,
                "spread" : int(self.spreadField.value),
                "commission" : float(self.commissionField.value) / 100,
                "trade_on_close" : self.tradeOnCloseField.value,
                "exclusive_orders" : self.exclusiveOrdersField.value
            }
            # TODO : send these params to backend and fetch backtest results
            # Example placeholder - replace with actual API call
            
        async def open_strategy_builder(e):
            await e.page.push_route("/strategy_builder")

        backtest_container = ft.Container(
            content=ft.Row(controls=[
                ft.Column(
                    controls=[
                        ft.Text("Backtesting Center", size=36,
                        weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT),
                        ft.Row(controls=[
                            ft.Text("Strategy: "),
                            strategyPicker
                        ], margin=controlMargin),
                        ft.Row(controls=[
                            ft.Text("Currency Pair: "),
                            curPairPicker
                        ], margin=controlMargin),
                        ft.Row(controls=[
                            ft.Text("Timeframe: "),
                            timeframePicker
                        ], margin=controlMargin),
                        ft.Row(controls=[
                            ft.Text("From: "),
                            fromDateText,
                            ft.Button(content='Pick Date', icon=ft.Icons.CALENDAR_MONTH,
                                      on_click=lambda e: self.page.show_dialog(self.fromDatePicker))
                        ], margin=controlMargin),
                        ft.Row(
                            controls=[
                                ft.Text("To: "),
                                toDateText,
                                ft.Button(content='Pick Date', icon=ft.Icons.CALENDAR_MONTH,
                                          on_click=lambda e: self.page.show_dialog(self.toDatePicker))
                            ],
                            margin=controlMargin
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "Cash(units of currency): ", tooltip="Amount of cash to backtest with"),
                                self.cashField
                            ]
                        ),
                        ft.Button("Run Backtest", margin=controlMargin, on_click= send_backtest_params),
                        # send data to backend and fetch results
                        ft.Text("Results", size=30)
                        # Chart and backtest result table here
                    ]
                ),
                ft.Column(controls=[
                    ft.Container(height=40),
                    ft.Row(controls=[
                        ft.Text(
                            "Hedging: ", tooltip="Whether to allow hedging in the backtest"),
                        self.hedgingField
                    ]),
                    ft.Row(controls=[
                        ft.Text("Spread(Pips): ", tooltip="Spread to use in backtest"),
                        self.spreadField
                    ]),
                    ft.Row(controls=[
                        ft.Text("Commission(%): ",
                                tooltip="Commission to use in backtest"),
                        self.commissionField
                    ]),
                    ft.Row(controls=[
                        ft.Text(
                            "Trade on Close: ", tooltip="Whether to only execute trades at the close of a candle"),
                        self.tradeOnCloseField
                    ]),
                    ft.Row(controls=[
                        ft.Text(
                            "Exclusive Orders: ", tooltip="Whether to only allow one open position at a time"),
                        self.exclusiveOrdersField
                    ])
                ])
            ])
        )

        strategy_container = ft.Container(
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Row(controls=[
                        ft.Text("Strategy Center", size=36, weight=ft.FontWeight.BOLD,
                                align=ft.Alignment.CENTER_LEFT, expand=True),
                        ft.Button(content="New Strategy", icon=ft.Icons.BUILD, on_click=open_strategy_builder)
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
        
        accNameField = ft.TextField()
        accPassField = ft.TextField(password=True, can_reveal_password=True)
        statusText = ft.Text("Status : Not Connected", color=ft.Colors.RED)
        
        async def connect_broker(e):
            login_info = {
                "login" : accNameField.login,
                "password" : accPassField.value
            }
            token = await self.page.shared_preferences.get("token")
            headers = {
                'Content-Type' : 'application/json',
                'Authorization' : f'Bearer {token}'
            }
            response = requests.post("http://localhost:8000/connect", data=login_info, headers=headers)
            if response.status_code == 200:
                statusText.value = "Status : Connected"
                statusText.color = ft.Colors.GREEN
                e.page.update()
        
        live_container = ft.Container(
            content=ft.Row(controls=[
                ft.Text("Broker Login", size=30, weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT),
                ft.Column(controls=[
                    ft.Text("Account Name"),
                    accNameField,
                    ft.Text("Account Password"),
                    accPassField,
                    ft.Button("Login", on_click=connect_broker),
                    statusText
                ], align=ft.Alignment.CENTER)
            ])
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
                            backtest_container,
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
    
    stratNameField = ft.TextField(hint_text="Strategy Name", width=300)
    initTextField = ft.TextField(expand=True, multiline=True, min_lines=10, max_lines=20)
    nextTextField = ft.TextField(expand=True, multiline=True, min_lines=10, max_lines=20)
    calcIndicatorsTextField = ft.TextField(expand=True, multiline=True, min_lines=10, max_lines=20)
    
    async def save_strategy(e):
        strategy_code = {
            "name" : StrategyBuilderView.stratNameField.value,
            "init" : StrategyBuilderView.initTextField.value,
            "next" : StrategyBuilderView.nextTextField.value,
            "calc_indicators" : StrategyBuilderView.calcIndicatorsTextField.value
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
        
    
    builder = ft.Container(
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Strategy Builder)", size=36, weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT),
                stratNameField,
                ft.Button("Save Strategy", icon=ft.Icons.SAVE, align=ft.Alignment.CENTER_LEFT, on_click=save_strategy),
                ft.Text("Init", tooltip="Code to run when strategy is initialized", size=30, weight=ft.FontWeight.BOLD,
                        align=ft.Alignment.CENTER_LEFT),
                initTextField,
                ft.Text("Next", tooltip="Code to run on every tick/candle", size=30, weight=ft.FontWeight.BOLD,
                        align=ft.Alignment.CENTER_LEFT),
                nextTextField,
                ft.Text("Calculate Indicators", tooltip="Code to calculate indicators. Runs on every tick/candle before Next",
                        size=30, weight=ft.FontWeight.BOLD, align=ft.Alignment.CENTER_LEFT),
                calcIndicatorsTextField
            ]
        ),
        expand=True
    )
    
    
    
    def __init__(self, route):
        super().__init__(
            route=route,
            appbar=ft.AppBar(title=ft.Text("Strategy Builder")),
            controls=[self.builder],
            can_pop=False,
            on_confirm_pop=self.ask_pop_permission
        )
        
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
