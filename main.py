import os.path
import flet as ft
from flet import icons
from yt_dlp import YoutubeDL

class VideoInfo:
    def __init__(
            self,
            video_link: str = '',
            video_title: str = '',
            status: str = 'Esperando',
            thumbnail_url='',
    ):
        self.video_link = video_link
        self.video_title = video_title
        self.status = status
        self.thumbnail_url = thumbnail_url

    def reset(self):
        self.video_link = ''
        self.video_title = ''
        self.status = 'Esperando'
        self.thumbnail_url = ''
        return self

    def set_thumbnail(self, thumbnails) -> str:
        for thumbnail in thumbnails:
            if 'resolution' not in thumbnail:
                continue
            if thumbnail['resolution'] != "1920x1080":
                continue
            self.thumbnail_url = thumbnail['url']
        return self.thumbnail_url

def main(page: ft.Page):
    def auto_update(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            page.update()
            return result

        return wrapper

    video_info: VideoInfo = VideoInfo()
    page.title = "Descarga de videos"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    status_text = ft.TextField(value=video_info.status, read_only=True, border=ft.InputBorder.NONE)
    progress_bar = ft.ProgressBar(value=100,width=400,opacity=0.5)
    status_bar = ft.Row(
        [
            progress_bar,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    video_status = ft.Row(
        [
            status_text,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    @auto_update
    def get_video_info(url:str):
        status_text.value = 'Buscando video'
        page.update()
        try:
            with YoutubeDL() as ydl:
                info = ydl.extract_info(url,download=False)
                thumbnails = info.get('thumbnails', [])
                thumbnail_url = video_info.set_thumbnail(thumbnails)
                add_thumbnail(thumbnail_url, info['title'])
                status_text.value = 'Video encontrado'
        except Exception:
            status_text.value = 'Error al buscar video'
            video_info.thumbnail_url = ''

    link_input = ft.TextField(label="Video link", width=200,on_change=lambda event: get_video_info(link_input.value))

    def get_directory_path(e):
        download(download_path=e.path)

    filepicker = ft.FilePicker(on_result=get_directory_path)

    @auto_update
    def progress_hook(d):
        if d['status'] == 'finished':
            status_text.value = 'Finalizó la descarga'
            progress_bar.value= 100
        else:
            progress_bar.value = float(d['_percent_str'].replace('%', '')) * 0.01
            status_text.value =f"Descargado: {d['_percent_str']} Velocidad: {d['_speed_str']}"

    @auto_update
    def add_thumbnail(thumbnail_url:str, title:str):
        if video_info.thumbnail_url:
            page.controls.pop()
        page.add(
            ft.Row(
                [
                    ft.Image(thumbnail_url, width=200, border_radius=ft.border_radius.all(10)),
                    ft.Text(title, width=200, overflow=ft.TextOverflow.ELLIPSIS, max_lines=4)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

    def download_video(url, path):
        with YoutubeDL({
            'outtmpl': fr"{path}\%(title)s.%(ext)s",
        }) as ydl:
            ydl.add_progress_hook(progress_hook)
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)
            filepath = ydl.get_output_path(filename=filename)
            if os.path.exists(filepath):
                status_text.value = 'Video descargado'
            ydl.build_format_selector(format_spec='bestvideo+bestaudio/best')
            ydl.download(url_list=[url])

    @auto_update
    def download(download_path):
        page.add(
            ft.Row(
                [
                    status_bar
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
        try:
            download_video(str(link_input.value), download_path)
        except Exception:
            status_text.value = "Error al descargar"
            video_info.thumbnail_url = ''

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(
                icon=icons.EXPLORE, label="Explore"
            ),
            ft.NavigationDestination(
                icon=icons.BOOKMARK, label="Saved"
            ),
        ]
    )

    page.overlay.extend([filepicker])
    page.add(
        ft.Row(
            [
                link_input,
                ft.IconButton(icons.CLOUD_DOWNLOAD, on_click=lambda _: filepicker.get_directory_path()),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                video_status
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [   ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )


ft.app(main)
