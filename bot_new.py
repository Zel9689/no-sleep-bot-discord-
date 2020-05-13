#限制utc輸入不符合規定
import os
import time
import discord
from threading import Timer
from dotenv import load_dotenv
from discord.ext import commands
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='ns ')

#obj: id utc exp stack 只換指定obj的值
def only_change(File, text, obj, value): #File:str text:str obj:str value:str
    content = read(File)
    x = text.split('\t')
    Id = x[0]
    Utc = x[1]
    Exp = x[2]
    Stack = x[3]
    if(obj == 'id'):
        Id = value
    elif(obj == 'utc'):
        Utc = value
    elif(obj == 'exp'):
        Exp = value
    elif(obj == 'stack'):
        Stack = value
    text_new = Id + '\t' + Utc + '\t' + Exp + '\t' + Stack + '\t' + '\n'
    #這行不知道是三小 List的replace小方法
    content = [text_new if x == text else x for x in content]
    write(File, content)
def set_UTC(user, msg):
    flag = False
    File = 'info.txt'
    content = read(File)
    Utc = msg.content[3:len(msg.content)]
    Exp = '0'
    Stack = '0'
    text = str(user.id) + '\t' + Utc + '\t' + Exp + '\t' + Stack + '\t' + '\n'
    for i in content:
        if(str(user.id) in i):
            #進來代表已經有資料
            only_change(File, i, 'utc', Utc)
            flag = True
            break
    #沒資料的話
    if(flag == False):
        content.append(text)
        write(File, content)
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
    File = 'info.txt'
    content = read(File)
    L = -1
    for i in content:
        if(str(user.id) in i):
            L = i.split('\t')
            break
    return L
def check_cd():#check cooldown
    t = Timer(15, check_online)
    t.start()

def check_online():
    check_cd()
    File = 'info.txt'
    content = read(File)
    for i in content:
        text = i.split('\t')
        for j in bot.guilds:
            user = discord.utils.find(lambda g: g.id==eval(text[0]), j.members)
            #進來代表至少找到一個他在線上的證據
            if(user != None and \
                (user.status.value == 'online' or user.web_status.value == 'online' \
                    or user.mobile_status.value == 'online' \
                        or (user.voice != None and user.voice.afk == False)\
                )\
              ):
                print(user.display_name,'wow') #wow
                Utc = text[1]
                h = time.gmtime().tm_hour + eval(Utc)
                if(h > 24):
                    h = h - 24
                elif(h < 0):
                    h = h + 24
                if(h>=0 and h<24): #哪個時間內可以增加stack
                    only_change(File, i, 'stack', str(int(text[3])+1))
                    exp_add(user.id)
                break
#還不會動    
def save_time():
    UTC_time = str([time.gmtime().tm_year, time.gmtime().tm_mon, time.gmtime().tm_mday, time.gmtime().tm_hour, time.gmtime().tm_min])
    text = UTC_time + Utc + ':00' + '\t' + '\n'
    path = './history/' + data[0] + '.txt'
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
    only_change('info.txt', text, 'exp', str(exp + expVal))


@bot.event
async def on_ready():
    print(bot.user.name, 'has connected to Discord!')
    UTC_time = [time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec]
    sec = 1800 - UTC_time[1]*60 - UTC_time[2]
    if(sec < 0):
        sec = 3600 - UTC_time[1]*60 - UTC_time[2]
    sec = 3
    t = Timer(sec, check_cd)
    t.start()
    check_cd()
@bot.command()
async def timezone(ctx):
    user = ctx.author
    await user.create_dm()
    await user.dm_channel.send(
        f'哈囉 {user.name}, 設定你的時區, 輸入：UTC(+or-)數字; e.g. UTC+8\n'
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
    await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
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
                    msg = f'{user.mention}還沒有想要變強'
                else:
                    msg = f'{user.mention}的資訊：\n\
UTC: {L[1]}\n\
EXP: {L[2]}\n\
疊加狀態: {L[3]}'
            else:
                msg = '找不到該位使用者'
        await ctx.channel.send(msg)

@bot.command()
async def history(ctx):
    pass

@bot.command()
async def rank(ctx):
    pass




















bot.run(TOKEN)