import flet as ft
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
    
    
    def get_directory_path(e):
        download(download_path=e.path)
         
    filepicker = ft.FilePicker(on_result=get_directory_path)
    
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
        page.controls.pop()
    
    
    global added_thumbail    
    added_thumbail = False
    
    def add_thumbnail(thumb, title):
        global added_thumbail
        if added_thumbail:
            page.controls.pop()
        page.add(
                    ft.Row(
                        [
                            ft.Image(thumb, width=200,border_radius=ft.border_radius.all(10)),
                            ft.Text(title,width=200,overflow=ft.TextOverflow.ELLIPSIS, max_lines=4)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                )
        page.update()
        if not added_thumbail:
            added_thumbail = True
            
    def download_video(url,path):
        with YDL({
                'outtmpl': fr"{path}\%(title)s.%(ext)s",
            }) as ydl:
            ydl.add_progress_hook(progress_hook)
            info = ydl.extract_info(url,download=False)
            filename = ydl.prepare_filename(info)
            filepath = ydl.get_output_path(filename=filename)
            if ydl._ensure_dir_exists(filepath):
                status_text.value = "Video ya descargado"
            ydl.build_format_selector(format_spec='bestvideo+bestaudio/best')
            ydl.download(url_list=[url])
            thumbails = info.get('thumbnails', [])
            for thumb in thumbails:
                if 'resolution' not in thumb:
                    continue
                if thumb['resolution'] != "1920x1080":
                    continue
                add_thumbnail(thumb['url'],info['title'])
                
            

    def download(download_path):
        try:
            download_video(str(link_input.value),download_path)
        except Exception as e:
            print(e)
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
    )


ft.app(main)
