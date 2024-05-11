import flet as ft
from flet import icons
from yt_dlp import YoutubeDL as YDL


def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    video_status = ft.TextField(value="Aún no has descargado ningún video",read_only=True,border=ft.InputBorder.NONE)
    link_input = ft.TextField(label="Escribe el link de tu video", width=200)

    def progress_hook(d):
        print(d)
        if d['status'] == 'finished':
            video_status.value = "Video descargado"
            page.update()
        else:
            video_status.value = f"Descargando... {d['_percent_str']} a {d['_speed_str']}"
            page.update()
            
            
    def download_video(url):
        dl_opts = {
            'progress_hooks': [progress_hook],
        }
        with YDL(dl_opts) as ydl:
            ydl.download([url])

    def download(e):
        try:
            download_video(str(link_input.value))
        except:
            video_status.value = "Link inválido"
            page.update()

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
    page.add(
        ft.Row(
            [
                link_input,
                ft.IconButton(icons.CLOUD_DOWNLOAD, on_click=download),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                video_status
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )


ft.app(main)
