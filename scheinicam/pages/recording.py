from nicegui import ui, app, Client
from obscontroller import ObsController
from settings import Settings
from ui_object_container import UiObjectContainer
from datetime import datetime, timedelta

def recording_page(client: Client, obs_controller: ObsController, settings: Settings, ui_object_container: UiObjectContainer):
    '''Page for recording'''
    with ui.card().tight().classes("w-full"):
        with ui.expansion("Anleitung", icon="description").classes("w-full"):
            with ui.card_section():
                ui.markdown(open("assets/manual.md", encoding="utf-8").read())

    connecting_card = ui.card().classes("w-full")
    with connecting_card:
        with ui.row().style('align-items: center'):
            ui.spinner()
            ui.label('Verbinde mit OBS')
    connecting_card.bind_visibility_from(obs_controller, 'connected', backward=lambda x: not x)

    # display current time
    time_card = ui.card().classes("w-full")
    with time_card:
        clock_label = ui.label("").classes("text-xl")
        ui.timer(1, lambda: clock_label.set_text(datetime.now().strftime("Zeit: %H:%M:%S Uhr")))

    recording_card = ui.card().tight().classes("w-full")
    with recording_card:
        # Show Camera Preview
        preview = ui.html("").classes("w-full")
        preview.bind_content_from(ui_object_container, 'html_preview')
        with ui.card_section():
            with ui.row().style('align-items: center'):
                #ui.button('Zeitmarker setzen', on_click=set_time_marker)
                ui.spinner('pie', size='1em', color='red')
                ui.badge('Aufnahme läuft', color="red")
    recording_card.bind_visibility_from(obs_controller, 'recording')

    no_recording_card = ui.card().classes("w-full")
    with no_recording_card:
        ui.html(f"<p>Zur Zeit läuft keine Aufnahme.</p> <p>Die Aufnahme startet {settings.start_time.strftime('%H:%M')} Uhr und endet {settings.end_time.strftime('%H:%M')} Uhr automatisch.</p> <p>Die Aufnahmen können bis {settings.shutdown_time.strftime('%H:%M')} Uhr weiterhin heruntergeladen werden.</p> <p>Alle Aufnahmen werden automatisch nach {settings.delete_age.days} Tagen gelöscht.</p>")
    no_recording_card.bind_visibility_from(obs_controller, 'recording', backward=lambda x: not x)