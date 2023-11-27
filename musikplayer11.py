import os 
import pickle #Menyimpan dan membaca objek Python ke dan dari file.
import tkinter as tk #Memanggil tkinter
from tkinter import filedialog #Menyediakan fungsi untuk memilih file atau direktori melalui dialog.
from tkinter import PhotoImage #Menyediakan gambar di dalam tkinter
from pygame import mixer #Digunakan untuk memutar file audio dalam aplikasi ini.
import random #Menyediakan fungsi-fungsi untuk menghasilkan bilangan acak.
from tkinter import ttk #Untuk tema-widget (Themed Tkinter). 
from PIL import Image, ImageTk #Mengolah dan menampilkan gambar
from ttkthemes import ThemedStyle #untuk menggunakan tema yang sudah ditentukan pada widget Tkinter.
import pygame #Menyediakan fungsionalitas untuk membuat game dan aplikasi multimedia.
import eyed3 #Membaca dan menulis metadata dari file audio MP3

# Class untuk mengatur pengaturan awal
class Player(tk.Frame): 
    def __init__(self, master=None):
        super().__init__(master,  bg="#8496a9")
        self.master = master
        self.pack()
        mixer.init()

        if os.path.exists('songs.pickle'):
            with open('songs.pickle', 'rb') as f:
                self.playlist = pickle.load(f)
        else:
            self.playlist = []

        self.current = 0
        self.paused = True
        self.played = False
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#343a40')

        self.create_frames()
        self.track_widgets()
        self.tracklist_widgets()
        self.bind_listbox_event() 
        
    # Membuat frame dalam gui   
    def create_frames(self): 
        # frame song track
        self.track = tk.LabelFrame(self, text='Song Track',
                                   font=("Scarlet Josephine", 20, "bold"),
                                   bg="#8496a9", fg="white", bd=5, relief=tk.FLAT, labelanchor="n") 
        self.track.config(width=400, height=300)
        self.track.grid(row=0, column=0, padx=0, pady=0)
        
        # frame track info (tambahan)
        self.additional_frame = tk.LabelFrame(self, text='Track Info',
                                              font=("Scarlet Josephine", 20, "bold"), 
                                              bg="#384B6B", fg="white", bd=5, relief=tk.FLAT, labelanchor="n")
        self.additional_frame.config(width=200, height=410)
        self.additional_frame.grid(row=0, column=1, pady=0, padx=5)
        self.additional_frame.grid_propagate(False)
        
         #frame playlist
        self.tracklist = tk.LabelFrame(self, text=f'PlayList - {str(len(self.playlist))}',
                                       font=("Scarlet Josephine", 20, "bold"),
                                       bg="#384B6B", fg="white", bd=5, relief=tk.FLAT, labelanchor="n")
        self.tracklist.config(width=170, height=350)
        self.tracklist.grid(row=0, column=2, pady=5, padx=15)
        
        # frame untuk track control
        self.controls = TrackControl(self, relief=tk.FLAT)
        self.controls.grid(row=2, column=0, pady=5, padx=10)
        
        # Mengganti gambar song track ketika lagu diputar
        track_info_image = 'musik4.png'
        original_image = Image.open(track_info_image)
        
        # Mengatur lebar yang diinginkan
        target_width = 150
        w_percent = (target_width / float(original_image.size[0]))
        target_height = int((float(original_image.size[1]) * float(w_percent)))
        resized_image = original_image.resize((target_width, target_height), Image.LANCZOS)

        # Konversi gambar untuk Tkinter
        track_info_image = ImageTk.PhotoImage(resized_image)

        # Tambahkan label gambar pada frame "Track Info"
        self.track_info_image_label = tk.Label(self.additional_frame, image=track_info_image, bg="#7c8184")
        self.track_info_image_label.image = track_info_image
        self.track_info_image_label.grid(row=0, column=0, padx=20, pady=10)
         
        # Tambahkan tombol untuk reset lagu
        self.reset_button = tk.Button(self.additional_frame, image=reset_img, command=self.reset, relief=tk.FLAT, bd=0, bg="#384B6B")
        self.reset_button.image = reset_img
        self.reset_button.grid(row=3, column=0, pady=5, sticky='w')
        
        # Tambahkan tombol untuk remove lagu
        self.remove_button = tk.Button(self.additional_frame, image=remove, command=self.remove_song, relief=tk.FLAT, bd=0, bg="#384B6B")
        self.remove_button.grid(row=2, column=0, pady=5, sticky='w')
        
        # Label untuk menampilkan informasi detail lagu yang dipilih
        self.song_info_label = tk.Label(self.additional_frame, text='', font=("Lucida Sans", 8), bg="#384B6B", fg="white")
        self.song_info_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='w')
        
    # Membuat dan mengatur widget
    def track_widgets(self):
        self.canvas = tk.Label(self.track, image=img)
        self.canvas.configure(width=400, height=330)
        self.canvas.grid(row=0, column=0)

        # Mengatur label track
        self.songtrack = tk.Label(self.track, font=("Lucida Sans", 12, "bold"),
                                  bg="#384B6B", fg="white")
        self.songtrack['text'] = 'Jafa Music Player App'
        self.songtrack.config(width=40, height=1)
        self.songtrack.grid(row=1, column=0, padx=10)
        
        # Mengatur frame slider 
        self.duration_slider_frame = tk.Frame(self.track)
        self.duration_slider_frame.grid(row=2, column=0, padx=10, pady=5)

        self.duration = tk.Label(self.duration_slider_frame, font=("lucida sans", 6),
                                 bg="white", fg="black")
        self.duration.config(width=10)
        self.duration.pack(side=tk.RIGHT)
        # Mengatur progress durasi dari slider ketika lagu di putar
        self.progress_slider = tk.Scale(self.duration_slider_frame, from_=0, to=100,
                                        orient=tk.HORIZONTAL, length=400, showvalue=False)
        self.progress_slider.pack(side=tk.LEFT)
        
    #  Membuat dan mengatur widget terkait dengan daftar trek musik, seperti scrollbar, kolom pencarian, tombol pencarian, dan daftar trek musik.
    def tracklist_widgets(self):
        self.scrollbar = tk.Scrollbar(self.tracklist, orient=tk.VERTICAL, width=15)
        self.scrollbar.grid(row=1, column=1, rowspan=5, sticky='ns')

        # Mengatur dan membuat search
        style = ttk.Style()
        style.configure("Search.TEntry", padding=(5, 5, 40, 5), font=("lucida sans", 12), foreground="#D8E4E7", background="#384B6B")

        self.search_entry = ttk.Entry(self.tracklist, style="Search.TEntry")
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        # Tombol search
        self.search_button = tk.Button(self.tracklist, image=search_img, command=self.search_songs, relief=tk.FLAT, bd=0, bg="#384B6B")
        self.search_button.grid(row=0, column=1, pady=5, sticky='w')
    
        self.list = tk.Listbox(self.tracklist, selectmode=tk.SINGLE,
                               yscrollcommand=self.scrollbar.set, selectbackground='sky blue', font=("lucida sans", 8))
        self.enumerate_songs()
        self.list.config(height=20, width=25)
        self.list.bind('<Double-1>', self.play_song)

        # Mengatur dan membuat scrollbar
        self.scrollbar.config(command=self.list.yview)
        self.list.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    
    # Mengikat daftar lagu yang dipilih  
    def bind_listbox_event(self):
        self.list.bind("<<ListboxSelect>>", self.on_song_select)

    # Memanggil lagu yang dipilih
    def on_song_select(self, event):
        selected_song_index = self.list.curselection()
        if selected_song_index:
            self.current = selected_song_index[0]
            self.show_song_info()
            
    # Mendapatkan informasi tentang lagu
    def get_audio_tags(self, song_path):
        audiofile = eyed3.load(song_path)
        if audiofile is not None:
            return {
                'title': audiofile.tag.title,
                'artist': audiofile.tag.artist,
                'album': audiofile.tag.album
            }
        else:
            return {} 
        
    # Memperbarui gambar lagu ketika di putar
    def update_song_image(self):
     if self.playlist and 0 <= self.current < len(self.playlist):
        song_path = self.playlist[self.current]
        tags = self.get_audio_tags(song_path)
        album_art_path = tags.get('album_art', None)

        if album_art_path and os.path.exists(album_art_path):
            image = Image.open(album_art_path)
            image = image.resize((400, 330), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            # Mengupdate gambar
            self.canvas.config(image=photo)
            self.canvas.image = photo
        else:    
            default_image = Image.open('musik4.png') 
            default_image = default_image.resize((400, 330), Image.LANCZOS)
            default_photo = ImageTk.PhotoImage(default_image)

            self.canvas.config(image=default_photo)
            self.canvas.image = default_photo
     
    # Mengatur ke pengaturan awal          
    def reset(self):
        # Menghentikan lagu yang sedang di putar
        mixer.music.stop()

        # Membersihkan playlist
        self.playlist = []
        self.list.delete(0, tk.END)
        
        # Membuka file 'songs.pickle' 
        with open('songs.pickle', 'wb') as f:
            pickle.dump(self.playlist, f)

        # Memperbarui tulisan pada playlist
        self.current = 0
        self.tracklist['text'] = f'PlayList - {str(len(self.playlist))}'

        # Membersihkan info lagu di frame track info
        self.song_info_label['text'] = ''

        # Membersihkan tulisan pada songtrack kembali ke default
        self.songtrack['text'] = 'Jafa Music Player App'

        self.canvas.config(image=None)

        # Memperbarui tombol play dan pause
        self.controls.pause['image'] = pause
        self.paused = True
        self.played = False
        
        # Memperbarui gambar pada song track menjadi gambar default
        default_image = Image.open('musik4.png') 
        default_photo = ImageTk.PhotoImage(default_image)
        self.canvas.config(image=default_photo)
        self.canvas.image = default_photo
    
    # Mengatur info lagu        
    def show_song_info(self):
        if self.playlist and 0 <= self.current < len(self.playlist):
            song_path = self.playlist[self.current]
            tags = self.get_audio_tags(song_path)
            title = tags.get('title', 'Unknown Title')
            artist = tags.get('artist', 'Unknown Artist')
            album = tags.get('album', 'Unknown Album')
            info_text = f'Title: {title}\nArtist: {artist}\nAlbum: {album}'
            self.song_info_label['text'] = info_text
            info_text = f'Title: {title}\nArtist: {artist}\nAlbum: {album}'
            # mengatur label info lagu
            info_label = tk.Label(self.additional_frame, text=info_text, font=("Lucida Sans", 10),
                                  bg="#7c8184", fg="white", justify=tk.CENTER, wraplength=180)
            
    # Mengatur remove lagu
    def remove_song(self):
     if self.playlist and 0 <= self.current < len(self.playlist):
        removed_song = self.playlist.pop(self.current)
        self.list.delete(self.current)
        
        with open('songs.pickle', 'wb') as f:
            pickle.dump(self.playlist, f)
        
        # Memperbarui tulisan pada playlist
        self.current = 0
        self.tracklist['text'] = f'PlayList - {str(len(self.playlist))}'
        
        # Menghentikan lagunya ketika sedang diputar
        mixer.music.stop()
        
        # Menampilkan info bahwa lagu sudah di remove
        self.song_info_label['text'] = ''

    # Mengatur label durasi trek
    def update_duration(self):
        if mixer.music.get_busy() and not self.paused:
            current_time = mixer.music.get_pos() // 1000
            formatted_time = self.convert_seconds_to_time(current_time)
            self.duration['text'] = f'{formatted_time} / {self.convert_seconds_to_time(int(self.song_duration))}'
            self.progress_slider.set(current_time)
        self.after(1000, self.update_duration)

    # Mengatur posisi pemutaran musik sesuai perubahan posisi slider
    def seek(self, event):
        new_position = self.progress_slider.get()
        new_position_ms = new_position * 1000
        mixer.music.set_pos(new_position_ms)
        self.progress_slider.bind("<ButtonRelease-1>", self.seek)

    # Mengonversi detik menjadi format waktu menit:detik.
    def convert_seconds_to_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f'{minutes:02d}:{seconds:02d}'

    # Mencari trek musik
    def search_songs(self):
        keyword = self.search_entry.get().lower()
        matching_songs = [song for song in self.playlist if keyword in song.lower()]

        self.list.delete(0, tk.END)
        for index, song in enumerate(matching_songs):
            self.list.insert(index, os.path.basename(song))

    # Meminta pengguna untuk memilih direktori yang berisi file musik
    def retrieve_songs(self):
        self.songlist = []
        directory = filedialog.askdirectory()
        for root_, dirs, files in os.walk(directory):
            for file in files:
                if os.path.splitext(file)[1] == '.mp3':
                    path = (root_ + '/' + file).replace('\\', '/')
                    self.songlist.append(path)

        with open('songs.pickle', 'wb') as f:
            pickle.dump(self.songlist, f)
        self.playlist = self.songlist
        self.tracklist['text'] = f'PlayList - {str(len(self.playlist))}'
        self.list.delete(0, tk.END)
        self.enumerate_songs()

    # Menampilkan daftar trek musik di daftar
    def enumerate_songs(self):
        for index, song in enumerate(self.playlist):
            self.list.insert(index, os.path.basename(song))

    # Memainkan trek musik yang dipilih dari daftar.
    def play_song(self, event=None):
        if event is not None:
            self.current = self.list.curselection()[0]
            for i in range(len(self.playlist)):
                self.list.itemconfigure(i, bg="white")

        print(self.playlist[self.current])
        mixer.music.load(self.playlist[self.current])
        mixer.music.play()
        self.song_duration = mixer.Sound(self.playlist[self.current]).get_length()
        self.progress_slider.config(to=self.song_duration)
        self.update_duration()
        self.progress_slider.set(0)

        self.songtrack['anchor'] = 'w'
        self.songtrack['text'] = os.path.basename(self.playlist[self.current])
        
        # Update info lagu
        self.show_song_info()
        # Update gambar lagu
        self.update_song_image()
        self.controls.pause['image'] = play
        self.paused = False
        self.played = True
        self.list.activate(self.current)
        self.list.itemconfigure(self.current, bg='sky blue')
        
        mixer.music.set_endevent(pygame.USEREVENT + 1)
        # Mengantrikan trek musik berikutnya
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        pygame.mixer.music.queue(self.playlist[self.current + 1]) 
        mixer.music.play()
        self.update_duration()
        self.progress_slider.set(0)
        
    # Mengatur pemutaran trek berikutnya setelah trek saat ini selesai.
    def play_next_song(self, event):
        if event.type == pygame.USEREVENT + 1:
            self.next_song()  
            self.show_song_info()

    # Menjeda atau melanjutkan pemutaran musik.
    def pause_song(self):
        if not self.paused:
            self.paused = True
            mixer.music.pause()
            self.controls.pause['image'] = pause
        else:
            if self.played == False:
                self.play_song()
            self.paused = False
            mixer.music.unpause()
            self.controls.pause['image'] = play

    # Memainkan trek musik sebelumnya 
    def prev_song(self):
        if self.current > 0:
            self.current -= 1
        else:
            self.current = 0
        self.list.itemconfigure(self.current + 1, bg='white')
        self.play_song()
        self.update_duration()

    # Memainkan trek musik berikutnya.
    def next_song(self):
        if self.current < len(self.playlist) - 1:
            self.current += 1
        else:
            self.current = 0
        self.list.itemconfigure(self.current - 1, bg='white')
        self.play_song()
        self.update_duration()
        
    # Memainkan trek musik secara acak.
    def shuffle_songs(self):
        if len(self.playlist) > 1:
            current_index = self.current
            while current_index == self.current:
                current_index = random.randint(0, len(self.playlist) - 1)

            self.current = current_index
            self.play_song()

    # Mengatur volume pemutaran musik.
    def change_volume(self, event=None):
        self.v = self.controls.volume.get()
        mixer.music.set_volume(self.v / 10)

# Class pembuatan GUI untuk aplikasi pemutar musik
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('980x500') # Mengatur ukuran awal jendela aplikasi
        self.wm_title('Jafa Music Palyer App') # Memberi judul pada jendela aplikasi
        self.configure(bg="#343a40") # Mengatur warna background jendela aplikasi

        global img, next_, prev, play, pause, shuffle, loadsongs, search_img, remove, reset_img
        
        img = PhotoImage(file='musik4.png')
        next_ = PhotoImage(file='next40.png')
        prev = PhotoImage(file='prev40.png')
        play = PhotoImage(file='pause40.png')
        pause = PhotoImage(file='play40.png')
        shuffle = PhotoImage(file='shuffle3.png')
        loadsongs = PhotoImage(file='addd.png')
        search_img = PhotoImage(file='search40.png') 
        remove = PhotoImage(file='remove20.png')
        reset_img = PhotoImage(file='reset20.png')
        
        # Mengurangi ukuran gambar
        next_ = next_.subsample(1)
        prev = prev.subsample(1)
        play = play.subsample(1)
        pause = pause.subsample(1)

        app = Player(self)
        app.mainloop()

# Class yang menyediakan kontrol trek musik di aplikasi
class TrackControl(tk.LabelFrame):
    def __init__(self, player, *args, **kwargs):
        super().__init__(player, *args, **kwargs)
        self.song_duration = 0
        self.player = player
        self.configure(bg="#8496a9")
        
        # Menyimpan nilai volume
        self.volume = tk.DoubleVar(self)
        style = ThemedStyle(self) # Menerapkan tema tkinter
        style.set_theme("equilux") 
        
        
        # Membuat frame dari volume
        style = ttk.Style()
        style.configure("Volume.Horizontal.TScale", sliderthickness=15, troughcolor="#1d3b55", background="#384B6B")
        self.slider = ttk.Scale(self, from_=0, to=10, orient=tk.HORIZONTAL, variable=self.volume, style="Volume.Horizontal.TScale")
        self.slider.set(8)
        mixer.music.set_volume(0.8)
        self.slider['command'] = self.player.change_volume
        self.slider.grid(row=0, column=5, padx=10, pady=5)
        
        self.controls_frame = tk.Frame(self)
        self.controls_frame.grid(row=1, column=0, pady=5)
        
        # Tombol loadsongs
        self.loadSongs = tk.Button(self, image=loadsongs, relief=tk.FLAT, bg="#8496a9")
        self.loadSongs['command'] = self.player.retrieve_songs
        self.loadSongs.grid(row=0, column=0, padx=10, pady=5)

        # Tombol shuffle
        self.shuffle = tk.Button(self, image=shuffle, relief=tk.FLAT, bg="#8496a9")
        self.shuffle['command'] = self.player.shuffle_songs
        self.shuffle.grid(row=0, column=1, padx=10, pady=5)

        # Tombol Previous
        self.prev = tk.Button(self, image=prev, relief=tk.FLAT, bg="#8496a9")
        self.prev['command'] = self.player.prev_song
        self.prev.grid(row=0, column=2, padx=10, pady=5)

        # Tombol pause
        self.pause = tk.Button(self, image=pause, relief=tk.FLAT, bg="#8496a9")
        self.pause['command'] = self.player.pause_song
        self.pause.grid(row=0, column=3, padx=10, pady=5)

        # Tombol next
        self.next = tk.Button(self, image=next_, relief=tk.FLAT, bg="#8496a9")
        self.next['command'] = self.player.next_song
        self.next.grid(row=0, column=4, padx=10, pady=5)

# Mengeksekusi program
if __name__ == "__main__":
    Application()
    
