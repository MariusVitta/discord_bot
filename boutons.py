import re
import typing
from discord import Interaction
from affichage import *


class TopButton(discord.ui.Button):
    def __init__(self, cid, emote, estCoin, estAffichageMobile):
        self.cid = cid
        self.emote = emote
        self.estCoin = estCoin
        self.estAffichageMobile = estAffichageMobile

        super().__init__(style=discord.ButtonStyle.secondary, custom_id=self.cid, emoji=self.emote, row=0)

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view: ViewTop = self.view

        currentPage = int(re.search(r"Page (\d)\/\d", interaction.message.embeds[0].footer.text).group(1))
        pages = int(re.search(r"Page \d\/(\d)", interaction.message.embeds[0].footer.text).group(1))
        newPage = 0
        if self.cid == "cst_next_btn":
            if currentPage + 1 == pages + 1:
                newPage = 1
            else:
                newPage = currentPage + 1
        if self.cid == "cst_prev_btn":
            if currentPage - 1 == 0:
                newPage = pages
            else:
                newPage = currentPage - 1
        if not self.estAffichageMobile:
            if self.estCoin:
                await interaction.message.edit(embed=afficher_top_coin(newPage, interaction.guild))
            else:
                await interaction.message.edit(embed=afficher_top(newPage, interaction.guild))
        else:
            if self.estCoin:
                await interaction.message.edit(embed=afficher_top_coin(newPage, interaction.guild, self.estAffichageMobile))
            else:
                await interaction.message.edit(embed=afficher_top(newPage, interaction.guild, self.estAffichageMobile))
        await interaction.response.defer()


class ViewTop(discord.ui.View):
    childen: typing.List[TopButton]

    def __init__(self, estCoin, affichageMobile: typing.Optional[bool] = False):
        super().__init__()

        tabTop = [
            ["cst_prev_btn", discord.PartialEmoji.from_str("<:reversefleche:936724361740693585>")],
            ["cst_next_btn", discord.PartialEmoji.from_str("<:fleche:925077237164806164>")]
        ]
        for i in range(len(tabTop)):
            self.add_item(TopButton(tabTop[i][0], tabTop[i][1], estCoin, affichageMobile))
