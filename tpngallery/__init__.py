from .tpngallery import TPNGallery


def setup(bot):
    bot.add_cog(TPNGallery(bot))
