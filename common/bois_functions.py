import csv
import datetime
from csv import writer
import os
from pathlib import Path

import discord
from common.bot_logger import get_logger

logger = get_logger(__name__)


async def reply_and_delete(ctx, reply: str):
    # noinspection PyBroadException
    try:
        await ctx.author.send(reply)
        await ctx.message.delete()
    except Exception:
        if ctx.guild:
            logger.warning(
                "Could not remove old message: 'ctx.message.content=%s' by user: 'ctx.author=%s'",
                ctx.message.content,
                ctx.author,
            )


# region date helper functions


def get_now():
    return datetime.datetime.now()


def get_date_string_from_user(date: str = None):
    if not date:
        now = get_now()
        date = f"{now.day}-{now.month}-{now.year}"
    else:
        try:
            _date = datetime.datetime.strptime(date, "%d-%m-%Y")
            date = f"{_date.day}-{_date.month}-{_date.year}"
        except ValueError:
            return False
    return date


def get_date_from_string(date: str):
    # noinspection PyBroadException
    try:
        if not date:
            return get_now()
        return datetime.datetime.strptime(date, "%d-%m-%Y")
    except Exception:
        print("Error in get_date_from_string")
        return None


# endregion

# region handling and updating barf stats/leaderboards


def get_boi_file_path(user_id: int, year: int):
    # Make sure the /bois dir exists.
    if not os.path.exists("./bois"):
        os.mkdir("./bois")

    # Make sure the /bois/'year' folder exists.
    if not os.path.exists(f"./bois/{str(year)}"):
        os.mkdir(f"./bois/{str(year)}")

    # Make sure the /bois/'year'/'user_id'.csv exists
    if not os.path.exists(f"./bois/{str(year)}/{str(user_id)}.csv"):
        Path(f"./bois/{str(year)}/{str(user_id)}.csv").touch()

    return f"./bois/{str(year)}/{str(user_id)}.csv"


def write_barfs(lines, member_id: int, date: str):
    lines = sorted(
        lines, key=lambda x: (x[0].split(sep="-")[1], x[0].split(sep="-")[0])
    )

    with open(
        get_boi_file_path(member_id, get_date_from_string(date).year),
        "w",
        newline="\n",
    ) as file:
        writer(file).writerows(lines)


def add_barf(member: discord.Member, reason: str, date: str = None):
    date_string = get_date_string_from_user(date)
    if not date_string:
        return -1

    lines = list()
    with open(
        get_boi_file_path(member.id, get_date_from_string(date_string).year),
        "r",
        newline="\n",
    ) as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == date_string:
                return -2
            lines.append(row)

    lines.append([date_string, reason])
    write_barfs(lines, member.id, date_string)

    return len(lines)


def rem_barf(member: discord.Member, date: str = None):
    date_string = get_date_string_from_user(date)

    lines = list()
    removed = None
    with open(
        get_boi_file_path(member.id, get_date_from_string(date_string).year),
        "r",
        newline="\n",
    ) as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if not row[0] == date_string:
                lines.append(row)
            else:
                removed = row
    print(row[0].split(sep="-")[:2])

    write_barfs(lines, member.id, date_string)

    if removed:
        return f'Removed barf "{removed[1]}" with date {removed[0]} from {member.display_name}'
    return "Nothing to be removed"


def get_leaderboard_embeds():
    years = [
        name
        for name in os.listdir("./bois")
        if os.path.isdir("./bois/" + name) and name.isdigit()
    ]
    embeds = list()
    with open("leaderboards.csv", "r", newline="\n") as file:
        csv_reader = csv.reader(file)
        for message_id, year in csv_reader:
            if year in years:
                years.remove(year)
                embeds.append((int(year), int(message_id)))
    if years:
        for year in years:
            embeds.append((int(year), 0))
    embeds.sort()
    return embeds


def add_leaderboard(year: int, message_id: int):
    with open("leaderboards.csv", "r", newline="\n") as file:
        csv_reader = csv.reader(file)
        if str(year) in [row[1] for row in csv_reader]:
            logger.warning(f"Year {year} already in leaderboards, updating id")
            remove_leaderboard(year)

    with open("leaderboards.csv", "a", newline="\n") as file:
        file.write(f"{message_id},{year}\n")


def remove_leaderboard(year: int):
    with open("leaderboards.csv", "r", newline="\n") as file:
        boards = [
            (msg_id, year) for msg_id, year in csv.reader(file) if year != str(year)
        ]

    with open("leaderboards.csv", "w", newline="\n") as file:
        for message_id, year in boards:
            file.write(f"{message_id},{year}\n")


def get_boi_member_by_name(guild: discord.Guild, name: str):
    with open("./bois/bois.csv", "r", newline="\n") as file:
        csv_reader = csv.reader(file)
        for _name, _id in csv_reader:
            if str(_name) == name:
                return guild.get_member(int(_id))
        return None


def get_boi_name(member_id: int):
    with open("./bois/bois.csv", "r", newline="\n") as file:
        csv_reader = csv.reader(file)
        for name, _id in csv_reader:
            if _id == str(member_id):
                return name
    return False


def get_bois_names():
    with open("./bois/bois.csv", "r", newline="\n") as file:
        csv_reader = csv.reader(file)
        return [(row[0], row[1]) for row in csv_reader]


def get_stats(year: int):
    stats = list()
    for name, user_id in get_bois_names():
        length = 0
        last_date = "n.v.t."
        if os.path.exists(f"./bois/{str(year)}/{user_id}.csv"):
            with open(f"./bois/{str(year)}/{user_id}.csv", "r", newline="\n") as file:
                csv_reader = csv.reader(file)
                barfjes = [(r[0], r[1]) for r in csv_reader]
                length = len(barfjes)
                barfjes.sort(key=lambda x: get_date_from_string(x[0]))
                try:
                    last_date = get_date_from_string(barfjes[-1][0])
                except IndexError:
                    last_date = "n.v.t."
                    logger.warning(
                        f"Boi {name} shouldn't have a file for {year}, but has one."
                    )
        stats.append((name, length, last_date))
    return sorted(stats, key=lambda x: (x[1], x[2]), reverse=True)


async def update_roles(ctx, year):
    roles = [
        ctx.guild.get_role(722111112090484847),
        ctx.guild.get_role(722111166750523454),
        ctx.guild.get_role(722111370321068082),
        ctx.guild.get_role(722112336080666785),
    ]
    bois_as_members = list(
        filter(
            None,
            map(
                lambda l: get_boi_member_by_name(ctx.guild, l[0]),
                get_stats(year),
            ),
        )
    )
    leader_members = list(
        map(
            lambda l: get_boi_member_by_name(ctx.guild, l[0]),
            filter(lambda stat: stat[1] > 0, get_stats(year)[:3]),
        )
    )
    for boi in bois_as_members:
        await boi.remove_roles(*roles)

    for i in range(len(leader_members)):
        bois_as_members.remove(leader_members[i])
        await leader_members[i].add_roles(roles[i])

    for boi in bois_as_members:
        await boi.add_roles(roles[-1])


async def update_barfjes(ctx, channel: discord.TextChannel, current_year_only=False):
    leaderboards = get_leaderboard_embeds()  # [(year: int, message_id: int)]
    leaderboards.sort()  # year descending
    if current_year_only:
        leaderboards = [leaderboards[-1]]

    for year, message_id in leaderboards:
        # create embed
        embed = discord.Embed(title=f"Barfjes {year}", color=0x4E06D2)
        for name, barfjes, date in get_stats(year):
            embed.add_field(name=str(name), value=str(barfjes), inline=True)
            if not date == "n.v.t.":
                date = str(date.strftime("%d-%m-%Y"))
            embed.add_field(name="Laatste barf", value=date, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.remove_field(-1)

        # update/create message
        if message_id == 0:
            msg = await channel.send(embed=embed)
            add_leaderboard(year, int(msg.id))
        else:
            try:
                msg = await channel.fetch_message(message_id)
                await msg.edit(embed=embed)
            except discord.NotFound:
                remove_leaderboard(year)
                msg = await channel.send(embed=embed)
                add_leaderboard(year, int(msg.id))

    # update roles
    await update_roles(ctx, leaderboards[-1][0])


async def get_boi_barf_info(ctx, member: discord.Member, year: int):
    name = get_boi_name(member.id)
    if not name:
        await reply_and_delete(ctx, "Could not find this boi")
        return

    embed = discord.Embed(title=f"{name}'s barfjes {year}", color=0x4E06D2)
    if os.path.exists(f"./bois/{str(year)}/{member.id}.csv"):
        with open(f"./bois/{str(year)}/{member.id}.csv", "r", newline="\n") as file:
            csv_reader = csv.reader(file)
            barfjes = [(r[0], r[1]) for r in csv_reader]
            for date, reason in barfjes:
                embed.add_field(name=date, value=reason, inline=False)
            print(barfjes)
            if not barfjes:
                embed.add_field(
                    name="\u200b", value=f"This noob did not barf in {year}"
                )
    else:
        embed.add_field(name="\u200b", value=f"This noob did not barf in {year}")

    # noinspection PyBroadException
    try:
        await ctx.channel.send(embed=embed)
        await ctx.message.delete()
    except Exception:
        if ctx.guild:
            logger.warning(
                "Could not remove old message: 'ctx.message.content=%s' by user: 'ctx.author=%s'",
                ctx.message.content,
                ctx.author,
            )


# endregion
