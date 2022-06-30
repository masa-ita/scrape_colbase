import os
from threading import Thread

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import showerror

from selenium import webdriver
import chromedriver_binary
from scrape_colbase import get_url_list, download_files


class AsyncDownload(Thread):
    def __init__(self, driver, dir, url_list, prog_bar, log):
        super().__init__()

        self.driver = driver
        self.dir = dir
        self.url_list = url_list
        self.prog_bar = prog_bar
        self.log = log

    def run(self):
        if self.url_list:
            download_files(self.driver, self.dir, self.url_list, self.prog_bar, self.log)

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Colbase検索・一括ダウンロードプログラム（Chrome バージョン103.0.5060.53.0）')
        self.geometry('600x430')
        self.resizable(0, 0)

        self.create_header_frame()
        self.create_body_frame()
        self.create_footer_frame()

    def create_header_frame(self):

        self.header = ttk.Frame(self)
        # configure the grid
        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=10)
        self.header.columnconfigure(2, weight=1)

        # label directory
        self.label_dir = ttk.Label(self.header, text='ダウンロード先')
        self.label_dir.grid(column=0, row=0, sticky=tk.W)

        # entry directory
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(self.header,
                                   textvariable=self.dir_var,
                                   width=35)

        self.dir_entry.grid(column=1, row=0, sticky=tk.EW)

        # dir select button
        self.dir_select_button = ttk.Button(self.header, text='ダウンロード先選択')
        self.dir_select_button['command'] = self.handle_dir_select
        self.dir_select_button.grid(column=2, row=0, sticky=tk.W)

        # label keyword
        self.label_keyword = ttk.Label(self.header, text='検索キーワード')
        self.label_keyword.grid(column=0, row=1, sticky=tk.W)

        # entry keyword
        self.keyword_var = tk.StringVar()
        self.keyword_entry = ttk.Entry(self.header,
                                   textvariable=self.keyword_var,
                                   width=35)

        self.keyword_entry.grid(column=1, row=1, sticky=tk.EW)

        # download button
        self.download_button = ttk.Button(self.header, text='ダウンロード開始')
        self.download_button['command'] = self.handle_download
        self.download_button.grid(column=2, row=1, sticky=tk.W)

        # attach the header frame
        self.header.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=10)

    def handle_dir_select(self):
        out_dir = filedialog.askdirectory(initialdir=os.curdir)
        self.dir_var.set(out_dir)

    def handle_download(self):
        self.log.delete("1.0", "end")
        keyword = self.keyword_var.get()
        dir = self.dir_var.get()
        if keyword and dir:
            self.download_button['state'] = tk.DISABLED
            self.driver = webdriver.Chrome()
            url_list = get_url_list(self.driver, keyword)
            self.prog_bar["maximum"] = len(url_list)
            output_dir = os.path.join(dir, keyword)
            download_thread = AsyncDownload(self.driver, output_dir, url_list, self.count_var, self.log)
            download_thread.start()

            self.monitor(download_thread)
        elif not dir:
            showerror(title='Error',
                      message='ダウンロード先を指定してください。')
        elif not keyword:
            showerror(title='Error',
                      message='検索キーワードを入力してください。')
            

    def monitor(self, thread):
        if thread.is_alive():
            # check the thread every 100ms
            self.after(500, lambda: self.monitor(thread))
        else:
            self.download_button['state'] = tk.NORMAL

    def create_body_frame(self):
        self.body = ttk.Frame(self)

        # progress bar        
        self.count_var = tk.IntVar()
        self.count_var.set(0)
        self.prog_bar = ttk.Progressbar(
            self.body,
            mode = "determinate",
            variable = self.count_var,
        )
        self.prog_bar.grid(column=0, row=0, sticky=tk.EW)

        # text and scrollbar
        self.log = tk.Text(self.body, height=20)
        self.log.grid(column=0, row=1)

        scrollbar = ttk.Scrollbar(self.body,
                                  orient='vertical',
                                  command=self.log.yview)

        scrollbar.grid(column=1, row=1, sticky=tk.NS)
        self.log['yscrollcommand'] = scrollbar.set

        # attach the body frame
        self.body.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)

    def create_footer_frame(self):
        self.footer = ttk.Frame(self)
        # configure the grid
        self.footer.columnconfigure(0, weight=1)
        # exit button
        self.exit_button = ttk.Button(self.footer,
                                      text='終了',
                                      command=self.destroy)

        self.exit_button.grid(column=0, row=0, sticky=tk.E)

        # attach the footer frame
        self.footer.grid(column=0, row=2, sticky=tk.NSEW, padx=10, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()