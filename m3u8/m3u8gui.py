import tkinter
import tkinter.filedialog
import m3u8download
import tkinter.messagebox
from multiprocessing import Process
#函数 

file_path=''
def filepath_get():
    global file_path
    file_path=tkinter.filedialog.askdirectory()
    print(file_path)
def base1_run():
    url=entry_url.get()
    name='视频'
    headers=entry_headers.get()
    if headers=='':
        headers=None
    ip=entry_ip.get()
    pron=entry_porn.get()
    if ip!=''and pron!='':
        pass
    else:
        ip=None
        pron=None
    m3=m3u8download.M3U8()
    m3.__int__(file_path,name,url,pron,ip,headers)
    tkinter.messagebox.showinfo(title='提示', message='已经开始下载了，请不要退出主程序')
    m3.base_run()
    tkinter.messagebox.showinfo(title='提示', message='已经开始下载完成')
def test(file_path,name,url,pron,ip,headers):
    m3=m3u8download.M3U8()
    m3.__int__(file_path,name,url,pron,ip,headers)
    m3.multi_process_run(100)

def mutiprosse():
    url=entry_url.get()
    name='视频'
    headers = entry_headers.get()
    if headers == '':
        headers = None
    ip = entry_ip.get()
    pron = entry_porn.get()
    if ip != '' and pron != '':
        pass
    else:
        ip = None
        pron = None
    args1 = (file_path,name,url,pron,ip,headers)
    print(args1)
    p = Process(target = test,args=args1)
    p.start()
    tkinter.messagebox.showinfo(title='提示',message='已经开始下载')
    #非阻塞形式
if __name__ == '__main__':
    #界面
    root=tkinter.Tk()
    root.title('m3u8下载器')
    root.geometry('700x700')
    label=tkinter.Label(root,text='m3u8下载器',font=('黑体',15),width=20)
    label_file=tkinter.Label(root,text='请选择文件保存地址:',font=('楷体',15),width=20)
    label_download_type=tkinter.Label(root,text='请选择下载模式',font=('楷体',15),width=20)
    label_url=tkinter.Label(root,text='请输入下载地址',font=('楷体',15),width=20)
    label_headers=tkinter.Label(root,text='请输入headers,无则不输入',font=('楷体',15),width=25)
    label_ip=tkinter.Label(root,text='请输入代理ip，无则不输入',font=('楷体',15),width=25)
    label_porn=tkinter.Label(root,text='请输入代理ip的端口，无则不输入',font=('楷体',15),width=25)
    entry_url=tkinter.Entry(width=30)
    entry_ip=tkinter.Entry(width=30)
    entry_porn=tkinter.Entry(width=30)
    entry_headers=tkinter.Entry(width=30)
    entry_url.place(relx=0.5,rely=0.2)
    entry_ip.place(relx=0.5,rely=0.3)
    entry_porn.place(relx=0.5,rely=0.4)
    entry_headers.place(relx=0.5,rely=0.5)
    label_url.place(relx=0.1,rely=0.2)
    label_ip.place(relx=0.1,rely=0.3)
    label_porn.place(relx=0.1,rely=0.4)
    label_headers.place(relx=0.1,rely=0.5)
    label_download_type.place(relx=0.1,rely=0.75)
    label_file.place(relx=0.1,rely=0.6)
    label.place(relx=0.4,rely=0.1)
    Button_d=tkinter.Button(root,text='多进程',command=mutiprosse)
    Button_l=tkinter.Button(root,text='单进程',command=base1_run)
    Button_file=tkinter.Button(root,text='文件',command=filepath_get)
    Button_file.place(relx=0.5,rely=0.6)
    Button_l.place(relx=0.3,rely=0.8)
    Button_d.place(relx=0.7,rely=0.8)
    root.mainloop()

