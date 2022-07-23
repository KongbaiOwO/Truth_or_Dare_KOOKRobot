from khl import Bot, Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element, Types

import logging
logging.basicConfig(level='INFO')

def loaddata(gid):
    from os.path import exists
    if not exists(f'./data/{gid}.json'):
        reset(gid)
    del exists
    from json import loads
    with open(f'./data/{gid}.json', 'r') as f:
        global data
        data = loads(f.read())
        del loads

def writedata(gid):
    from json import dump
    with open(f'./data/{gid}.json', 'w') as f:
        dump(data,f,sort_keys=True, indent=2)
        del dump
    loaddata(gid)

def reset(gid):
    from json import dump
    from os import mkdir
    with open(f'./data/{gid}.json', 'w+') as f:
        global data
        data = {"是否开始": False,
                "玩家": {},
                "是否拼点": False,
                "惩罚玩家": -1,
                "选择的惩罚": "",
                "惩罚完成": False,
                "判断真的": [],
                "判断假的": [],
                "结束游戏": []
                }
        dump(data, f, sort_keys=True, indent=2)
        del dump
    del mkdir


bot = Bot(token='在这里填写你机器人的秘钥')

@bot.command(name = '重置真心话大冒险' )
async def restcommand(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('./管理员.txt' , 'r' , encoding='utf-8') as f:
        admin=f.read().split('+')
    if msg.author_id not in admin:
        await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 你没有权限使用此命令''', temp_target_id=msg.author_id)
    else:
        reset(msg.extra['guild_id'])
        await msg.ctx.channel.send("重置成功")
        c = Card(Module.Header('真心话大冒险'),
                 Module.Context('加入或退出真心话大冒险'),
                 Module.ActionGroup(
                     Element.Button('加入', '加入真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.INFO),
                     Element.Button('退出', '退出真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.DANGER),
                     Element.Button('开始真心话大冒险', '开始真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.PRIMARY))
                 )
        cm = CardMessage(c)
        await msg.ctx.channel.send(cm)

@bot.command(name = '真心话大冒险' )
async def menucommand(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    from os.path import exists
    if not exists(f'./data/{msg.extra["guild_id"]}.json'):
        reset(msg.extra['guild_id'])
    del exists
    c = Card(Module.Header('真心话大冒险'),
                Module.Context('加入或退出真心话大冒险'),
                Module.ActionGroup(
                    Element.Button('加入' , '加入真心话大冒险' , Types.Click.RETURN_VAL , Types.Theme.INFO),
                    Element.Button('退出' , '退出真心话大冒险' , Types.Click.RETURN_VAL , Types.Theme.DANGER),
                    Element.Button('开始真心话大冒险' , '开始真心话大冒险' , Types.Click.RETURN_VAL , Types.Theme.PRIMARY))
             )
    cm = CardMessage(c)
    await msg.ctx.channel.send(cm)

@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def print_btn_value(b: Bot, e: Event):
    print(f'''{e.body['user_info']['nickname']} 按下了 \"{e.body['value']}\" 按钮''')
    loaddata(e.body['guild_id'])
    channel = await b.fetch_public_channel(e.body['target_id'])

    if e.body['value']=='加入真心话大冒险':
        if e.body['user_id'] in data['玩家']:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你已经加入了真心话大冒险''' , temp_target_id=e.body['user_id'])
        elif data["是否开始"]:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 真心话大冒险已开始，请结束后再加入''' , temp_target_id=e.body['user_id'])
        else:
            data['玩家'][e.body['user_id']] = -1
            await b.send(channel, f'''(met){e.body['user_id']}(met) 加入真心话大冒险成功（{len(data["玩家"])}）''')
            writedata(e.body['guild_id'])

    if e.body['value'] == '退出真心话大冒险':
        if e.body['user_id'] not in data['玩家']:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你尚未加入了真心话大冒险''', temp_target_id=e.body['user_id'])
        elif data["是否开始"]:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 真心话大冒险已开始，请结束后再退出''', temp_target_id=e.body['user_id'])
        else:
            del data['玩家'][e.body['user_id']]
            await b.send(channel, f'''(met){e.body['user_id']}(met) 退出真心话大冒险成功（{len(data["玩家"])}）''')
            writedata(e.body['guild_id'])

    if e.body['value'] == '开始真心话大冒险':
        if data["是否开始"]:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 真心话大冒险已开始''',temp_target_id=e.body['user_id'])
        elif len(data['玩家']) > 1:
            data["是否开始"] = True
            data["是否拼点"] = True
            c = Card(Module.Header('真心话大冒险开始'),
                     Module.Context('开始拼点'),
                     Module.ActionGroup(
                         Element.Button('拼点', '拼点', Types.Click.RETURN_VAL, Types.Theme.PRIMARY))
                     )
            cm = CardMessage(c)
            await b.send(channel, cm)
            writedata(e.body['guild_id'])
        else:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 加入人数不足，需要2人才可开始''', temp_target_id=e.body['user_id'])

    if e.body['value'] == '拼点':
        if not data["是否开始"]:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 真心话大冒险尚未开始''', temp_target_id=e.body['user_id'])
        elif e.body['user_id'] not in data['玩家']:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你尚未加入真心话大冒险''', temp_target_id=e.body['user_id'])
        elif data['玩家'][e.body['user_id']] != -1:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你已经拼过点了''', temp_target_id=e.body['user_id'])
        elif not data['是否拼点']:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 不在拼点状态''', temp_target_id=e.body['user_id'])
        else:
            from random import randint
            points = randint(0, 100)
            del randint
            data['玩家'][e.body['user_id']] = points
            writedata(e.body['guild_id'])
            await b.send(channel, f'''(met){e.body['user_id']}(met) 拼点成功，你的点数为{points}''')
            for i in data['玩家']:
                if data['玩家'][i] == -1:
                    return None
            data['是否拼点'] = False
            d_order = sorted(data['玩家'].items(), key=lambda x: x[1], reverse=False)
            data["惩罚玩家"] = int(d_order[0][0])
            writedata(e.body['guild_id'])
            await b.send(channel, f'''所有人拼点完成，(met){d_order[0][0]}(met) 拼的点数最小''')
            c = Card(Module.Header('选择惩罚'),
                     Module.ActionGroup(
                         Element.Button('选真心话', '选真心话', Types.Click.RETURN_VAL, Types.Theme.INFO),
                         Element.Button('选大冒险', '选大冒险', Types.Click.RETURN_VAL, Types.Theme.DANGER))
                     )
            cm = CardMessage(c)
            await b.send(channel, cm)

    if e.body['value'] == '选真心话':
        if data['选择的惩罚']!='' or int(e.body['user_id'])!=data['惩罚玩家']:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你现在无需选择''', temp_target_id=e.body['user_id'])
        else:
            with open('真心话词库.txt', 'r', encoding='utf-8') as f:
                zxh=f.read().split("+")
            from random import choice
            punish=choice(zxh)
            del choice
            data['选择的惩罚']=punish
            await b.send(channel, f'''(met){e.body['user_id']}(met)选择成功，下面请听题，完成请点击完成按钮''')
            c = Card(Module.Header(f'{punish}'),
                     Module.ActionGroup(
                         Element.Button('完成', '完成', Types.Click.RETURN_VAL, Types.Theme.PRIMARY))
                     )
            cm = CardMessage(c)
            await b.send(channel,cm)
            writedata(e.body['guild_id'])

    if e.body['value'] == '选大冒险':
        if data['选择的惩罚']!='' or int(e.body['user_id'])!=data['惩罚玩家']:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你现在无需选择''', temp_target_id=e.body['user_id'])
        else:
            with open('大冒险词库.txt', 'r' ,encoding='utf-8') as f:
                zxh=f.read().split("+")
            from random import choice
            punish=choice(zxh)
            del choice
            data['选择的惩罚']=punish
            await b.send(channel, f'''(met){e.body['user_id']}(met)选择成功，下面请听题，完成请点击完成按钮''')
            c = Card(Module.Header(f'{punish}'),
                     Module.ActionGroup(
                         Element.Button('完成', '完成', Types.Click.RETURN_VAL, Types.Theme.PRIMARY))
                     )
            cm = CardMessage(c)
            await b.send(channel,cm)
            writedata(e.body['guild_id'])

    if e.body['value'] == '完成':
        if data['选择的惩罚']=='' or int(e.body['user_id'])!=data['惩罚玩家']:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你现在无需惩罚''', temp_target_id=e.body['user_id'])
        else:
            data["惩罚完成"] = True
            c = Card(Module.Header('惩罚完成，请大家判断真假'),
                     Module.ActionGroup(
                         Element.Button('真的', '选真的', Types.Click.RETURN_VAL, Types.Theme.INFO),
                         Element.Button('假的', '选假的', Types.Click.RETURN_VAL, Types.Theme.DANGER))
                     )
            cm = CardMessage(c)
            await b.send(channel, cm)
            writedata(e.body['guild_id'])

    if e.body['value'] == '选真的':
        if not data["惩罚完成"] or e.body['user_id'] not in data["玩家"] or int(e.body['user_id']) == data['惩罚玩家'] or e.body['user_id'] in data["判断真的"]:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你现在无需判断''', temp_target_id=e.body['user_id'])
        elif e.body['user_id'] in data["判断假的"]:
            for i in range(len(data["判断假的"])):
                if i >= len(data["判断假的"]):
                    break
                if data["判断假的"][i]==e.body['user_id']:
                    del data["判断假的"][i]
                    data["判断真的"].append(e.body['user_id'])
                    writedata(e.body['guild_id'])
                    await b.send(channel, f'''(met){e.body['user_id']}(met) 修改成功，你选择了真的（真：假={len(data["判断真的"])}：{len(data["判断假的"])}）''')
        else:
            data["判断真的"].append(e.body['user_id'])
            writedata(e.body['guild_id'])
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你选择了真的（真：假={len(data["判断真的"])}：{len(data["判断假的"])}）''')
        if len(data["判断真的"]) + len(data["判断假的"]) == len(data["玩家"]) - 1:
            if len(data["判断真的"]) >=len(data["判断假的"]):
                await b.send(channel, f'''恭喜 (met){data["惩罚玩家"]}(met) 成功完成惩罚''')
            else:
                await b.send(channel, f'''(met){data["惩罚玩家"]}(met) 未能完成惩罚，你将遭到谴责''')
            temp = data['玩家']
            for i in temp:
                temp[i] = -1
            reset(e.body['guild_id'])
            data['玩家'] = temp
            writedata(e.body['guild_id'])
            await b.send(channel, "游戏结束")
            c = Card(Module.Header('真心话大冒险'),
                     Module.Context('加入或退出真心话大冒险'),
                     Module.ActionGroup(
                         Element.Button('加入', '加入真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.INFO),
                         Element.Button('退出', '退出真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.DANGER),
                         Element.Button('开始真心话大冒险', '开始真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.PRIMARY))
                     )
            cm = CardMessage(c)
            await b.send(channel, cm)

    if e.body['value'] == '选假的':
        if not data["惩罚完成"] or  e.body['user_id'] not in data["玩家"] or int(e.body['user_id']) == data['惩罚玩家'] or e.body['user_id'] in data["判断假的"]:
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你现在无需判断''', temp_target_id=e.body['user_id'])
        elif e.body['user_id'] in data["判断真的"]:
            for i in range(len(data["判断真的"])):
                if i >= len(data["判断真的"]):
                    break
                if data["判断真的"][i]==e.body['user_id']:
                    del data["判断真的"][i]
                    data["判断假的"].append(e.body['user_id'])
                    writedata(e.body['guild_id'])
                    await b.send(channel, f'''(met){e.body['user_id']}(met) 修改成功，你选择了假的（真：假={len(data["判断真的"])}：{len(data["判断假的"])}）''')
        else:
            data["判断假的"].append(e.body['user_id'])
            writedata(e.body['guild_id'])
            await b.send(channel, f'''(met){e.body['user_id']}(met) 你选择了假的（真：假={len(data["判断真的"])}：{len(data["判断假的"])}）''')
        if len(data["判断真的"]) + len(data["判断假的"]) == len(data["玩家"]) - 1:
            if len(data["判断真的"]) >=len(data["判断假的"]):
                await b.send(channel, f'''恭喜 (met){data["惩罚玩家"]}(met) 成功完成惩罚''')
            else:
                await b.send(channel, f'''(met){data["惩罚玩家"]}(met) 未能完成惩罚，你将遭到谴责''')
            temp=data['玩家']
            for i in temp:
                temp[i]=-1
            reset(e.body['guild_id'])
            data['玩家'] = temp
            writedata(e.body['guild_id'])
            await b.send(channel,"游戏结束")
            c = Card(Module.Header('真心话大冒险'),
                     Module.Context('加入或退出真心话大冒险'),
                     Module.ActionGroup(
                         Element.Button('加入', '加入真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.INFO),
                         Element.Button('退出', '退出真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.DANGER),
                         Element.Button('开始真心话大冒险', '开始真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.PRIMARY))
                     )
            cm = CardMessage(c)
            await b.send(channel,cm)

@bot.command(name = '谁没拼点' )
async def checkpoints(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    loaddata(msg.extra['guild_id'])
    if not data['是否开始'] :
        await msg.ctx.channel.send(f"(met){msg.author_id}(met) 游戏尚未开始")
    else:
        temp=[]
        for i in data['玩家']:
            if data['玩家'][i]==-1:
                temp.append(i)
        tempmsg = f'还有{len(temp)}没有拼点，请下列玩家尽快拼点'
        for i in temp:
            tempmsg+=f" (met){i}(met) "
        await msg.ctx.channel.send(tempmsg)
        c = Card(Module.Header('请尽快拼点'),
                 Module.Context('开始拼点'),
                 Module.ActionGroup(
                     Element.Button('拼点', '拼点', Types.Click.RETURN_VAL, Types.Theme.PRIMARY))
                 )
        cm = CardMessage(c)
        await msg.ctx.channel.send(cm)

@bot.command(name = '谁没投票' )
async def checkpoints(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    loaddata(msg.extra['guild_id'])
    if not data['惩罚完成'] :
        await msg.ctx.channel.send(f"(met){msg.author_id}(met) 惩罚尚未开始")
    else:
        temp=[]
        for i in data['玩家']:
            if i not in data['判断真的']+data['判断假的'] and int(i)!=data["惩罚玩家"]:
                temp.append(i)
        tempmsg = f'还有{len(temp)}没有判断，请下列玩家尽快判断'
        for i in temp:
            tempmsg+=f" (met){i}(met) "
        await msg.ctx.channel.send(tempmsg)
        c = Card(Module.Header('请尽快判断'),
                 Module.ActionGroup(
                     Element.Button('真的', '选真的', Types.Click.RETURN_VAL, Types.Theme.INFO),
                     Element.Button('假的', '选假的', Types.Click.RETURN_VAL, Types.Theme.DANGER))
                 )
        cm = CardMessage(c)
        await msg.ctx.channel.send(cm)

@bot.command(name = '结果拼点' )
async def stoppoints(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    loaddata(msg.extra['guild_id'])
    if not data['是否开始'] :
        await msg.ctx.channel.send(f"(met){msg.author_id}(met) 游戏尚未开始")
    else:
        no_pd_count = 0
        for i in data['玩家']:
            if data['玩家'][i] == -1:
                no_pd_count += 1
        if no_pd_count <= len(data["玩家"]) // 2:
            for i in data['玩家']:
                if data['玩家'][i] == -1:
                    data['玩家'][i] = 101
            data['是否拼点'] = False
            d_order = sorted(data['玩家'].items(), key=lambda x: x[1], reverse=False)
            data["惩罚玩家"] = int(d_order[0][0])
            writedata(msg.extra['guild_id'])
            await msg.ctx.channel.send(f'''所有人拼点完成，(met){d_order[0][0]}(met) 拼的点数最小''')
            c = Card(Module.Header('选择惩罚'),
                     Module.ActionGroup(
                         Element.Button('选真心话', '选真心话', Types.Click.RETURN_VAL, Types.Theme.INFO),
                         Element.Button('选大冒险', '选大冒险', Types.Click.RETURN_VAL, Types.Theme.DANGER))
                     )
            cm = CardMessage(c)
            await msg.ctx.channel.send(cm)
            writedata(msg.extra['guild_id'])
        else:
            await msg.ctx.channel.send(f"(met){msg.author_id}(met) 结果拼点失败")
            temp = []
            for i in data['玩家']:
                if data['玩家'][i] == -1:
                    temp.append(i)
            tempmsg = f'还有{len(temp)}没有拼点，请下列玩家尽快拼点'
            for i in temp:
                tempmsg += f" (met){i}(met) "
            await msg.ctx.channel.send(tempmsg)
            c = Card(Module.Header('请尽快拼点'),
                     Module.Context('开始拼点'),
                     Module.ActionGroup(
                         Element.Button('拼点', '拼点', Types.Click.RETURN_VAL, Types.Theme.PRIMARY))
                     )
            cm = CardMessage(c)
            await msg.ctx.channel.send(cm)


@bot.command(name = '结果投票' )
async def checkpoints(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    loaddata(msg.extra['guild_id'])
    if not data['惩罚完成'] :
        await msg.ctx.channel.send(f"(met){msg.author_id}(met) 惩罚尚未开始")
    else:
        no_pd_count = 0
        for i in data['玩家']:
            if i not in data['判断真的']+data['判断假的'] and int(i) != data["惩罚玩家"]:
                no_pd_count += 1
        if (no_pd_count) <= ((len(data["玩家"]) - 1 )// 2):
            if len(data["判断真的"]) >=len(data["判断假的"]):
                await msg.ctx.channel.send(f'''恭喜 (met){data["惩罚玩家"]}(met) 成功完成惩罚''')
            else:
                await msg.ctx.channel.send(f'''(met){data["惩罚玩家"]}(met) 未能完成惩罚，你将遭到谴责''')
            temp=data['玩家']
            writedata(msg.extra['guild_id'])
            for i in temp:
                temp[i]=-1
            reset(msg.extra['guild_id'])
            data['玩家'] = temp
            writedata(msg.extra['guild_id'])
            await msg.ctx.channel.send("戏结束")
            c = Card(Module.Header('真心话大冒险'),
                     Module.Context('加入或退出真心话大冒险'),
                     Module.ActionGroup(
                         Element.Button('加入', '加入真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.INFO),
                         Element.Button('退出', '退出真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.DANGER),
                         Element.Button('开始真心话大冒险', '开始真心话大冒险', Types.Click.RETURN_VAL, Types.Theme.PRIMARY))
                     )
            cm = CardMessage(c)
            await msg.ctx.channel.send(cm)
        else:
            await msg.ctx.channel.send(f"(met){msg.author_id}(met) 结果投票失败")
            temp=[]
            for i in data['玩家']:
                if i not in data['判断真的']+data['判断假的'] and int(i)!=data["惩罚玩家"]:
                    temp.append(i)
            tempmsg = f'还有{len(temp)}没有判断，请下列玩家尽快判断'
            for i in temp:
                tempmsg+=f" (met){i}(met) "
            await msg.ctx.channel.send(tempmsg)
            c = Card(Module.Header('请尽快判断'),
                     Module.ActionGroup(
                         Element.Button('真的', '选真的', Types.Click.RETURN_VAL, Types.Theme.INFO),
                         Element.Button('假的', '选假的', Types.Click.RETURN_VAL, Types.Theme.DANGER))
                     )
            cm = CardMessage(c)
            await msg.ctx.channel.send(cm)

@bot.command(name = '查真心话')
async def inquirezxh(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('真心话词库.txt', 'r', encoding='utf-8') as f:
        zxh=f.read().split('+')
    reply=''
    page=1
    for i in range(len(zxh)):
        reply+=f'{i+1}. {zxh[i]} \n'
        if (i+1)%20 == 0 or i+1==len(zxh):
            c = Card(Module.Header(f'共有{len(zxh)}个真心话（第{page}/{(len(zxh)+19)//20}页）：'),
                     Module.Context(reply))
            cm=CardMessage(c)
            reply=''
            page+=1
            await msg.ctx.channel.send(cm)

@bot.command(name = '查大冒险')
async def inquiredmx(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('大冒险词库.txt', 'r', encoding='utf-8') as f:
        dmx=f.read().split('+')
    reply=''
    page=1
    for i in range(len(dmx)):
        reply+=f'{i+1}. {dmx[i]} \n'
        if (i+1)%20 == 0 or i+1==len(dmx):
            c = Card(Module.Header(f'共有{len(dmx)}个大冒险（第{page}/{(len(dmx)+19)//20}页）：'),
                     Module.Context(reply))
            cm=CardMessage(c)
            reply=''
            page+=1
            await msg.ctx.channel.send(cm)

@bot.command(name = '删真心话')
async def delzxh(msg: Message , number:int):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('./管理员.txt', 'r', encoding='utf-8') as f:
        admin = f.read().split('+')
    if msg.author_id not in admin:
        await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 你没有权限使用此命令''', temp_target_id=msg.author_id)
    else:
        with open('真心话词库.txt', 'r', encoding='utf-8') as f:
            zxh=f.read().split('+')
        if number > len(zxh):
            await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 无此真心话，共{len(zxh)}个真心话''')
        else:
            reply=zxh[number-1]
            del zxh[number-1]
            writezxh='+'.join(zxh)
            with open('真心话词库.txt', 'w', encoding='utf-8') as f:
                f.write(writezxh)
            await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 删除真心话\"{reply}\"成功，现在共{len(zxh)}个真心话''')

@bot.command(name = '删大冒险')
async def deldmx(msg: Message , number:int):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('./管理员.txt', 'r', encoding='utf-8') as f:
        admin = f.read().split('+')
    if msg.author_id not in admin:
        await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 你没有权限使用此命令''', temp_target_id=msg.author_id)
    else:
        with open('大冒险词库.txt', 'r', encoding='utf-8') as f:
            dmx=f.read().split('+')
        if number>len(dmx):
            await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 无此大冒险，共{len(dmx)}个大冒险''')
        else:
            reply=dmx[number-1]
            del dmx[number-1]
            writedmx='+'.join(dmx)
            with open('大冒险词库.txt', 'w', encoding='utf-8') as f:
                f.write(writedmx)
            await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 删除大冒险\"{reply}\"成功，现在共{len(dmx)}个大冒险''')

@bot.command(name = '加真心话')
async def addzxh(msg: Message , add:str):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('./管理员.txt', 'r', encoding='utf-8') as f:
        admin = f.read().split('+')
    if msg.author_id not in admin:
        await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 你没有权限使用此命令''', temp_target_id=msg.author_id)
    else:
        with open('真心话词库.txt', 'r', encoding='utf-8') as f:
            zxh=f.read().split('+')
        zxh.append(add)
        writezxh='+'.join(zxh)
        with open('真心话词库.txt', 'w', encoding='utf-8') as f:
            f.write(writezxh)
        await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 添加真心话\"{add}\"成功，现在共{len(zxh)}个真心话''')

@bot.command(name = '加大冒险')
async def adddmx(msg: Message , add:str):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('./管理员.txt', 'r', encoding='utf-8') as f:
        admin = f.read().split('+')
    if msg.author_id not in admin:
        await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 你没有权限使用此命令''', temp_target_id=msg.author_id)
    else:
        with open('大冒险词库.txt', 'r', encoding='utf-8') as f:
            dmx=f.read().split('+')
        dmx.append(add)
        writedmx='+'.join(dmx)
        with open('大冒险词库.txt', 'w', encoding='utf-8') as f:
            f.write(writedmx)
        await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 添加大冒险\"{add}\"成功，现在共{len(dmx)}个大冒险''')

@bot.command(name = '呼叫管理员')
async def calladmin(msg: Message):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('./管理员.txt', 'r', encoding='utf-8') as f:
        admin = f.read().split('+')
    reply=''
    for i in admin:
        reply+=f'(met){i}(met) '
    await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 正在呼叫管理员，请管理员尽快到达战场： \n{reply}''')

@bot.command(name = '加管理员')
async def addadmin(msg: Message , add:str):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('./管理员.txt', 'r', encoding='utf-8') as f:
        admin = f.read().split('+')
    if msg.author_id not in admin:
        await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 你没有权限使用此命令''', temp_target_id=msg.author_id)
    else:
        add=add.replace('(met)','')
        if add in admin:
            await msg.ctx.channel.send(f'''(met){add}(met) 已为管理员''')
        else:
            admin.append(add)
            writeadmin='+'.join(admin)
            with open('./管理员.txt', 'w', encoding='utf-8') as f:
                f.write(writeadmin)
            await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 已添加 (met){add}(met) 为管理员''')

@bot.command(name = '删管理员')
async def deladmin(msg: Message , number:str):
    print(f'''{msg.author.nickname} 触发了命令 \"{msg.extra["kmarkdown"]["raw_content"]}\"''')
    with open('./管理员.txt', 'r', encoding='utf-8') as f:
        admin = f.read().split('+')
    if msg.author_id not in admin:
        await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 你没有权限使用此命令''', temp_target_id=msg.author_id)
    else:
        number=number.replace('(met)','')
        if number not in admin:
            await msg.ctx.channel.send(f'''(met){number}(met) 不是管理员''')
        else:
            for i in range(len(admin)):
                if admin[i]==number:
                    del admin[i]
                    break
            writeadmin='+'.join(admin)
            with open('./管理员.txt', 'w', encoding='utf-8') as f:
                f.write(writeadmin)
            await msg.ctx.channel.send(f'''(met){msg.author_id}(met) 已删除 (met){number}(met) 为管理员''')


if __name__=="__main__":
    bot.run()
