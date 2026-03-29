import os.path
import subprocess
import flet as ft
from platform import system
from flet import Colors
from flet_core.event import Event
from yt_dlp import YoutubeDL, DownloadError, SameFileError
from flet_core import TextField
from urllib.parse import urlparse
from flet.controls.material.icons import Icons

class Explorer:
    def __init__(
            self,
            path: str = '',
            system_name:str = system(),
            text_field: TextField = None,
    ):
        self.path = path
        self.system_name = system_name
        self.text_field = text_field

    def open_win(self):
        subprocess.Popen(fr"explorer.exe /select,{self.path}")
        return self

    def open_linux(self):
        subprocess.run(['xdg-open',self.path],check=True)
        return self

    def open_darwin(self):
        subprocess.run(['open',self.path],check=True)
        return self

    def open_by_os(self):
        if self.system_name == 'Windows':
            self.open_win()
        elif self.system_name == 'Linux':
            self.open_linux()
        elif self.system_name == 'Darwin':
            self.open_darwin()
        else:
            raise OSError(f'Sistema no soportado: {self.system_name}')

    def check_path(self):
        self.path = os.path.normpath(fr"{self.path}")
        if not os.path.exists(self.path):
            raise FileNotFoundError(f'{self.path} no existe')
        if not os.path.isfile(self.path):
            raise FileNotFoundError(f'{self.path} no existe')
        return self

    def open_path(self):
        try:
            self.check_path().open_by_os()
        except FileNotFoundError as e:
            print(e)
            self.text_field.value = e.args[0]
        except OSError as e:
            print(e)
            self.text_field.value = e.args[0]
        except subprocess.CalledProcessError as e:
            print(e)
            self.text_field.value = 'Error al abrir el explorador'
        finally:
            self.text_field.update()

class VideoInfo:
    def __init__(
            self,
            video_link: str = '',
            video_title: str = '',
            thumbnail_url='',
    ):
        self.video_link = video_link
        self.video_title = video_title
        self.thumbnail_url = thumbnail_url

    def reset(self):
        self.video_link = ''
        self.video_title = ''
        self.thumbnail_url = ''
        return self

    def find_thumbnail(self, thumbnails):
        for thumbnail in thumbnails:
            if 'resolution' not in thumbnail:
                continue
            if thumbnail['resolution'] != "1920x1080":
                continue
            self.thumbnail_url = thumbnail['url']
        return self


async def main(page: ft.Page):
    def auto_update(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            page.update()
            return result

        return wrapper

    video_info: VideoInfo = VideoInfo()
    page.title = "Descarga de videos"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    status_text = ft.TextField(value='Esperando', read_only=True, border=ft.InputBorder.NONE)
    explorer: Explorer = Explorer(text_field=status_text)
    progress_bar = ft.ProgressBar(width=400,visible=False,border_radius=10)
    filepicker = ft.FilePicker()
    video_thumbnail = ft.Image(src='',width=200, border_radius=10)
    video_title = ft.Text(width=200, overflow=ft.TextOverflow.ELLIPSIS, max_lines=4)
    open_button = ft.IconButton(icon=Icons.FOLDER_OPEN,on_click=lambda _: explorer.open_path(),disabled=True)
    video_container = ft.Container(
        ft.Row(
            [
                video_thumbnail,
                video_title,
                open_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=10,
        margin=10,
        alignment=ft.alignment.Alignment.CENTER,
        bgcolor=Colors.with_opacity(0.2,Colors.SHADOW),
        border_radius=15,
        visible=False,
    )

    @auto_update
    def get_video_info(url:str):
        status_text.value = 'Buscando video'
        progress_bar.visible = True
        page.update()
        try:
            with (YoutubeDL() as ydl):
                info = ydl.extract_info(url,download=False)
                thumbnails = info.get('thumbnails', [])
                video_info.find_thumbnail(thumbnails)
                add_video_card(video_info.thumbnail_url, info['title'])
                status_text.value = 'Video encontrado'
                download_button.disabled = False
        except DownloadError:
            status_text.value = 'Error al buscar video'
        finally:
            video_info.thumbnail_url = ''
            progress_bar.visible = False

    def on_input_change(event: Event):
        url = event.data
        if not url or not urlparse(url).scheme:
            status_text.value = 'Link inválido'
            return
        get_video_info(url)

    link_input = ft.TextField(label="Video link", width=350, border_radius=10, on_change=on_input_change)

    async def download_to_path(_:Event):
        path = await filepicker.get_directory_path(dialog_title='Selecicona la carpeta de descarga')
        if path is None:
            status_text.value = 'Cancelado'
            return
        download_video(str(link_input.value), str(path))

    download_button = ft.IconButton(Icons.CLOUD_DOWNLOAD,width=50, on_click=download_to_path,disabled=True)

    @auto_update
    def progress_hook(d):
        if d['status'] == 'finished':
            status_text.value = 'Finalizó la descarga'
            progress_bar.value = 100
        else:
            progress_bar.value = float(d['_percent_str'].replace('%', '')) * 0.01
            status_text.value = f"Descargado: {d['_percent_str']} Velocidad: {d['_speed_str']}"

    def add_video_card(thumbnail_url:str, title:str):
        video_thumbnail.src = thumbnail_url
        video_thumbnail.title = title
        video_title.value = title
        video_container.visible = True

    @auto_update
    def download_video(url, path):
        status_text.value = 'Iniciando descarga'
        progress_bar.visible = True
        page.update()
        try:
            with YoutubeDL({
                'outtmpl': fr"{path}\%(title)s.%(ext)s",
                'progress_hooks': [progress_hook],
            }) as ydl:
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                filepath = ydl.get_output_path(filename=filename)
                if os.path.exists(filepath):
                    status_text.value = 'Video ya descargado'
                    explorer.path = filepath
                    open_button.disabled = False
                    return
                ydl.build_format_selector(format_spec='bestvideo+bestaudio/best')
                explorer.path = filepath
                ydl.download(url_list=[url])
                open_button.disabled = False
                ydl.close()
        except SameFileError:
            status_text.value = 'Video ya descargado'
        except DownloadError:
            status_text.value = 'Error al descargar video'
        finally:
            progress_bar.visible = False

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=Icons.EXPLORE, label="Explore"
            ),
            ft.NavigationBarDestination(
                icon=Icons.BOOKMARK, label="Saved"
            ),
        ]
    )

    page.add(
ft.Row(
            [
                link_input,
                download_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                status_text
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Column(
            [
                ft.Row(
                    [
                    progress_bar
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                ft.Column(
                    [
                        video_container
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )


ft.run(main)
