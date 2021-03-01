import base64
import os
from urllib.parse import urlencode

from kivy.app import App
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
# from kivy.uix.camera import Camera
from kivy.core.camera import Camera
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
import time
import asyncio
import tempfile

import random

# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
from kivy.uix.settings import SettingsWithSidebar
from requests_toolbelt import MultipartEncoder

from settings import settings_json

Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        Button:
            text: 'Новый рулон'
            on_press: root.selector(1)
        Button:
            text: 'Зафиксировать брак'
            on_press: root.selector(2)
        Button:
            text: 'Рулон завершен'
            on_press: root.selector(3)
        Button:
            text: 'Настройки'
            on_press: app.open_settings()
        Button:
            text: 'Выход'
            on_press: app.get_running_app().stop()
            
<SelectWorkEquipment>:
    on_enter: self._on_enter(app)
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        ScrollView:            
            do_scroll_x: False
            do_scroll_y: True
            BoxLayout:
                id: scrolling
                orientation: 'vertical'
        BoxLayout:
            orientation: 'vertical'
            padding: 20
        Button:
            text: 'Отмена'
            size_hint_max_y: 100
            on_press: root.manager.current = 'menu'
            
<StartWorker>:
    on_enter: self._on_enter(app)
    on_leave: self._on_exit()
    lay_box: lay_box.__self__
    BoxLayout:
        id: lay_box
        first: first.__self__
        second: second.__self__
        orientation: 'vertical'
        padding: 20
        Label:
            text: 'Транспортный код:'
            size_hint_max_y: 100
            id: input_label        
        TextInput:
            id: input_value
            size_hint_max_y: 120
        ImageButton:
            id: first
            on_press: self.get_data_from_intcam(1)
            size_hint_min_y: 300
        ImageButton:  
            id:second
            size_hint_min_y: 300      
            on_press: self.get_data_from_intcam(2)
        Label:
            id: error_text
            text: ''
            size_hint_max_y: 100           
        Button:
            id: savebtn
            text: 'Сохранить'
            size_hint_max_y: 100
            on_press: root.save()        
        Button:
            text: 'Отмена'
            size_hint_max_y: 100
            on_press: root.manager.current = 'menu'


            
<EndWorker>:
    lay_box: lay_box.__self__
    BoxLayout:
        id: lay_box
        orientation: 'vertical'
        padding: 20
        Label:
            text: 'Количество циклов:'
            size_hint_max_y: 100
        TextInput:
            id: input_value
            input_filter: 'int'
            size_hint_max_y: 120
        Label:
            id: error_text
            text: ''                        
        Button:
            id: savebtn
            text: 'Сохранить'
            on_press: root.save()
            size_hint_max_y: 100       
        Button:
            text: 'Отмена'
            on_press: root.manager.current = 'menu'
            size_hint_max_y: 100
                    
<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 20    
        Button:
            text: 'Сохранить'
        Button:
            text: 'Отмена'
            on_press: root.manager.current = 'menu'
""")


class ImageButton(ButtonBehavior, Image):
    def get_data_from_cam(self, camera, index):
        if camera:
            temp = tempfile.gettempdir()
            path = f'{temp}/img_{index}.png'
            camera.export_to_png(path)
            self.source = path
            self.reload()

    def get_data_from_intcam(self, index):
        camera = self.parent.parent.camera
        if camera:
            camera.start()
            temp = tempfile.gettempdir()
            path = f'{temp}/img_{index}.png'
            camera.texture.save(path, flipped=False)
            print('camera', path)
            self.source = path
            self.reload()
            camera.play = False


# Declare both screens
class MenuScreen(Screen):
    def selector(self, menu_id):
        app = App.get_running_app()
        app.menu_id = menu_id
        app.screen_manager.current = 'select'


class SelectWorkEquipment(Screen):
    def _on_enter(self, instance_program):
        self.app = instance_program
        self.app.curent_worker = None
        main_box = self.children[0]
        sub_box = main_box.children[1]
        sub_box.clear_widgets()
        # self.modify_array(sub_box)
        print(self.ids)
        sub_box = self.ids.scrolling
        sub_box.add_widget(Label(text='Fetching...'))
        self.fetch_workers(sub_box)

    def react(self, id=None):
        self.app.curent_worker = id
        if self.app.menu_id == 1:
            self.app.screen_manager.current = 'start'
        elif self.app.menu_id == 2:
            self.app.screen_manager.current = 'bad'
        elif self.app.menu_id == 3:
            self.app.screen_manager.current = 'end'
        print('click', id)

    def show_error(self, sub_box, request, response):
        print(response)
        sub_box.clear_widgets()
        sub_box.add_widget(Label(text=f'{response.errno}: {response.strerror}'))

    def fetch_workers(self, sub_box):
        fetch_url = f'{self.app.config_url}/machines' if self.app.menu_id == 1 else f'{self.app.config_url}/actives'
        print(fetch_url)
        UrlRequest(
            fetch_url,
            lambda request, respone: self.modify_array(sub_box, request, respone),
            on_error=lambda req, resp: self.show_error(sub_box, req, resp),
            on_failure=lambda req, resp: self.show_error(sub_box, req, resp),
            timeout=360
        )

    def modify_array(self, sub_box, request=None, respone=None):
        # print('start async operation', request, respone)
        self.app.cookie = request.resp_headers['Set-Cookie']
        sub_box.clear_widgets()
        self.app.xsrf = respone['token']
        for index, value in enumerate(respone['machines_list']):
            if value:
                # print(f'create BTN{index} {value}')
                button = Button(text=f'{value["name"]}')
                button.worker_index = index
                button.on_release = self.create_onclick(value['pk'])
                button.size_hint_max_y = 200
                sub_box.add_widget(button)
        if not respone['machines_list']:
            label = Label(text='Нет свободных станков')
            sub_box.add_widget(label)
        # print('end async')

    def create_onclick(self, index):
        return lambda: self.react(index)


class SettingsScreen(Screen):
    pass


class Utils:
    def __init__(self):
        self.app = App.get_running_app()
        self.camera = None
        self.temp_path = tempfile.gettempdir()

    def save(self):
        if self.can_save():
            self.send_form()

    def can_save(self):
        if self.ids.input_value.text:
            if os.path.exists(f'{self.temp_path}/img_1.png') or os.path.exists(f'{self.temp_path}/img_2.png'):
                return True
        self.ids.error_text.text = 'Необходимо заполнить поле и снять хотя бы одну фотографию'
        return False

    def read_file(self, index):
        temp = tempfile.gettempdir()
        path = f'{temp}/img_{index}.png'
        with open(path, 'rb') as f:
            my_image = f.read()
        return (f'img_{index}.png',
                my_image,
                'image/png'
                )

    def read_file_encoded(self, index):
        print('READ FILE')
        path = f'{self.temp_path}/img_{index}.png'
        return base64.urlsafe_b64encode(open(path, 'rb').read())

    def get_form_fields(self):
        return {
            'value': self.ids.input_value.text,
            'file_1': self.read_file_encoded(1),
            'file_2': self.read_file_encoded(2),
            'worker_id': str(self.app.curent_worker),
            'csrfmiddlewaretoken': str(self.app.xsrf)
        }

    def get_form_url(self):
        return f'{self.app.config_url}/rolls_update'

    def get_ref_url(self):
        return f'{self.app.config_url}/machines'

    def sending_data(self, payload, url, refer_url):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',  # payload.content_type,
            # 'Content-Type': 'multipart/form-data',
            'X-CSRFToken': self.app.xsrf,
            'X-CSRF-TOKEN': self.app.xsrf,
            'Referer': refer_url
        }
        print(payload)
        print(url)
        body = urlencode(payload)
        UrlRequest(url,
                   method='POST',
                   req_headers=headers,
                   req_body=body,
                   verify=False,
                   timeout=360,
                   cookies=self.app.cookie,
                   on_success=self.return_to_main,
                   on_error=self.show_error,
                   on_failure=self.show_error
                   )

    def clear_images(self):
        for index in range(1, 3):
            path = f'{self.temp_path}/img_{index}.png'
            if os.path.exists(path):
                print('deleted ', path)
                os.remove(path)

    def return_to_main(self, *args):
        self.clear_images()
        App.get_running_app().screen_manager.current = 'menu'

    def show_error(self, a, error):
        print('ERROR', a, error)
        self.ids.error_text.text = f'ERROR: {a.resp_status}'

    def send_form(self):
        # payload = MultipartEncoder(
        #    fields=self.get_form_fields(),
        # )
        self.sending_data(self.get_form_fields(), self.get_form_url(), self.get_ref_url())


class StartWorker(Screen, Utils):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _on_enter(self, instance_program):
        self.app = instance_program
        # print('enter')
        if self.camera is None:
            self.camera = Camera()
        self.camera.play = True
        self.camera.start()
        self.clear_images()
        self.ids.first.texture = None
        self.ids.second.texture = None

    def _on_exit(self):
        # print('exit')
        # camera = self.ids['camera']
        self.camera.play = False
        self.camera.stop()


class BadWorker(StartWorker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ids.input_label.text = 'Кол-во метров брака'

    def get_form_url(self):
        return f'{self.app.config_url}/fix_defects'


class EndWorker(Screen, Utils):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_form_url(self):
        return f'{self.app.config_url}/rolls_end'

    def _on_enter(self, instance_program):
        self.app = instance_program

    def _on_exit(self):
        pass

    def can_save(self):
        if self.ids.input_value.text:
            return True
        return False

    def get_form_fields(self):
        return {
            'value': self.ids.input_value.text,
            'worker_id': str(App.get_running_app().curent_worker),
            'csrfmiddlewaretoken': str(App.get_running_app().xsrf)
        }


class TestApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        self.screen_manager = sm
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SelectWorkEquipment(name='select'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(StartWorker(name='start'))
        sm.add_widget(EndWorker(name='end'))
        sm.add_widget(BadWorker(name='bad'))

        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        # setting = self.config.get('appsettings', 'server_port')
        url = self.config.get('Network', 'server_address')
        port = self.config.get('Network', 'server_port')
        self.config_url = f'http://{url}:{port}'
        return sm

    def build_config(self, config):
        config.setdefaults('Network', {
            'server_port': 8000,
            'server_address': '127.0.0.1',
        })

    def build_settings(self, settings):
        settings.add_json_panel('Network',
                                self.config,
                                data=settings_json)

    def on_config_change(self, config, section,
                         key, value):
        url = self.config.get('Network', 'server_address')
        port = self.config.get('Network', 'server_port')
        self.config_url = f'http://{url}:{port}'


if __name__ in ('__main__', '__android__'):
    TestApp().run()
