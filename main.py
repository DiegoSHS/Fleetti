import flet as ft
import shutil
from flet import icons
from yt_dlp import YoutubeDL as YDL


def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    status_text = ft.TextField(value="Aún no has descargado ningún video",read_only=True,border=ft.InputBorder.NONE)
    progress_bar = ft.ProgressBar(width=400)
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
    
    link_input = ft.TextField(label="Escribe el link de tu video", width=200)

    def progress_hook(d):
        page.add(
            status_bar
        )
        if d['status'] == 'finished':
            status_text.value = "Video descargado"
            page.update()
        else:
            progress_bar.value = float(d['_percent_str'].replace('%','')) * 0.01
            status_text.value = f"Descargando... {d['_percent_str']} a {d['_speed_str']}"
            page.update()
        status_text.value = "Descargar otro video"
        page.controls.pop()
            
            
    def download_video(url):
        with YDL() as ydl:
            ydl.add_progress_hook(progress_hook)
            ydl.build_format_selector(format_spec='1080x1920+bestaudio/best')
            ydl.format_resolution(format='1080x1920+bestaudio/best')
            info = ydl.extract_info(url,download=False)
            filename = ydl.prepare_filename(info)
            ydl.download([url])
            oldpath = ydl.get_output_path()
            filepicker = ft.FilePicker(dialog_title="Selecciona la carpeta de descarga")
            result = filepicker.save_file(filename=filename,file_type="MEDIA")
            newpath = result.path
            shutil.move(oldpath,newpath)
            ##page.launch_url(path)
            thumbails = info.get('thumbnails', [])
            for thumb in thumbails:
                if 'resolution' not in thumb:
                    continue
                if thumb['resolution'] != "1920x1080":
                    continue
                page.add(
                    ft.Row(
                        [
                            ft.Image(thumb['url'], width=200, height=200,border_radius=ft.border_radius.all(10)),
                            ft.Text(info['title'],width=200,overflow=ft.TextOverflow.ELLIPSIS, max_lines=4)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                )
                page.update()
            

    def download(e):
        try:
            download_video(str(link_input.value))
        except:
            status_text.value = "Link inválido"
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
