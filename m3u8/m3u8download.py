from Crypto.Cipher import AES
import os
import re
import requests

from concurrent.futures import ThreadPoolExecutor,as_completed

class M3U8():
    def __int__(self, path, name, url, port, ip, headers):
        self.path = path  # 储存地址
        self.name = name  # 视频名字
        self.url = url
        self.error = []
        if ip != None:
            self.ip = {'HTTP': f'http://{ip}:{port}'
                , 'HTTPS': f'https://{ip}:{port}'}#代理ip
        else:
            self.ip = None
        self.headers = headers#headers
        if os.path.exists(f'{self.path}'):
            pass
        else:
            os.mkdir(f'{self.path}')#生成文件夹
    #定义解密
    def Asejiemi(self,key,iv,date):
        crypto=AES.new(key.encode('utf-8'), AES.MODE_CBC,iv)#引入AES解密
        date_new=crypto.decrypt(date)
        return date_new#返回数据
    def requests_url(self,url,ip,headers):#请求
        if ip!=None and headers!=None:
            respone=requests.get(url,proxies=ip,headers=headers)
            return respone
        elif ip==None and headers!=None:
            respone=requests.get(url,headers=headers)
            return respone
        elif ip!=None and headers==None:
            respone=requests.get(url,proxies=ip)
            return respone
        elif ip==None and headers==None:
            respone=requests.get(url)
            return respone
    def analysis_date(self,url,respone,path,name):#分析链接
        if '#EXTINF'in respone.text:#如果#EXTINF存在则为最后一层
            with open(f'{path}/{name}_m3u81.txt','w',encoding='utf-8')as f:
                print(respone.text,file=f)
            with open(f'{path}/{name}_m3u81.txt','r',encoding='utf-8')as f:
                lst_mo=f.readlines()

            lst_ts=[]
            Key_lst=['1']#防止第一层判断出现问题，超出遍历范围
            for item in lst_mo:#随后一层的链接
                if '#EXT-X-KEY' in item:#寻找加密位置
                    if 'METHOD=NONE' in item:#排除一些小问题
                        continue
                    else:
                        if item==Key_lst[-1]:#判断key值相同否？防止最后变换
                            continue
                        else:
                            Key_lst.append(item)
                            lst_ts.append('Key')#打一个断点表明在这里之后开始换了一个Key
                elif '#'in item:
                    continue#防止还是链接
                else:
                    lst_ts.append(item)#将ts链接找出
            Key_lst.pop(0)#排除开始的1
            key_d_l=[]#存放一个字典
            if Key_lst != []:
                for Key in Key_lst:
                    Iv = re.findall('IV=0x(.*?)', Key)#找iv不同
                    code_type = re.findall('METHOD=(.*?),URI', Key)[0]#找加密方式
                    url_key_1 = re.findall('URI="(.*?)"', Key)#找key的链接
                    del lst_mo#释放一部分内存
                    if url != []:#防止不规范key不存在，还有一些小问题如果不存在那么就必须使用上一个key代解决
                        if 'http' in url[0]:
                            key=self.requests_url(url_key_1[0],self.ip,self.headers).text
                        else:
                            url_key_1 = url.replace(f'{url.split("/")[-1]}', f'{url_key_1[0].split("/")[-1]}')
                            key = self.requests_url(url_key_1,self.ip,self.headers).text
                    if Iv==[]:
                        Iv = b'0000000000000000'#iv不存在就是0，只是一般情况
                    else:
                        Iv=Iv[0]
                    dict10={'key':key,'iv':Iv,'code_type':code_type}
                    key_d_l.append(dict10)
            else:
                dict10={'key':None,'iv':None,'code_type':None}
                key_d_l.append(dict10)
            return key_d_l, lst_ts, url
        elif '#EXT' in respone.text:#解决第一层
            with open(f'{path}/{name}_m3u8.txt','w',encoding='utf-8')as f:
                print(respone.text,file=f)
            with open(f'{path}/{name}_m3u8.txt','r',encoding='utf-8')as f:
                lst=f.readlines()
            for item in lst:
                 if '.m3u8' in item:
                     url_m3u8_s=item
                     break
            if 'http' in url_m3u8_s:
                date_r=self.requests_url(item,self.ip,self.headers)
                return self.analysis_date(date_r,path,name)
            else:
                lst_1 = self.url.split('/')
                lst_1_1 =url_m3u8_s.split('/')
                for item1 in lst_1_1:
                    if item1 == 'hls':
                        if lst_1_1.index(item1) != 0:
                            url2 = self.url.replace(f'{lst_1[-1]}',
                                                    f'{lst_1_1[lst_1_1.index(item1) - 1]}/{lst_1_1[lst_1_1.index(item1)]}/{lst_1_1[lst_1_1.index(item1) + 1]}')
                        else:
                            url2 = self.url.replace(f'{lst_1[-1]}',
                                                    f'{lst_1_1[lst_1_1.index(item1)]}/{lst_1_1[lst_1_1.index(item1) + 1]}')
                        if "\n" in url2:
                            url2 = url2.replace('\n', '')
                date_r=self.requests_url(url2,self.ip,self.headers)
                return self.analysis_date(url2,date_r,path,name)
    def ts_get(self,key,iv,lst,code_type,url2,name):
        if code_type=='AES-128':
            error_lst =[]
            for url_ts_l in lst:
                try:
                    if 'http' in url_ts_l:
                        respone = self.requests_url(url_ts_l,self.ip,self.headers)
                    else:
                        url_ts_l = url2.replace(f'{url2.split("/")[-1]}', f'{url_ts_l.split("/")[-1]}')
                        if '\n' in url_ts_l:
                            url_ts_l = url_ts_l.replace('\n', '')
                        respone=self.requests_url(url_ts_l,self.ip,self.headers)#获取视频
                        i = 0
                        if respone.status_code !=200:
                            while i <5:
                                respone = self.requests_url(url_ts_l,self.ip,self.headers)
                                if respone.status_code==200:
                                    break
                                else:
                                    i += 1
                                    continue
                            if i == 5:
                                error_lst.append(url_ts_l)
                                continue
                                
                except:
                    error_lst.append(url_ts_l)
                    continue
                date_new=self.Asejiemi(key,iv,respone.content)

                with open(f'{self.path}/{name}.ts','ab+')as f:
                    f.write(date_new)
            return (0,error_lst)
        else:
            error_lst =[]
            for url_ts_l in lst:
                if 'http' in url_ts_l:
                    respone=self.requests_url(url_ts_l,self.ip,self.headers)
                else:
                    url_ts_l = url2.replace(f'{url2.split("/")[-1]}', f'{url_ts_l.split("/")[-1]}')
                    if '\n' in url_ts_l:
                        url_ts_l = url_ts_l.replace('\n', '')
                    respone=self.requests_url(url_ts_l,self.ip,self.headers)
                    i = 0
                    if respone.status_code !=200:
                        while i <5:
                                respone = self.requests_url(url_ts_l,self.ip,self.headers)
                                if respone.status_code==200:
                                    break
                                else:
                                    i += 1
                                    continue
                    if i == 5:
                        error_lst.append(url_ts_l)
                        continue
                with open(f'{self.path}/{name}.ts', 'ab+') as f:
                    f.write(respone.content)
            return (0,error_lst)
        
    def lst_Deal(self,num,lst):
        key=lst.count('Key')#分割列表
        if key!=0:
            Ase_lst = [[[]] for i in range(key)]
            num_1=-1
            for item in lst:
                if item=='Key':
                    num_1+=1
                else:
                    if len(Ase_lst[num_1][-1])<= int(len(lst)/num):
                        Ase_lst[num_1][-1].append(item)
                    else:
                        Ase_lst[num_1].append([])
                        Ase_lst[num_1][-1].append(item)
        elif key==0:
            i=int(len(lst)/num)+1
            Ase_lst=[[]]
            for it in range(0,num):
                if it*i>=len(lst)-i:
                    Ase_lst[-1].append(lst[it*i:])
                    break
                else:
                    Ase_lst[-1].append(lst[it*i:it*i+1*i])
        return Ase_lst#方便多任务开启多线程平均分配
    def base_run(self):
        respone_c=self.requests_url(self.url,self.ip,self.headers)
        dict_1_lst, lst_ts, url=self.analysis_date(self.url,respone_c,self.path,self.name)
        lst_ts_new=self.lst_Deal(1,lst_ts)
        for item in lst_ts_new:
            dict_k=dict_1_lst[lst_ts_new.index(item)]
            Key=dict_k['key']
            Iv=dict_k['iv']
            code_type=dict_k['code_type']
            for lst_ts_4 in item:
                code=self.ts_get(Key,Iv,lst_ts_4,code_type,url,self.name)
                if code[1] != []:
                    self.error.append(code[1])
        os.remove(f'{self.path}/{self.name}_m3u81.txt')
        os.remove(f'{self.path}/{self.name}_m3u8.txt')
        with open(f'{self.path}/{self.name}_error.txt','w',encoding='utf-8')as f:
            for item in self.error:
                for i in item:
                    print(i,'\n',file=f)
    def multi_process_run(self, num):
        respone_c = self.requests_url(self.url, self.ip, self.headers)
        key_d_l, lst_ts, url = self.analysis_date(self.url, respone_c, self.path, self.name)
        lst_ts_new=self.lst_Deal(num,lst_ts)
        pol = ThreadPoolExecutor(max_workers=10,thread_name_prefix='ts_download')
        num_part=0
        lst_tread=[]
        for item in lst_ts_new:
            dict_k=key_d_l[lst_ts_new.index(item)]
            Key=dict_k['key']
            Iv=dict_k['iv']
            code_type=dict_k['code_type']
            for lst_ts_4 in item:
                # ash=(Key,Iv,lst_ts_4,code_type,url,f'{self.name}_{num_part}')
                res = pol.submit(self.ts_get,key=Key,iv=Iv,lst=lst_ts_4,code_type=code_type,url2=url,name=f'{self.name}_{num_part}')
                lst_tread.append(res)
                num_part+=1
        for fueture in as_completed(lst_tread):
            data = fueture.result()
            if data[1] != []:
                    self.error.append(data[1])
        print('正在合并视频')
        with open(f'{self.path}/{self.name}.ts', 'ab+') as f:
            for i5 in range(num_part):
                try:
                    with open(f'{self.path}/{self.name}_{i5}.ts', 'rb') as f2:
                        f3 = f2.read()
                    f.write(f3)
                except FileNotFoundError:
                    print(f'没有找到{self.name}_{i5}')
                    continue
        for i5 in range(num_part):
            try:
                os.remove(f'{self.path}/{self.name}_{i5}.ts')
            except FileNotFoundError:
                continue
        if os.path.exists(f'{self.path}/{self.name}_m3u8.txt'):
            os.remove(f'{self.path}/{self.name}_m3u8.txt')
        if os.path.exists(f'{self.path}/{self.name}_m3u81.txt'):
            os.remove(f'{self.path}/{self.name}_m3u81.txt')
        with open(f'{self.path}/{self.name}_error.txt','w',encoding='utf-8')as f:
            for item in self.error:
                for i in item:
                    print(i,'\n',file=f)
if __name__ == '__main__':
    path1 = input('请输入下载文件的地址')
    name = input('文件名称')
    url = input('输入文件网址')
    ip = eval(input('代理ip,无则输入None'))
    port = eval(input('请输入代理ip对应的端口,无则输入None'))
    headers = eval(input('网址请求头(headers),无则输入None'))
    m3 = M3U8()
    m3.__int__(path1, name, url, port, ip, headers)
    download_type = input('请选择模式：1、普通2、多任务')
    if download_type == '1':
        m3.base_run()
    if download_type == '2':
        m3.multi_process_run(150)

# '''headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46'}'''
#解决数据修改
#解决了请求失败，数据会部分数据丢失的问题
#存在会卡死的问题
#解决卡死问题，但数据可能会丢失。回到原点，但是数据丢失概率降低,创建了将出错链接写入目标文件的程序
