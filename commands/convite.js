const { SlashCommandBuilder } = require("discord.js");

module.exports = {
  data: new SlashCommandBuilder()
    .setName("convite")
    .setDescription("Envia um link com convite para o servidor"),
  async execute(interaction) {
    await interaction.reply("**Tá na mão chefe:**\nhttps://discord.gg/D48QWY6MhK");
  },
};
