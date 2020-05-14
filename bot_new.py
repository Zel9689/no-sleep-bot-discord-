#把讀取寫入提示放在動作前 更明確點
#修stack_clear
#修save_time -2會變負
import os
import time
import discord
from threading import Timer
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='ns ')
f_info = 'info.txt'
f_offcount = 'offcount.txt'
#File:哪個檔 text:該行的str index:該行第幾個資料 value:改成啥
def only_change(File, text, index, value): #File:str text:str index:int value:str
    content = read(File)
    x = text.split('\t')
    x.pop()
    text_new = ''
    for i in range(len(x)):
        if(i == index):
            text_new = text_new + value + '\t'
        else:
            text_new = text_new + x[i] + '\t' 
    text_new = text_new + '\n'
    #這行不知道是三小 List的replace小方法
    content = [text_new if x == text else x for x in content]
    write(File, content)
def set_UTC(user, msg):
    flag = False
    content = read(f_info)
    Utc = msg.content[3:len(msg.content)]
    Exp = '0'
    Stack = '0'
    text = str(user.id) + '\t' + Utc + '\t' + Exp + '\t' + Stack + '\t' + '\n'
    for i in content:
        if(str(user.id) in i):
            #進來代表已經有資料
            only_change(f_info, i, 1, Utc)
            flag = True
            break
    #沒資料的話
    if(flag == False):
        content.append(text)
        write(f_info, content)
def read(File):
    print('讀取檔案...')
    with open(File, 'a+') as f:
        f.seek(0)
        return f.readlines()
def write(File, content):
    print('寫入檔案...')
    with open(File, 'w+') as f:
        f.seek(0,2)
        f.writelines(content)
def getinfo(user):
    content = read(f_info)
    L = -1
    for i in content:
        if(str(user.id) in i):
            L = i.split('\t')
            break
    return L
def check_cd():#check cooldown
    t = Timer(1800, check_cd)
    t.start()
    status_L = check_online()
    stack_up(status_L)
    stack_clear(status_L)
    #exp_add()
    #lv_up()
def check_online():
    status_L = []
    content = read(f_info)
    for i in content:
        status = 'off' #假設使用者離線
        text = i.split('\t')
        for j in bot.guilds:
            user = discord.utils.find(lambda g: g.id==eval(text[0]), j.members)
            #進來代表至少找到一個他在線上的證據
            if(user != None and \
                (user.status.value == 'online' or user.web_status.value == 'online' \
                    or user.mobile_status.value == 'online' \
                        or (user.voice != None and user.voice.afk == False))):
                status = 'on' #刷新成上線
                print(user.display_name,'在線上') #wow
                break
        status_L.append(status)
    return status_L
def stack_up(status_L):
    content = read(f_info)
    for i in status_L:
        if(i=='on'):
            index = status_L.index(i)
            text = content[index]
            x = text.split('\t') #該行的List形式
            Utc = x[1]
            h = time.gmtime().tm_hour + eval(Utc)
            if(h >= 24):
                h = h - 24
            elif(h < 0):
                h = h + 24
            if((h>=0 and h<7) or x[3] != '0'): #哪個時間內可以增加stack
                print(x[0],'stack增加') #wow
                only_change(f_info, text, 3, str(int(x[3])+1))
def stack_clear(status_L):
    content = read(f_info)
    content2 = read(f_offcount)
    for i in status_L:
        flag = False
        index = status_L.index(i)
        text = content[index]
        x = text.split('\t') #該行的List形式
        stack = x[3]
        if(i == 'off' and stack != '0'): #符合離線&&stack有值
            for j in content2:
                if(x[0] in j): #檢查這個人有沒有已經在offcount.txt資料內
                    flag = True
                    text = j
                    x = text.split('\t')
                    break
        if(flag):
            times = x[1] + 1
            only_change(f_offcount, text, 1, '0')

#還不會動    
def save_time(id, mode):#'on' > 存上線 ; 'off' > 存下線
    UTC_time = [time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min]
    if(mode == 'on'):
        status = 'online'
    else:
        status = 'offline'
        UTC_time[3] = UTC_time[3] - 2
    File = 'info.txt'
    content = read(File)
    for i in content:
        if(str(id) in i):
            x = i.split('\t')
            Utc = x[1]
            break
    text = str(UTC_time) + Utc + ':00' + '\t' + status + '\t' + '\n'
    path = './history/' + str(id) + '.txt'
    with open(path, 'a') as f:
        f.seek(0,2)
        f.writelines(text)
    print('寫入檔案...')
def level_cal():
    return levelVal
def exp_add(id): #給我欲升經驗值的id
    File = 'info.txt'
    content = read(File)
    for i in content:
        if(str(id) in i):
            text = i
            x = i.split('\t')
            break
    stack = x[3]
    exp = eval(x[2])
    File = 'exp_rule.txt'
    content = read(File)
    if(int(stack) > 8):
        expVal =  eval(content[len(content)-1].split('\t')[0])
    else:
        for i in content:
            x = i.split()
            if(x[2] == stack):
                Uptime = x[1]
                expVal = eval(x[0])
                break
    only_change('info.txt', text, 2, str(exp + expVal))


def getdetail(user):
    File = './history/' + str(user.id) + '.txt'
    try:
        content = read(File)
    except:
        content = -1
    return content

async def send(channel, msg):
    channel = bot.get_channel(channel)
    await channel.send(msg)

@bot.event
async def on_ready():
    print(bot.user.name, 'has connected to Discord!')
    UTC_time = [time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec]
    sec = 1800 - UTC_time[1]*60 - UTC_time[2]
    if(sec < 0):
        sec = 3600 - UTC_time[1]*60 - UTC_time[2]
    t = Timer(sec, check_cd)
    t.start()
@bot.command()
async def timezone(ctx):
    user = ctx.author
    await user.create_dm()
    await user.dm_channel.send(
        f'哈囉 {user.name}, 不睡覺才會變強！加入變強的行列請設定你的時區！\n'
        f'設定你的時區, 輸入：UTC(+or-)數字; e.g. UTC+8\n'
        f'看看你在哪裡 https://upload.wikimedia.org/wikipedia/commons/8/88/World_Time_Zones_Map.png'
    )
    def check(m):
        response = m.content[0:3]
        return response.upper() == 'UTC' and m.channel == user.dm_channel
    msg = await bot.wait_for('message', check=check)
    set_UTC(user, msg)
    await user.dm_channel.send(f'你輸入了UTC{msg.content[3:len(msg.content)]}，你已經加入變強的行列')

@bot.command()
async def info(ctx, *args):
    #await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
    try:
        Users = ctx.message.guild.members
    except:
        await ctx.send('這個指令只能在頻道中使用')
    else:
        #error
        if(len(args)>1):
            msg = '你輸入了錯誤的格式, usage: ns info 使用者群暱稱'
        #ns info user.displayname
        else:
            L = [] #重置暫存器狀態
            user = 0
            #ns info
            if(len(args)==0):
                user = ctx.author
            else:
                for i in Users:
                    if(args[0] == i.display_name):
                        user = i
                        break
            if(user != 0):
                L = getinfo(user)
                if(L == -1):
                    msg = f'{user.mention}還沒有成為變強的一員\n\
輸入 ns timezone 設定你的時區 不睡覺才會變強'
                else:
                    msg = f'{user.mention}的資訊：\n\
UTC: {L[1]}\n\
EXP: {L[2]}\n\
疊加狀態: {L[3]}'
                    if(L[2] == '0'):
                        await ctx.channel.send(f'嫩 不睡覺才會變強')
            else:
                msg = '找不到該位使用者'
        await ctx.channel.send(msg)

@bot.command()
async def history(ctx, *args):
    try:
        Users = ctx.message.guild.members
    except:
        await ctx.send('這個指令只能在頻道中使用')
    else:
        #error
        if(len(args)>1):
            msg = '你輸入了錯誤的格式, usage: ns history 使用者群暱稱'
        #ns info user.displayname
        else:
            L = []
            user = 0
            #ns info
            if(len(args)==0):
                user = ctx.author
            else:
                for i in Users:
                    if(args[0] == i.display_name):
                        user = i
                        break
            if(user != 0):
                L = getdetail(user)
                if(L == -1):
                    msg = f'{user.mention}還沒有成為變強的一員\n\
輸入 ns timezone 設定你的時區 不睡覺才會變強'
                else:
                    data = ''
                    for i in L:
                        data = data + i.replace("\\","    ")
                    msg = f'{user.mention}的上線歷史紀錄：\n{data}'
            else:
                msg = '找不到該位使用者'
        await ctx.channel.send(msg)

@bot.command()
async def rank(ctx):
    pass

bot.run(TOKEN)