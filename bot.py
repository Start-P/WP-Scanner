from WPScanner import WPScanner, WPDoesntUse

import disnake
from disnake.ext import commands
import datetime
from requests import HTTPError
import urllib3

bot = commands.InteractionBot()
TOKEN = "Input your discord bot token here."


@bot.slash_command(
    name="wordpress_scanner",
    description="View WordPress site infomation",
    options=[
        disnake.Option(
            name="url",
            description="Enter URL",
            type=disnake.OptionType.string,
            required=True,
        )
    ]
)
async def wp_scan(inter, url: str):
    await inter.response.defer(ephemeral=True)
    try:
        wp = WPScanner(url)
    except WPDoesntUse:
        await inter.send("We can't find WordPress in this page.\n Try again with another page or another site.", ephemeral=True)
        return
    except:
        await inter.send("We can't access this site.", ephemeral=True)
        return

    try:
        version = wp.get_wordpress_version()
        all_user = "\n".join(wp.get_all_users())
        all_plugin = "\n".join([f"{plugin['name']} Version: {plugin['version']}" for plugin in wp.get_all_plugins()])
        all_theme = "\n".join([f"{theme['name']} Version: {theme['version']}" for theme in wp.get_all_themes()])
        vulneravility_pages = "\n".join(wp.get_vulnerability_page())
    except Exception as e:
        await inter.send("We can't access this site.", ephemeral=True)
        return

    embed = disnake.Embed(
        title="WordPress Infomation",
        description="This bot can check wordpress site infomation.",
        color=disnake.Colour.red(),
        timestamp=datetime.datetime.utcnow()
    )

    embed.set_author(
        name=inter.user.name,
        icon_url=inter.user.avatar.url
    )

    embed.set_footer(
        text="This bot is OpenSource on Github.",
    )

    embed.add_field(name="Version", value=version, inline=False)
    embed.add_field(name="Users", value=f"```\n{all_user}\n```", inline=False)
    embed.add_field(name="Themes", value=f"```\n{all_theme}\n```", inline=False)
    embed.add_field(name="Plugins", value=f"```\n{all_plugin if all_plugin else None}\n```", inline=False)
    embed.add_field(name="Vulneravility Pages", value=f"```\n{vulneravility_pages if vulneravility_pages else None}\n```", inline=False)

    await inter.edit_original_response("Done.")
    await inter.send(embed=embed)

bot.run(TOKEN)
