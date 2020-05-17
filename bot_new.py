#Rank實作
#最高疊加紀錄
import os
import time
from operator import itemgetter
import discord
from threading import Timer
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime,timezone,timedelta
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='ns ')
f_info = 'info.txt'
f_offcount = 'offcount.txt'
f_rule = 'exp_rule.txt'
Lv_need = [38.5, 77] #Lv_need[0]升兩等所需經驗 Lv_need[1]升兩等所需經驗 升三等是前兩個相加
image = ['https://imgur.com/SOxeu7c','https://imgur.com/3AFdpJy','https://imgur.com/4wQUnw2','https://imgur.com/MzxV0eU',\
    'https://imgur.com/pP9apDr','https://imgur.com/yhBzoJ3','https://imgur.com/jlahFPB','https://imgur.com/lZXT4OC',\
        'https://imgur.com/cggySDj','https://imgur.com/nbsxbkz','https://imgur.com/SvvwaP3','https://imgur.com/ejFydUg',\
            'https://imgur.com/BBnxfLf','https://imgur.com/lZXT4OC','https://imgur.com/azIji74','https://imgur.com/fQYJ2EF',\
                'https://imgur.com/ZTOVvJR','https://imgur.com/MGxkUMa','https://imgur.com/rFoJGVt','https://imgur.com/6RjGgaU',\
                    'https://imgur.com/l2EIjLe','https://imgur.com/H7p7ycP','https://imgur.com/y5uaRDc','https://imgur.com/EWhgxvy']
TEST = True
Time_to_start = 1800 #設定幾分觸發(e.g. 想要時間XX點12分觸發 Time_to_start = 720)
Loop_time = 1800
Time_range = 7

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
    return text_new
def set_UTC(user, msg):
    flag = False
    content = read(f_info)
    Utc = msg.content[3:len(msg.content)]
    Exp = '0'
    Stack = '0'
    LV = '1'
    Rank = 'none'
    Dst = '0'
    High = '0'
    text = str(user.id) + '\t' + Utc + '\t' + Exp + '\t' + Stack + '\t' + LV + '\t' + Rank + '\t' + Dst + '\t' + High + '\t' + '\n'
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
    print(user.display_name, '設定UTC')
def set_DST(user, msg):
    content = read(f_info)
    for i in content:
        if(str(user.id) in i):
            if(msg.upper() == 'Y'):
                only_change(f_info, i, 6, '1')
                return False
            elif(msg.upper() == 'N'):
                only_change(f_info, i, 6, '0')
                return False
            else:
                return True
def read(File):
    with open(File, 'a+') as f:
        f.seek(0)
        return f.readlines()
def write(File, content):
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
    print(user.display_name, '資料被查詢')
    return L
def check_cd():#check cooldown
    t = Timer(Loop_time, check_cd)
    t.start()
    print('##檢查時間到了##')
    status_L = check_online()
    stack_up(status_L)
    stack_clear(status_L)
    lv_up()
    update_high()
    update_rank()
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
    for i in range(len(status_L)):
        if(status_L[i]=='on'):
            text = content[i]
            x = text.split('\t') #該行的List形式
            user = bot.get_user(int(x[0]))
            local_dt = gettime(user)
            h = local_dt.hour
            if((h>=0 and h<Time_range) or x[3] != '0'): #哪個時間內可以增加stack&exp_add
                print(user.display_name,'stack增加') #wow
                stack = str(int(x[3])+1)
                #exp_add的部分
                exp = float(x[2])
                expVal = stack_exp(stack)
                text_new = only_change(f_info, text, 3, stack)
                only_change(f_info, text_new, 2, str(round(exp + expVal, 1)))
                print(user.display_name, 'exp增加')
def stack_exp(stack):
    content2 = read(f_rule)
    stack = int(stack)
    if(stack > 8):
        return float(content2[len(content2)-1].split('\t')[0])
    else:
        for i in content2:
            x = i.split('\t')
            if(x[2] == str(stack)):
                return float(x[0])
def stack_clear(status_L):
    content = read(f_info)
    content2 = read(f_offcount)
    for i in range(len(status_L)):
        text = content[i]
        x = text.split('\t') #該行的List形式
        stack = x[3]
        flag = False
        if(status_L[i] == 'off' and stack != '0'): #符合離線&&stack有值
            for j in content2:
                if(x[0] in j): #檢查這個人有沒有已經在offcount.txt資料內
                    text = j
                    a = text.split('\t')
                    flag = True
                    break
            if(flag):
                times = int(a[1]) + 1
                only_change(f_offcount, text, 1, str(times))
            else:
                text = x[0] + '\t' + '1' + '\t' + '\n'
                with open(f_offcount, 'a') as f:
                    f.seek(0,2)
                    f.writelines(text)
        if(status_L[i] == 'on'):
            for j in content2:
                if(x[0] in j):
                    text = j
                    a = text.split('\t')
                    if(a[1] != '0'):
                        only_change(f_offcount, text, 1, '0')
    content2 = read(f_offcount)
    for i in content2:
        text = i
        x = text.split('\t')
        if(int(x[1]) > 3):
            only_change(f_offcount, text, 1, '0')
            user = bot.get_user(int(x[0]))
            print(user.name, 'stack被清除')
            for j in content:
                if(x[0] in j):
                    text = j
                    only_change(f_info, text, 3, '0')   
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
def lv_up():
    content = read(f_info)
    for i in content:
        text = i
        x = text.split('\t')
        LEVEL = int(x[4])
        exp = float(x[2])
        run = True
        levelup_ed = False
        while(run):
            C = next_lv_exp(LEVEL)
            if(exp >= C):
                levelup_ed = True
                exp = exp - C
                LEVEL = LEVEL + 1
            else:
                run = False
        if(levelup_ed):
            user = bot.get_user(int(x[0]))
            print(user.display_name, '升等 ->',LEVEL)
            text_new = only_change(f_info, text, 2, str(round(exp, 1))) #把經驗值 -> 經驗值扣升等所需經驗
            only_change(f_info, text_new, 4, str(LEVEL))
def next_lv_exp(LEVEL):
    A = Lv_need[0]
    B = Lv_need[1]
    #3等的時候迴圈要跑1圈 得C值
    for j in range(LEVEL-2):
        C = A + B
        A = B
        B = C
    if(LEVEL == 1):
        C = A
    if(LEVEL == 2):
        C = B
    return C

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

def gettime(user):
    flag = False
    local_dt = 'not_found'
    content = read(f_info)
    for i in content:
        if(str(user.id) in i):
            x = i.split('\t')
            Utc = x[1]
            Dst = x[6]
            flag = True
    if(flag):
        dt = datetime.utcnow()
        dt = dt.replace(tzinfo=timezone.utc)
        DELTA = timezone(timedelta(hours=int(Utc)+int(Dst)))
        local_dt = dt.astimezone(DELTA)
    return local_dt
def sec_to_start():
    UTC_time = [time.gmtime().tm_hour, time.gmtime().tm_min, time.gmtime().tm_sec]
    sec = Time_to_start - UTC_time[1]*60 - UTC_time[2]
    if(sec < 0):
        sec = 3600 - UTC_time[1]*60 - UTC_time[2]
    return sec
def update_high():
    content = read(f_info)
    for i in content:
        text = i
        x = text.split('\t')
        if(int(x[3]) > int(x[7])):
            only_change(f_info, text, 7, x[3])
def update_rank():
    level_L = []
    content = read(f_info)
    for i in content:
        text = i
        x = text.split('\t')
        level_L.append([text, int(x[4]), float(x[2])])
    L = sorted(level_L, key = itemgetter(1, 2), reverse = True)
    for i in content:
        for j in L:
            if(j[0] in i):
                text = i
                x = text.split('\t')
                only_change(f_info, text, 5, str(L.index(j)+1))
@bot.event
async def on_ready():
    print(bot.user.name, 'has connected to Discord!')
    sec = sec_to_start()
    if(TEST):
        sec = 1
    t = Timer(sec, check_cd)
    t.start()
@bot.command(name='timezone')
async def tz(ctx):
    user = ctx.author
    await user.create_dm()
    await user.dm_channel.send(
        f'哈囉 {user.name}, 不睡覺才會變強！加入變強的行列請設定你的時區！\n'
        f'設定你的時區, 輸入：UTC(+or-)數字; e.g. **UTC+8**\n'
        f'看看你在哪裡 https://upload.wikimedia.org/wikipedia/commons/8/88/World_Time_Zones_Map.png'
    )
    def check(m):
        if(m.channel == user.dm_channel):
            if(m.content[0:3].upper() == 'UTC'):
                response = m.content[0:3]
                return True
            elif(m.content.upper() == 'Y' or m.content.upper() == 'N'):
                return True
        return False
    msg = await bot.wait_for('message', check=check)
    set_UTC(user, msg)
    await user.dm_channel.send(f'你輸入了UTC{msg.content[3:len(msg.content)]}，你已經加入變強的行列\n')
    run = True
    while(run):
        await user.dm_channel.send(f'開啟日光節約時間? (**y**/**n**)')
        msg = await bot.wait_for('message', check=check)
        run = set_DST(user, msg.content)
    await user.dm_channel.send(f'你已設定日光節約時間 :)')
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
            msg = '你輸入了錯誤的格式, usage: **ns info** 使用者群暱稱(不輸入則查詢自己)'
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
輸入 **ns timezone** 設定你的時區 不睡覺才會變強'
                else:
                    sec = sec_to_start()
                    if(L[6]=='1'):
                        Dst = 'Yes'
                    else:
                        Dst = 'No'
                    msg = f'{user.mention}的資訊：\n\
```ini\n\
[UTC]: {L[1]} (日光節約時間: {Dst})\n\
[LV]: {L[4]} ({L[2]} / {next_lv_exp(int(L[4]))})\n\
[疊加狀態]: {L[3]} (+EXP: {stack_exp(L[3])})\n\
[距離下次刷新時間]: {sec//60}分{sec%60}秒\n\
```'
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
            msg = '你輸入了錯誤的格式, usage: **ns history** 使用者群暱稱(不輸入則查詢自己)'
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
輸入 **ns timezone** 設定你的時區 不睡覺才會變強'
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

@bot.command()
async def now(ctx, *args):
    try:
        Users = ctx.message.guild.members
    except:
        await ctx.send('這個指令只能在頻道中使用')
    else:
        #error
        if(len(args)>1):
            msg = '你輸入了錯誤的格式, usage: **ns now** 使用者群暱稱(不輸入則查詢自己)'
        #ns now user.displayname
        else:
            user = 0
            #ns now
            if(len(args)==0):
                user = ctx.author
            else:
                for i in Users:
                    if(args[0] == i.display_name):
                        user = i
                        break
            if(user != 0):
                L = gettime(user)
                L_str = L.strftime("%Y年%m月%d日 %H:%M:%S")
                if(L == 'not_found'):
                    msg = f'{user.mention}還沒有成為變強的一員\n\
輸入 **ns timezone** 設定你的時區 不睡覺才會變強'
                else:
                    msg = f'{user.mention}的在地時間：{L_str}'
                    for i in range(24):
                        if(L.hour == i):
                            await ctx.channel.send(image[i])
            else:
                msg = '找不到該位使用者'
        await ctx.channel.send(msg)
@bot.command()
async def rule(ctx):
    user = ctx.author
    await user.create_dm()
    await user.dm_channel.send(
        f'```ini\n'
        f'這是一個讓你熬夜時會升等的BOT，只要在[晚上12點~早上7點]之間在線上就會加經驗值\n'
        f'如果你[整夜都沒睡覺]，即使超過早上7點還是會繼續加經驗值！\n'
        f'除此之外每個人都會有一個[疊加狀態]，疊加狀態越高加的經驗就越多\n'
        f'但中間只要[連續離線2小時]，疊加狀態就會被清除哦！\n'
        f'輸入[ns help]可以看有哪些可以用的指令\n'
        f'```'
    )
bot.run(TOKEN)