import disnake
from disnake.ext import tasks, commands
import json
intents = disnake.Intents.default()
intents.message_content = True

global slash_inter, button_inter

slash_inter: disnake.AppCmdInter
button_inter = disnake.MessageInteraction

activity = disnake.Activity(
    name="Made by dixxe",
    type=disnake.ActivityType.listening)

bot = commands.Bot(command_prefix='>', intents=intents, help_command=None, activity=activity)

global roles, service, channels
roles = {} # {user.name : role.id }
service = [True, 1, 20, '🍪'] # [0] - True/False role buying, [1] - how much credits for one reaction(emoji), [2] role cost, [3] - emoji
channels = {} # {channel.id : 0} for me its just simple to use channel id to get it
users = {} # {user.name : amount_of_credits}


##--сохранение--##
def exportData(users, service, roles, channels):
    data = {'users': users,
            'service'    : service    }
    with open('value.json', 'w') as save:
        json.dump(data, save)
##--сохранение--##

##--загрузка--##
def importData():
    with open('value.json', 'r') as save:
        data = json.load(save)
        users = data['users']
        service = data['service']
    return users, service
##--загрузка--##

##--очистка--##
def flushs():
    data = {'users': {},
            'service': [True, 1, 20, '🍪']}
    with open('value.json', 'w') as save:
        json.dump(data, save)

##############################
@bot.event
async def on_ready():
    print(f"We have logged in {bot.user}")
    parse_channels.start()

@bot.slash_command(description='Описание функций бота')
async def help(slash_inter):
    await slash_inter.response.defer()
    emb = disnake.Embed(title='Все команды бота:', color=16752640)
    emb.add_field(name='/set [канал]', value='Привязать канал где будут считаться кредиты.')
    emb.add_field(name='/emoji', value='Привязать эмодзи за который будут выдаваться кредиты.')
    emb.add_field(name='/unset [канал]', value='Отвязать канал где будут считаться кредиты.')
    emb.add_field(name='/role [название] [цвет в формате HEX]', value='Купить роль за ваши кредиты.')
    emb.add_field(name='/manage [пользователь] [количество]', value='Изменить количество кредитов у пользователя.')
    emb.add_field(name='/delete_role [роль]', value='Удалить покупную роль. Кредиты не возмещаются.')
    emb.add_field(name='/variables', value='Поменять параметры под ваш сервер.')
    emb.set_author(name='Бусти создателя', url='https://boosty.to/dixxe')
    await slash_inter.edit_original_response(embed=emb)

@bot.slash_command(description='Привязать канал где будут считаться кредиты.')
async def set(slash_inter, channel : disnake.abc.GuildChannel):
    await slash_inter.response.defer(ephemeral=True)
    if channel.id in channels.keys():
        await slash_inter.edit_original_response('Этот канал уже привязан')
    else:
        channels[channel.id] = 0
        await slash_inter.edit_original_response('Канал привязан')

@bot.slash_command(description='Привязать эмодзи за который будут выдаваться кредиты.')
async def emoji(slash_inter, emoji):
    await slash_inter.response.defer()
    try:
        print(emoji)
        try: service[3] = emoji.id
        except Exception: pass
        service[3] = emoji
        await slash_inter.edit_original_response(f'Эмодзи {emoji} привязан.')
    except Exception as e: await slash_inter.edit_original_response(f"Что-то пошло не так, отправьте этот код ошибки мне в телеграм:\n```{e}```")

@bot.slash_command(description='Отвязать канал где будут считаться кредиты.')
async def unset(slash_inter, channel : disnake.TextChannel or disnake.ForumChannel):
    await slash_inter.response.defer(ephemeral=True)
    if channel.id in channels.keys():
        channels.pop(channel.id)
        await slash_inter.edit_original_response('Канал отвязан.')
    else:
         await slash_inter.edit_original_response('Канал не был привязан.')

@bot.slash_command(description='Купить роль за ваши кредиты.')
async def role(slash_inter, name : str or int, color : str):
    if(service[0]):
        await slash_inter.response.defer()
        guild = slash_inter.author.guild
        int_color = int(color, 16)
        if ((slash_inter.author.name in users.keys()) and ( slash_inter.author.name not in roles.keys())):
            credits = int(users[slash_inter.author.name])
            if (credits >= service[2]):
                users[slash_inter.author.name] -= service[2]
                role = await guild.create_role(name=name, color=int_color, reason=f'Покупная роль {slash_inter.author.name}')
                roles[slash_inter.author.name] = role.id
                await slash_inter.author.add_roles(disnake.abc.Object(role.id))
                print(roles)
                print(users)
                await slash_inter.edit_original_response('Поздравляю с покупкой вашей новой роли!')
        else:
            await slash_inter.edit_original_response(f'Вам не хватает денег или у вас уже есть роль. Роль стоит - {service[2]}')
    else:
        await slash_inter.response.defer(ephemeral=True)
        await slash_inter.edit_original_response(f'Покупка ролей на сервере отключена :(')

@bot.slash_command(description='Изменить количество кредитов у пользователя.')
async def manage(slash_inter, user : disnake.Member, amount : int):
    await slash_inter.response.defer()
    if user.name not in users.keys():
        users[user.name] = amount
    else:
        users[user.name] += amount
    await slash_inter.edit_original_response(f'Вы изменили коичетсво кредитов пользователя. Теперь у него {users[user.name]} кредитов')

@bot.slash_command(description='Удалить покупную роль. Кредиты не возмещаются.')
async def delete_role(slash_inter, role : disnake.Role):
    await slash_inter.response.defer()
    if (role.id not in roles.values()):
        await slash_inter.edit_original_response('Данная роль не покупная.')
    else:
        holder_name = list(roles.keys())[list(roles.values()).index(role.id)]
        await role.delete(reason='Покупная роль удалена администрацией')
        roles.pop(holder_name)
        await slash_inter.edit_original_response(f'Роль удалена, {holder_name} скорее всего расстроится.')

@bot.slash_command(description='Поменять параметры под ваш сервер.')
async def variables(slash_inter, role_buying : bool, credit_course : int, role_cost : int):
    await slash_inter.response.defer(ephemeral=True)
    service[0] = role_buying
    service[1] = credit_course
    service[2] = role_cost
    await slash_inter.edit_original_response(f'Переменные настроены. Покупка роли: {service[0]}, Курс: {service[1]} кредитов за реакцию, цена роли: {service[2]} кредитов')

########################################################################3
@tasks.loop(seconds=5)
async def parse_channels():
    for channel_id in channels:
        channel = bot.get_channel(channel_id)
        async for msg in channel.history(limit=200):
            for reaction in range(len(msg.reactions)):
                if(str(msg.reactions[reaction]) == str(service[3])):
                    users[msg.author.name] = (msg.reactions[reaction].count + service[1])


with open('token.txt', 'r') as file:
    token = file.read() 
bot.run(token)