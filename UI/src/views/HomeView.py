import asyncio
import token

import flet as ft
from datetime import datetime, timedelta
import requests

class HomeView(ft.View):
    def __init__(self, route):

        live_tab = ft.Tab(label="Live Trading")

        backtest_tab = ft.Tab(label="Backtesting")

        strategy_tab = ft.Tab(label="Strategy")

        fromDateText = ft.Text()
        toDateText = ft.Text()
        
        # TODO : Get strategies from database and populate dropdown
        self.strategyPicker = ft.DropdownM2(
                                width=220,
                                options=[]
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
                "strategy" : self.strategyPicker.value,
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
                            self.strategyPicker
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
             
        self.datatable = ft.DataTable(columns=[ft.DataColumn(ft.Text("Name"), expand=True),
                                          ft.DataColumn(ft.Text("Actions"), expand=True)],
                                 rows=[], align=ft.Alignment.TOP_CENTER, expand=True)

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
                    self.datatable
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
        
    def did_mount(self):
        self.page.run_task(self.load_strategies)
        self.page.run_task(self.set_strategies)
        
    async def load_strategies(self):
        strategies = await self.fetch_strategies()
        self.datatable.rows = []
        for strat in strategies:
            self.datatable.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(strat["strategyName"])),
                    ft.DataCell(ft.Row(controls=[
                        ft.IconButton(ft.Icons.EDIT, on_click=lambda e, s=strat: print(f"Edit {s['strategyName']}")),
                        ft.IconButton(ft.Icons.DELETE, on_click=lambda e, s=strat: print(f"Delete {s['strategyName']}"))
                    ]))
                ])
            )
        self.page.update()
        
    async def set_strategies(self):
        strategies = await self.fetch_strategies()
        
        for strat in strategies:
            self.strategyPicker.options.append(ft.DropdownOption(strat["strategyName"], strat["strategyName"]))
        self.page.update()
    
    async def fetch_strategies(self):
        token = await self.page.shared_preferences.get("token")
        response = await asyncio.to_thread(requests.get,"http://localhost:8000/strategy", headers={"Authorization" : f"Bearer {token}"})

        if response.status_code == 200:
            strategies = response.json()
        else:
            strategies = []
        return strategies    