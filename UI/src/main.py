import flet as ft
from Views import LoginView, HomeView, StrategyBuilderView

def main(page: ft.Page):
    
    def route_change():
            
        page.views.clear()
        page.views.append(LoginView("/login"))
        
        if page.route == "/home":
            page.views.append(HomeView("/home"))
        elif page.route == "/strategy_builder":
            page.views.append(HomeView("/home"))        
            page.views.append(StrategyBuilderView("/strategy_builder"))
        page.update()
    
    async def view_pop(e):
            if e.view is not None:
                page.views.remove(e.view)
                top_view = page.views[-1]
                await page.push_route(top_view.route)
                
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.title = "Prop Firm"
    
    route_change()

ft.run(main)
